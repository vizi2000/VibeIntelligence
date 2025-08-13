"""
Scanner Agent
Continuously monitors projects for changes and updates
Following vibecoding principles for proactive assistance
"""

import logging
import os
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session

from .base_agent import BaseAgent
from ..models.agent_task import AgentTask, AgentType
from ..models.project import Project
from ..models.developer_activity import DeveloperActivity
from ..services.project_scanner import ProjectScanner
from ..ai.orchestrator import TaskType

logger = logging.getLogger(__name__)


class ScannerAgent(BaseAgent):
    """
    Agent that continuously scans projects for changes
    - Monitors file changes and updates
    - Detects new dependencies
    - Identifies potential issues
    - Tracks project health metrics
    """
    
    def __init__(self):
        super().__init__(AgentType.SCANNER, "Scanner Agent")
        self.scanner: Optional[ProjectScanner] = None  # Will be initialized per task with db
        self.file_hashes: Dict[str, str] = {}  # Path -> hash
        self.last_scan_times: Dict[int, datetime] = {}  # Project ID -> last scan
    
    async def execute_task(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Execute scanner task"""
        # Initialize scanner with db if not already done
        if self.scanner is None:
            self.scanner = ProjectScanner(db)
            
        task_type = task.input_data.get("scan_type", "quick")
        project_id = task.input_data.get("project_id")
        
        if task_type == "full_scan":
            return await self._full_project_scan(task, db)
        elif task_type == "quick_scan":
            return await self._quick_scan(task, db)
        elif task_type == "dependency_check":
            return await self._check_dependencies(task, db)
        elif task_type == "health_check":
            return await self._health_check(task, db)
        else:
            return await self._monitor_changes(task, db)
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze project scanning needs"""
        project_path = context.get("project_path")
        last_scan = context.get("last_scan")
        
        analysis = {
            "scan_needed": False,
            "scan_type": "quick",
            "reasons": [],
            "priority": "medium"
        }
        
        # Check if scan is overdue
        if last_scan:
            time_since_scan = datetime.utcnow() - last_scan
            if time_since_scan > timedelta(days=7):
                analysis["scan_needed"] = True
                analysis["scan_type"] = "full"
                analysis["reasons"].append("No scan in over 7 days")
                analysis["priority"] = "high"
            elif time_since_scan > timedelta(days=1):
                analysis["scan_needed"] = True
                analysis["reasons"].append("Daily scan due")
        else:
            analysis["scan_needed"] = True
            analysis["scan_type"] = "full"
            analysis["reasons"].append("Never scanned before")
            analysis["priority"] = "high"
        
        # Check for recent changes
        if self._has_recent_changes(project_path):
            analysis["scan_needed"] = True
            analysis["reasons"].append("Recent file changes detected")
        
        return analysis
    
    async def _full_project_scan(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Perform comprehensive project scan"""
        project_id = task.input_data.get("project_id")
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        logger.info(f"🔍 Starting full scan of {project.name}")
        
        # Use the project scanner service
        scan_result = await self.scanner.scan_directory(project.path, deep_scan=True)
        
        # Update project information
        project.size_mb = scan_result.get("size_mb", 0)
        project.tech_stack = scan_result.get("languages", [])
        project.has_documentation = scan_result.get("has_readme", False)
        project.has_tests = scan_result.get("has_tests", False)
        project.is_git_repo = scan_result.get("is_git_repo", False)
        project.last_modified = datetime.utcnow()
        
        # Store file hashes for change detection
        for file_info in scan_result.get("files", []):
            file_path = file_info["path"]
            self.file_hashes[file_path] = self._calculate_file_hash(file_path)
        
        # Analyze with AI for insights
        prompt = f"""
        Analyze this project scan result and provide insights:
        Project: {project.name}
        Path: {project.path}
        Languages: {scan_result.get('languages')}
        File Count: {scan_result.get('file_count')}
        Has Tests: {scan_result.get('has_tests')}
        Has README: {scan_result.get('has_readme')}
        
        Provide:
        1. Project health assessment
        2. Missing components
        3. Improvement suggestions
        4. Potential issues
        """
        
        ai_response = await self.use_ai(prompt, TaskType.CODE_ANALYSIS)
        insights = ai_response.get("content", "")
        
        # Log activity
        await self.log_activity(
            task.developer_id,
            f"Completed full scan of {project.name}",
            project.path,
            {
                "files_scanned": scan_result.get("file_count", 0),
                "size_mb": scan_result.get("size_mb", 0),
                "languages": scan_result.get("languages", [])
            }
        )
        
        # Update last scan time
        self.last_scan_times[project_id] = datetime.utcnow()
        
        db.commit()
        
        return {
            "project_id": project_id,
            "scan_type": "full",
            "files_scanned": scan_result.get("file_count", 0),
            "size_mb": scan_result.get("size_mb", 0),
            "languages": scan_result.get("languages", []),
            "has_tests": scan_result.get("has_tests", False),
            "has_documentation": scan_result.get("has_readme", False),
            "insights": insights,
            "issues_found": scan_result.get("issues", [])
        }
    
    async def _quick_scan(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Perform quick scan for recent changes"""
        project_id = task.input_data.get("project_id")
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        logger.info(f"⚡ Quick scan of {project.name}")
        
        changed_files = []
        new_files = []
        deleted_files = []
        
        # Check for file changes
        for root, dirs, files in os.walk(project.path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.scanner.exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project.path)
                
                # Check if file is new or changed
                current_hash = self._calculate_file_hash(file_path)
                
                if file_path not in self.file_hashes:
                    new_files.append(relative_path)
                    self.file_hashes[file_path] = current_hash
                elif self.file_hashes[file_path] != current_hash:
                    changed_files.append(relative_path)
                    self.file_hashes[file_path] = current_hash
        
        # Check for deleted files
        existing_paths = set()
        for root, dirs, files in os.walk(project.path):
            dirs[:] = [d for d in dirs if d not in self.scanner.exclude_dirs]
            for file in files:
                existing_paths.add(os.path.join(root, file))
        
        for stored_path in list(self.file_hashes.keys()):
            if stored_path.startswith(project.path) and stored_path not in existing_paths:
                deleted_files.append(os.path.relpath(stored_path, project.path))
                del self.file_hashes[stored_path]
        
        # Log changes
        total_changes = len(changed_files) + len(new_files) + len(deleted_files)
        
        if total_changes > 0:
            await self.log_activity(
                task.developer_id,
                f"Quick scan found {total_changes} changes in {project.name}",
                project.path,
                {
                    "changed_files": len(changed_files),
                    "new_files": len(new_files),
                    "deleted_files": len(deleted_files)
                }
            )
        
        return {
            "project_id": project_id,
            "scan_type": "quick",
            "changed_files": changed_files[:20],  # Limit to 20 for response size
            "new_files": new_files[:20],
            "deleted_files": deleted_files[:20],
            "total_changes": total_changes
        }
    
    async def _check_dependencies(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Check project dependencies for updates and security issues"""
        project_id = task.input_data.get("project_id")
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        logger.info(f"📦 Checking dependencies for {project.name}")
        
        dependency_files = {
            "Python": ["requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
            "JavaScript": ["package.json"],
            "Go": ["go.mod"],
            "Rust": ["Cargo.toml"],
            "Ruby": ["Gemfile"],
            "PHP": ["composer.json"]
        }
        
        found_dependencies = {}
        
        # Find dependency files
        for language, files in dependency_files.items():
            for dep_file in files:
                file_path = os.path.join(project.path, dep_file)
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        content = f.read()
                    found_dependencies[dep_file] = content
        
        if not found_dependencies:
            return {
                "project_id": project_id,
                "dependencies_found": False,
                "message": "No dependency files found"
            }
        
        # Analyze dependencies with AI
        prompt = f"""
        Analyze these dependency files for project {project.name}:
        
        {found_dependencies}
        
        Check for:
        1. Outdated packages
        2. Security vulnerabilities (based on known issues)
        3. Unused dependencies
        4. Missing dev dependencies
        5. Version conflicts
        
        Provide specific recommendations.
        """
        
        ai_response = await self.use_ai(prompt, TaskType.CODE_ANALYSIS)
        analysis = ai_response.get("content", "")
        
        return {
            "project_id": project_id,
            "dependencies_found": True,
            "dependency_files": list(found_dependencies.keys()),
            "analysis": analysis
        }
    
    async def _health_check(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Perform project health check"""
        project_id = task.input_data.get("project_id")
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        logger.info(f"🏥 Health check for {project.name}")
        
        health_metrics = {
            "has_readme": False,
            "has_tests": False,
            "has_ci": False,
            "has_license": False,
            "has_gitignore": False,
            "test_coverage": 0,
            "code_quality": 0,
            "documentation_quality": 0
        }
        
        # Check for essential files
        essential_files = {
            "has_readme": ["README.md", "README.rst", "README.txt"],
            "has_license": ["LICENSE", "LICENSE.md", "LICENSE.txt"],
            "has_gitignore": [".gitignore"],
            "has_ci": [".github/workflows", ".gitlab-ci.yml", ".travis.yml", "Jenkinsfile"]
        }
        
        for metric, files in essential_files.items():
            for file in files:
                if os.path.exists(os.path.join(project.path, file)):
                    health_metrics[metric] = True
                    break
        
        # Check for test directories
        test_dirs = ["tests", "test", "__tests__", "spec"]
        for test_dir in test_dirs:
            if os.path.exists(os.path.join(project.path, test_dir)):
                health_metrics["has_tests"] = True
                break
        
        # Calculate health score
        health_score = sum([
            health_metrics["has_readme"] * 20,
            health_metrics["has_tests"] * 20,
            health_metrics["has_ci"] * 15,
            health_metrics["has_license"] * 10,
            health_metrics["has_gitignore"] * 10,
            25  # Base score for existing
        ])
        
        # Get AI recommendations
        prompt = f"""
        Based on this project health check for {project.name}:
        {health_metrics}
        
        Overall health score: {health_score}/100
        
        Provide:
        1. Health assessment
        2. Critical missing components
        3. Improvement priorities
        4. Quick wins for better health
        """
        
        ai_response = await self.use_ai(prompt, TaskType.CODE_ANALYSIS)
        recommendations = ai_response.get("content", "")
        
        return {
            "project_id": project_id,
            "health_score": health_score,
            "metrics": health_metrics,
            "recommendations": recommendations
        }
    
    async def _monitor_changes(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Monitor for real-time changes"""
        project_id = task.input_data.get("project_id")
        duration_minutes = task.input_data.get("duration_minutes", 5)
        
        # This would ideally use file system watchers
        # For now, we'll do periodic checks
        
        return {
            "project_id": project_id,
            "monitoring_duration": duration_minutes,
            "status": "monitoring_started"
        }
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate hash of file contents"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception:
            return ""
    
    def _has_recent_changes(self, project_path: str) -> bool:
        """Check if project has recent changes"""
        try:
            # Check modification time of project directory
            path = Path(project_path)
            if path.exists():
                mtime = datetime.fromtimestamp(path.stat().st_mtime)
                return (datetime.utcnow() - mtime) < timedelta(hours=24)
        except Exception:
            pass
        return False