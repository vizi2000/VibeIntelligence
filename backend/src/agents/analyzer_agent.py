"""
Analyzer Agent
Analyzes code quality, patterns, and provides insights
Following vibecoding principles for constructive feedback
"""

import logging
import ast
import re
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from .base_agent import BaseAgent
from ..models.agent_task import AgentTask, AgentType
from ..models.project import Project
from ..models.developer_activity import DeveloperActivity
from ..models.skill_progress import SkillProgress
from ..ai.orchestrator import TaskType

logger = logging.getLogger(__name__)


class AnalyzerAgent(BaseAgent):
    """
    Agent that analyzes code quality and patterns
    - Code complexity analysis
    - Best practices checking
    - Pattern recognition
    - Skill assessment
    """
    
    def __init__(self):
        super().__init__(AgentType.ANALYZER, "Analyzer Agent")
        self.language_analyzers = {
            ".py": self._analyze_python,
            ".js": self._analyze_javascript,
            ".ts": self._analyze_typescript,
            ".go": self._analyze_go,
            ".rs": self._analyze_rust
        }
    
    async def execute_task(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Execute analyzer task"""
        analysis_type = task.input_data.get("analysis_type", "code_quality")
        
        if analysis_type == "code_quality":
            return await self._analyze_code_quality(task, db)
        elif analysis_type == "complexity":
            return await self._analyze_complexity(task, db)
        elif analysis_type == "patterns":
            return await self._analyze_patterns(task, db)
        elif analysis_type == "skills":
            return await self._analyze_skills(task, db)
        elif analysis_type == "security":
            return await self._analyze_security(task, db)
        else:
            return await self._general_analysis(task, db)
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code analysis needs"""
        file_path = context.get("file_path")
        code_content = context.get("code_content")
        
        analysis = {
            "analysis_needed": False,
            "analysis_types": [],
            "priority": "medium",
            "estimated_time": 5
        }
        
        if file_path or code_content:
            analysis["analysis_needed"] = True
            
            # Determine analysis types based on file
            if file_path:
                ext = Path(file_path).suffix
                if ext in self.language_analyzers:
                    analysis["analysis_types"].extend([
                        "code_quality",
                        "complexity",
                        "patterns"
                    ])
                
                # Security analysis for certain files
                if "auth" in file_path.lower() or "security" in file_path.lower():
                    analysis["analysis_types"].append("security")
                    analysis["priority"] = "high"
        
        return analysis
    
    async def _analyze_code_quality(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Analyze code quality metrics"""
        project_id = task.input_data.get("project_id")
        file_path = task.input_data.get("file_path")
        
        if file_path:
            return await self._analyze_single_file(file_path, task.developer_id)
        elif project_id:
            return await self._analyze_project_quality(project_id, task.developer_id, db)
        else:
            raise ValueError("Either file_path or project_id required")
    
    async def _analyze_single_file(self, file_path: str, developer_id: int) -> Dict[str, Any]:
        """Analyze a single file for quality"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        # Get file extension
        ext = Path(file_path).suffix
        
        # Basic metrics
        metrics = {
            "lines_of_code": len(content.split('\n')),
            "file_size": len(content),
            "language": self._detect_language(ext)
        }
        
        # Language-specific analysis
        if ext in self.language_analyzers:
            lang_metrics = self.language_analyzers[ext](content)
            metrics.update(lang_metrics)
        
        # AI-powered analysis
        prompt = f"""
        Analyze this code for quality and best practices:
        
        File: {file_path}
        Language: {metrics['language']}
        Lines: {metrics['lines_of_code']}
        
        Code:
        ```{metrics['language']}
        {content[:2000]}  # Limit for token usage
        ```
        
        Provide:
        1. Code quality score (0-100)
        2. Best practices violations
        3. Improvement suggestions
        4. Security concerns
        5. Performance issues
        """
        
        ai_response = await self.use_ai(prompt, TaskType.CODE_ANALYSIS)
        ai_analysis = ai_response.get("content", "")
        
        # Log activity
        await self.log_activity(
            developer_id,
            f"Analyzed code quality for {Path(file_path).name}",
            file_path,
            {"lines_analyzed": metrics['lines_of_code']}
        )
        
        return {
            "file_path": file_path,
            "metrics": metrics,
            "ai_analysis": ai_analysis
        }
    
    async def _analyze_project_quality(self, project_id: int, developer_id: int, db: Session) -> Dict[str, Any]:
        """Analyze overall project code quality"""
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        logger.info(f"📊 Analyzing code quality for {project.name}")
        
        total_files = 0
        total_lines = 0
        language_stats = {}
        quality_scores = []
        
        # Analyze all code files
        for root, dirs, files in os.walk(project.path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in [
                'node_modules', '__pycache__', 'venv', 'dist', 'build'
            ]]
            
            for file in files:
                file_path = os.path.join(root, file)
                ext = Path(file_path).suffix
                
                if ext in self.language_analyzers:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        total_files += 1
                        lines = len(content.split('\n'))
                        total_lines += lines
                        
                        # Track language statistics
                        lang = self._detect_language(ext)
                        if lang not in language_stats:
                            language_stats[lang] = {"files": 0, "lines": 0}
                        language_stats[lang]["files"] += 1
                        language_stats[lang]["lines"] += lines
                        
                        # Calculate file quality score
                        file_metrics = self.language_analyzers[ext](content)
                        if "quality_score" in file_metrics:
                            quality_scores.append(file_metrics["quality_score"])
                        
                    except Exception as e:
                        logger.warning(f"Could not analyze {file_path}: {e}")
        
        # Calculate average quality score
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Get AI insights
        prompt = f"""
        Analyze this project's code quality:
        
        Project: {project.name}
        Total Files: {total_files}
        Total Lines: {total_lines}
        Languages: {language_stats}
        Average Quality Score: {avg_quality:.1f}/100
        
        Provide:
        1. Overall assessment
        2. Strengths
        3. Areas for improvement
        4. Recommended refactoring priorities
        5. Technical debt estimation
        """
        
        ai_response = await self.use_ai(prompt, TaskType.CODE_ANALYSIS)
        assessment = ai_response.get("content", "")
        
        return {
            "project_id": project_id,
            "total_files_analyzed": total_files,
            "total_lines_of_code": total_lines,
            "language_breakdown": language_stats,
            "average_quality_score": round(avg_quality, 1),
            "assessment": assessment
        }
    
    async def _analyze_complexity(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Analyze code complexity"""
        file_path = task.input_data.get("file_path")
        
        if not file_path:
            raise ValueError("file_path required for complexity analysis")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        ext = Path(file_path).suffix
        complexity_metrics = {}
        
        # Python complexity analysis
        if ext == ".py":
            complexity_metrics = self._analyze_python_complexity(content)
        
        # AI complexity assessment
        prompt = f"""
        Analyze the complexity of this code:
        
        ```
        {content[:3000]}
        ```
        
        Assess:
        1. Cyclomatic complexity
        2. Cognitive complexity
        3. Nesting depth
        4. Function/method length
        5. Suggestions to reduce complexity
        """
        
        ai_response = await self.use_ai(prompt, TaskType.CODE_ANALYSIS)
        
        return {
            "file_path": file_path,
            "complexity_metrics": complexity_metrics,
            "ai_assessment": ai_response.get("content", "")
        }
    
    async def _analyze_patterns(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Analyze code patterns and practices"""
        project_id = task.input_data.get("project_id")
        
        if not project_id:
            raise ValueError("project_id required for pattern analysis")
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        patterns_found = {
            "design_patterns": [],
            "anti_patterns": [],
            "best_practices": [],
            "code_smells": []
        }
        
        # Sample files for pattern analysis
        sample_files = []
        for root, dirs, files in os.walk(project.path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            for file in files[:10]:  # Limit to 10 files per directory
                if Path(file).suffix in self.language_analyzers:
                    sample_files.append(os.path.join(root, file))
        
        # Analyze patterns with AI
        file_contents = []
        for file_path in sample_files[:5]:  # Limit to 5 files for AI analysis
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_contents.append({
                        "path": os.path.relpath(file_path, project.path),
                        "content": f.read()[:1000]  # First 1000 chars
                    })
            except Exception:
                continue
        
        prompt = f"""
        Analyze these code samples for patterns:
        
        Project: {project.name}
        Files analyzed: {len(file_contents)}
        
        {file_contents}
        
        Identify:
        1. Design patterns used
        2. Anti-patterns present
        3. Coding style consistency
        4. Architecture patterns
        5. Potential refactoring opportunities
        """
        
        ai_response = await self.use_ai(prompt, TaskType.CODE_ANALYSIS)
        
        return {
            "project_id": project_id,
            "files_analyzed": len(sample_files),
            "pattern_analysis": ai_response.get("content", ""),
            "patterns_found": patterns_found
        }
    
    async def _analyze_skills(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Analyze developer skills based on code"""
        developer_id = task.developer_id
        project_id = task.input_data.get("project_id")
        
        # Get recent code from activities
        recent_activities = db.query(DeveloperActivity).filter(
            DeveloperActivity.developer_id == developer_id,
            DeveloperActivity.activity_type == "code",
            DeveloperActivity.code_after.isnot(None)
        ).order_by(DeveloperActivity.created_at.desc()).limit(20).all()
        
        skills_demonstrated = {}
        code_samples = []
        
        for activity in recent_activities:
            if activity.code_after:
                code_samples.append({
                    "code": activity.code_after[:500],
                    "language": activity.details.get("language", "unknown"),
                    "lines_changed": activity.lines_changed
                })
        
        # Analyze skills with AI
        prompt = f"""
        Analyze these code samples to assess developer skills:
        
        Samples: {len(code_samples)}
        
        {code_samples[:5]}  # First 5 samples
        
        Assess:
        1. Technical skill level (beginner/intermediate/advanced)
        2. Languages proficiency
        3. Design pattern knowledge
        4. Code quality consistency
        5. Areas of strength
        6. Areas for improvement
        7. Recommended learning resources
        """
        
        ai_response = await self.use_ai(prompt, TaskType.CODE_ANALYSIS)
        skill_assessment = ai_response.get("content", "")
        
        # Update skill progress
        # Parse AI response to extract skill levels
        # This is simplified - in production, parse the AI response properly
        
        return {
            "developer_id": developer_id,
            "samples_analyzed": len(code_samples),
            "skill_assessment": skill_assessment,
            "recommendations": []
        }
    
    async def _analyze_security(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Analyze code for security issues"""
        file_path = task.input_data.get("file_path")
        
        if not file_path:
            raise ValueError("file_path required for security analysis")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": f"Could not read file: {e}"}
        
        # Common security patterns to check
        security_patterns = {
            "hardcoded_secrets": r'(api_key|password|secret|token)\s*=\s*["\'][^"\']+["\']',
            "sql_injection": r'(query|execute)\s*\([^?]+%[^)]+\)',
            "command_injection": r'(subprocess|os\.system|exec)\s*\([^)]*\+[^)]*\)',
            "unsafe_deserialization": r'(pickle\.loads|yaml\.load)\s*\(',
            "weak_crypto": r'(md5|sha1)\s*\('
        }
        
        vulnerabilities = []
        
        for vuln_type, pattern in security_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                vulnerabilities.append({
                    "type": vuln_type,
                    "occurrences": len(matches),
                    "severity": "high" if vuln_type in ["hardcoded_secrets", "sql_injection"] else "medium"
                })
        
        # AI security analysis
        prompt = f"""
        Perform security analysis on this code:
        
        File: {file_path}
        
        ```
        {content[:3000]}
        ```
        
        Check for:
        1. Security vulnerabilities
        2. Authentication/authorization issues
        3. Data validation problems
        4. Encryption weaknesses
        5. OWASP Top 10 issues
        
        Provide severity levels and remediation suggestions.
        """
        
        ai_response = await self.use_ai(prompt, TaskType.CODE_ANALYSIS)
        
        return {
            "file_path": file_path,
            "vulnerabilities_found": vulnerabilities,
            "ai_security_assessment": ai_response.get("content", "")
        }
    
    async def _general_analysis(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Perform general code analysis"""
        code_snippet = task.input_data.get("code_snippet")
        
        if not code_snippet:
            return {"error": "code_snippet required for general analysis"}
        
        prompt = f"""
        Analyze this code snippet:
        
        ```
        {code_snippet}
        ```
        
        Provide:
        1. What the code does
        2. Quality assessment
        3. Potential issues
        4. Improvement suggestions
        5. Best practices alignment
        """
        
        ai_response = await self.use_ai(prompt, TaskType.CODE_ANALYSIS)
        
        return {
            "analysis": ai_response.get("content", "")
        }
    
    def _detect_language(self, ext: str) -> str:
        """Detect programming language from extension"""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".rb": "ruby",
            ".php": "php"
        }
        return language_map.get(ext, "unknown")
    
    def _analyze_python(self, content: str) -> Dict[str, Any]:
        """Analyze Python code"""
        metrics = {
            "functions": 0,
            "classes": 0,
            "imports": 0,
            "docstrings": 0,
            "type_hints": 0,
            "quality_score": 70  # Base score
        }
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    metrics["functions"] += 1
                    if ast.get_docstring(node):
                        metrics["docstrings"] += 1
                    # Check for type hints
                    if node.returns or any(arg.annotation for arg in node.args.args):
                        metrics["type_hints"] += 1
                elif isinstance(node, ast.ClassDef):
                    metrics["classes"] += 1
                    if ast.get_docstring(node):
                        metrics["docstrings"] += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    metrics["imports"] += 1
            
            # Adjust quality score
            if metrics["functions"] > 0:
                docstring_ratio = metrics["docstrings"] / (metrics["functions"] + metrics["classes"])
                metrics["quality_score"] += int(docstring_ratio * 20)
                
                type_hint_ratio = metrics["type_hints"] / metrics["functions"]
                metrics["quality_score"] += int(type_hint_ratio * 10)
            
        except SyntaxError:
            metrics["syntax_error"] = True
            metrics["quality_score"] = 0
        
        return metrics
    
    def _analyze_python_complexity(self, content: str) -> Dict[str, Any]:
        """Analyze Python code complexity"""
        complexity = {
            "cyclomatic_complexity": 0,
            "max_nesting_depth": 0,
            "avg_function_length": 0
        }
        
        try:
            tree = ast.parse(content)
            
            function_lengths = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Simple cyclomatic complexity
                    for child in ast.walk(node):
                        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                            complexity["cyclomatic_complexity"] += 1
                    
                    # Function length
                    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                        length = node.end_lineno - node.lineno
                        function_lengths.append(length)
            
            if function_lengths:
                complexity["avg_function_length"] = sum(function_lengths) // len(function_lengths)
            
        except Exception:
            pass
        
        return complexity
    
    def _analyze_javascript(self, content: str) -> Dict[str, Any]:
        """Basic JavaScript analysis"""
        return {
            "functions": len(re.findall(r'function\s+\w+|const\s+\w+\s*=\s*\(', content)),
            "classes": len(re.findall(r'class\s+\w+', content)),
            "imports": len(re.findall(r'import\s+.*from', content)),
            "quality_score": 70
        }
    
    def _analyze_typescript(self, content: str) -> Dict[str, Any]:
        """Basic TypeScript analysis"""
        metrics = self._analyze_javascript(content)
        metrics["interfaces"] = len(re.findall(r'interface\s+\w+', content))
        metrics["types"] = len(re.findall(r'type\s+\w+\s*=', content))
        if metrics["interfaces"] > 0 or metrics["types"] > 0:
            metrics["quality_score"] += 10  # Bonus for type usage
        return metrics
    
    def _analyze_go(self, content: str) -> Dict[str, Any]:
        """Basic Go analysis"""
        return {
            "functions": len(re.findall(r'func\s+\w+', content)),
            "structs": len(re.findall(r'type\s+\w+\s+struct', content)),
            "interfaces": len(re.findall(r'type\s+\w+\s+interface', content)),
            "imports": len(re.findall(r'import\s+\(|import\s+"', content)),
            "quality_score": 75  # Go encourages good practices
        }
    
    def _analyze_rust(self, content: str) -> Dict[str, Any]:
        """Basic Rust analysis"""
        return {
            "functions": len(re.findall(r'fn\s+\w+', content)),
            "structs": len(re.findall(r'struct\s+\w+', content)),
            "enums": len(re.findall(r'enum\s+\w+', content)),
            "traits": len(re.findall(r'trait\s+\w+', content)),
            "quality_score": 80  # Rust enforces safety
        }