"""
Project Scanner Service
Following Directive 1: Strategic Thinking & System Design
Implements vibecoding principles for joyful project organization
"""

import os
import json
import hashlib
from typing import List, Dict, Any, Optional, Set
from pathlib import Path
import git
from datetime import datetime
import asyncio
import aiofiles
from sqlalchemy.orm import Session

from ..models.project import Project
from ..models.scan import ScanResult, FileInfo
from ..core.config import settings
from ..core.exceptions import ScannerException
from ..services.ai_service import ai_service
import logging

logger = logging.getLogger(__name__)


class ProjectScanner:
    """
    Scans directories for projects with vibecoding joy
    Implements Directive 17: Sustainable scanning with eco-awareness
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.exclude_patterns = settings.scan_exclude_dirs
        self.project_indicators = [
            "package.json", "requirements.txt", "setup.py", "Dockerfile",
            "docker-compose.yml", "pom.xml", "build.gradle", "Cargo.toml",
            "go.mod", "*.csproj", "*.sln", "composer.json", "Gemfile"
        ]
        self.duplicate_cache: Dict[str, List[Path]] = {}
        
    async def scan_directory(self, path: str, deep_scan: bool = True) -> Dict[str, Any]:
        """
        Scan directory for projects with ADHD-friendly progress updates
        Following Directive 5: Clear, efficient UI feedback
        """
        logger.info(f"🔍 Starting vibecoding scan of {path}")
        
        scan_result = {
            "path": path,
            "projects_found": 0,
            "duplicates_found": 0,
            "total_files": 0,
            "scan_time": 0,
            "eco_score": 100,  # Start optimistic!
            "vibe_level": "high",
            "projects": []
        }
        
        start_time = datetime.now()
        
        try:
            # Recursive project discovery
            projects = await self._discover_projects(Path(path))
            
            # Analyze each project
            for project_path in projects:
                project_info = await self._analyze_project(project_path, deep_scan)
                scan_result["projects"].append(project_info)
                
                # Update database
                await self._save_project_to_db(project_info)
                
            # Find duplicates with eco-awareness
            if deep_scan:
                duplicates = await self._find_duplicates(projects)
                scan_result["duplicates_found"] = len(duplicates)
                scan_result["duplicate_groups"] = duplicates
                
            # Calculate metrics
            scan_result["projects_found"] = len(projects)
            scan_result["scan_time"] = (datetime.now() - start_time).total_seconds()
            scan_result["eco_score"] = await self._calculate_eco_score(scan_result)
            scan_result["vibe_level"] = self._assess_vibe_level(scan_result)
            
            logger.info(f"✅ Scan complete! Found {len(projects)} projects with {scan_result['vibe_level']} vibe!")
            
        except Exception as e:
            logger.error(f"❌ Scan failed: {e}")
            raise ScannerException(f"Scan failed: {str(e)}")
            
        return scan_result
        
    async def _discover_projects(self, root_path: Path) -> List[Path]:
        """
        Discover all projects in directory tree
        Implements sustainable scanning (Directive 17)
        """
        projects = []
        
        async def _walk_directory(path: Path):
            try:
                for item in path.iterdir():
                    # Skip excluded directories
                    if item.name in self.exclude_patterns:
                        continue
                        
                    if item.is_dir():
                        # Check if this is a project root
                        if await self._is_project_root(item):
                            projects.append(item)
                            logger.info(f"🎯 Found project: {item.name}")
                        else:
                            # Recurse with async to maintain flow
                            await _walk_directory(item)
                            
            except PermissionError:
                logger.warning(f"⚠️ Permission denied: {path}")
                
        await _walk_directory(root_path)
        return projects
        
    async def _is_project_root(self, path: Path) -> bool:
        """Check if directory is a project root"""
        for indicator in self.project_indicators:
            if indicator.startswith("*"):
                # Handle wildcard patterns
                if list(path.glob(indicator)):
                    return True
            else:
                if (path / indicator).exists():
                    return True
        return False
        
    async def _analyze_project(self, project_path: Path, deep_scan: bool) -> Dict[str, Any]:
        """
        Analyze project with AI-powered insights
        Following Directive 8: Multi-model AI integration
        """
        logger.info(f"🔬 Analyzing project: {project_path.name}")
        
        project_info = {
            "name": project_path.name,
            "path": str(project_path),
            "type": await self._detect_project_type(project_path),
            "languages": await self._detect_languages(project_path),
            "health_score": 100,  # Start with perfect health!
            "has_readme": (project_path / "README.md").exists(),
            "has_tests": await self._has_tests(project_path),
            "has_ci": await self._has_ci(project_path),
            "last_modified": datetime.fromtimestamp(project_path.stat().st_mtime),
            "size_mb": await self._calculate_size(project_path),
            "file_count": 0,
            "duplicate_risk": "low",
            "documentation_score": 0,
            "vibe_score": 10,  # Maximum vibe!
            "eco_impact": "low"
        }
        
        # Git analysis
        if (project_path / ".git").exists():
            project_info.update(await self._analyze_git_repo(project_path))
            
        # Calculate health score
        project_info["health_score"] = self._calculate_health_score(project_info)
        
        # AI-powered insights if deep scan
        if deep_scan and ai_service.is_initialized:
            insights = await self._get_ai_insights(project_info)
            project_info["ai_insights"] = insights
            
        return project_info
        
    async def _detect_project_type(self, path: Path) -> str:
        """Detect project type from files"""
        if (path / "package.json").exists():
            return "Node.js"
        elif (path / "requirements.txt").exists() or (path / "setup.py").exists():
            return "Python"
        elif (path / "pom.xml").exists():
            return "Java"
        elif (path / "Cargo.toml").exists():
            return "Rust"
        elif (path / "go.mod").exists():
            return "Go"
        elif list(path.glob("*.csproj")):
            return "C#/.NET"
        elif (path / "composer.json").exists():
            return "PHP"
        elif (path / "Gemfile").exists():
            return "Ruby"
        else:
            return "Unknown"
            
    async def _detect_languages(self, path: Path) -> List[str]:
        """Detect programming languages used"""
        languages = set()
        extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".java": "Java",
            ".cs": "C#",
            ".go": "Go",
            ".rs": "Rust",
            ".php": "PHP",
            ".rb": "Ruby",
            ".cpp": "C++",
            ".c": "C",
            ".swift": "Swift",
            ".kt": "Kotlin"
        }
        
        for ext, lang in extensions.items():
            if list(path.rglob(f"*{ext}")):
                languages.add(lang)
                
        return list(languages)
        
    async def _has_tests(self, path: Path) -> bool:
        """Check if project has tests"""
        test_indicators = ["test", "tests", "spec", "specs", "__tests__"]
        for indicator in test_indicators:
            if (path / indicator).exists():
                return True
        return False
        
    async def _has_ci(self, path: Path) -> bool:
        """Check for CI/CD configuration"""
        ci_files = [
            ".github/workflows", ".gitlab-ci.yml", ".travis.yml",
            "Jenkinsfile", ".circleci", "azure-pipelines.yml"
        ]
        for ci_file in ci_files:
            if (path / ci_file).exists():
                return True
        return False
        
    async def _calculate_size(self, path: Path) -> float:
        """Calculate project size in MB"""
        total_size = 0
        for item in path.rglob("*"):
            if item.is_file() and not any(excl in str(item) for excl in self.exclude_patterns):
                total_size += item.stat().st_size
        return round(total_size / (1024 * 1024), 2)
        
    async def _analyze_git_repo(self, path: Path) -> Dict[str, Any]:
        """Analyze git repository"""
        try:
            repo = git.Repo(path)
            return {
                "is_git_repo": True,
                "current_branch": repo.active_branch.name,
                "commit_count": len(list(repo.iter_commits())),
                "has_uncommitted": repo.is_dirty(),
                "last_commit": repo.head.commit.committed_datetime,
                "remote_url": repo.remotes.origin.url if repo.remotes else None
            }
        except Exception as e:
            logger.warning(f"Git analysis failed: {e}")
            return {"is_git_repo": True, "git_error": str(e)}
            
    def _calculate_health_score(self, project_info: Dict[str, Any]) -> int:
        """
        Calculate project health score (0-100)
        Following Directive 19: Well-being for projects too!
        """
        score = 100
        
        # Deduct points for missing essentials
        if not project_info["has_readme"]:
            score -= 20
        if not project_info["has_tests"]:
            score -= 15
        if not project_info["has_ci"]:
            score -= 10
            
        # Git health
        if project_info.get("has_uncommitted"):
            score -= 5
            
        # Size penalty for large projects
        if project_info["size_mb"] > 500:
            score -= 10
        elif project_info["size_mb"] > 1000:
            score -= 20
            
        # Boost for good practices
        if project_info.get("commit_count", 0) > 50:
            score += 5
            
        return max(0, min(100, score))
        
    async def _find_duplicates(self, projects: List[Path]) -> Dict[str, List[str]]:
        """
        Find duplicate projects using smart hashing
        Implements eco-friendly deduplication (Directive 17)
        """
        logger.info("🔍 Searching for duplicates to save space...")
        
        duplicates = {}
        file_hashes = {}
        
        for project in projects:
            # Create project fingerprint
            fingerprint = await self._create_project_fingerprint(project)
            
            if fingerprint in file_hashes:
                if fingerprint not in duplicates:
                    duplicates[fingerprint] = [str(file_hashes[fingerprint])]
                duplicates[fingerprint].append(str(project))
            else:
                file_hashes[fingerprint] = project
                
        # Only return actual duplicates
        return {k: v for k, v in duplicates.items() if len(v) > 1}
        
    async def _create_project_fingerprint(self, path: Path) -> str:
        """Create unique fingerprint for project"""
        hasher = hashlib.md5()
        
        # Hash key files that define project identity
        key_files = ["package.json", "requirements.txt", "README.md", ".gitignore"]
        
        for key_file in key_files:
            file_path = path / key_file
            if file_path.exists():
                async with aiofiles.open(file_path, 'rb') as f:
                    content = await f.read()
                    hasher.update(content)
                    
        return hasher.hexdigest()
        
    async def _calculate_eco_score(self, scan_result: Dict[str, Any]) -> int:
        """
        Calculate eco-score based on scan efficiency
        Following Directive 17: Sustainable practices
        """
        score = 100
        
        # Penalize for duplicates (waste of space)
        if scan_result["duplicates_found"] > 0:
            score -= min(30, scan_result["duplicates_found"] * 5)
            
        # Reward for efficient scan time
        if scan_result["scan_time"] < 5:
            score += 10
        elif scan_result["scan_time"] > 30:
            score -= 10
            
        # Bonus for finding well-organized projects
        healthy_projects = sum(1 for p in scan_result["projects"] if p["health_score"] > 80)
        if healthy_projects > len(scan_result["projects"]) * 0.7:
            score += 15
            
        return max(0, min(100, score))
        
    def _assess_vibe_level(self, scan_result: Dict[str, Any]) -> str:
        """
        Assess overall vibe level of the scan
        Following Directive 19: Holistic well-being
        """
        if scan_result["eco_score"] > 90 and scan_result["duplicates_found"] == 0:
            return "peak_flow"
        elif scan_result["eco_score"] > 70:
            return "high"
        elif scan_result["eco_score"] > 50:
            return "medium"
        else:
            return "needs_love"
            
    async def _get_ai_insights(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI-powered insights about the project
        Following Directive 8: AI integration
        """
        try:
            prompt = f"""
            Analyze this project and provide actionable insights:
            - Name: {project_info['name']}
            - Type: {project_info['type']}
            - Languages: {', '.join(project_info['languages'])}
            - Health Score: {project_info['health_score']}
            - Has README: {project_info['has_readme']}
            - Has Tests: {project_info['has_tests']}
            
            Provide:
            1. Main improvement suggestions (max 3)
            2. Monetization potential (score 1-10)
            3. Quick win tasks for ADHD-friendly progress
            """
            
            response = await ai_service.generate(
                prompt=prompt,
                task_type="analysis",
                max_tokens=300
            )
            
            return {
                "suggestions": response.get("content", ""),
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.warning(f"AI insights generation failed: {e}")
            return {"error": "AI insights unavailable"}
            
    async def _save_project_to_db(self, project_info: Dict[str, Any]) -> None:
        """Save or update project in database"""
        try:
            # Check if project exists
            existing = self.db.query(Project).filter(
                Project.path == project_info["path"]
            ).first()
            
            if existing:
                # Update existing project
                for key, value in project_info.items():
                    if hasattr(existing, key) and key != "id":
                        setattr(existing, key, value)
                existing.last_scan = datetime.now()
            else:
                # Create new project
                project = Project(**{
                    k: v for k, v in project_info.items() 
                    if k in Project.__table__.columns
                })
                self.db.add(project)
                
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to save project to DB: {e}")
            self.db.rollback()


# Scanner instance factory
def get_scanner(db: Session) -> ProjectScanner:
    """Get scanner instance with database session"""
    return ProjectScanner(db)