"""
Documentation Agent
Monitors developer actions and maintains documentation
Following vibecoding principles for transparency
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from .base_agent import BaseAgent
from ..models.agent_task import AgentTask, AgentType
from ..models.developer_activity import DeveloperActivity
from ..models.project import Project
from ..ai.orchestrator import TaskType

logger = logging.getLogger(__name__)


class DocumentationAgent(BaseAgent):
    """
    Agent that monitors developer activities and maintains documentation
    - Tracks code changes and decisions
    - Updates README files automatically
    - Creates ADR (Architecture Decision Records)
    - Generates API documentation
    """
    
    def __init__(self):
        super().__init__(AgentType.DOCUMENTATION, "Documentation Agent")
        self.documentation_templates = {
            "readme": self._get_readme_template(),
            "adr": self._get_adr_template(),
            "api": self._get_api_template()
        }
    
    async def execute_task(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Execute documentation task"""
        task_type = task.input_data.get("doc_type", "readme")
        project_id = task.input_data.get("project_id")
        
        if task_type == "activity_summary":
            return await self._create_activity_summary(task, db)
        elif task_type == "readme_update":
            return await self._update_readme(task, db)
        elif task_type == "adr_creation":
            return await self._create_adr(task, db)
        elif task_type == "api_docs":
            return await self._generate_api_docs(task, db)
        else:
            return await self._auto_document(task, db)
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze documentation needs"""
        project_path = context.get("project_path")
        recent_activities = context.get("recent_activities", [])
        
        analysis = {
            "documentation_health": 0,
            "missing_docs": [],
            "outdated_docs": [],
            "recommendations": []
        }
        
        # Check for README
        if not self._has_readme(project_path):
            analysis["missing_docs"].append("README.md")
            analysis["recommendations"].append("Create README.md with project overview")
        
        # Analyze recent code changes
        significant_changes = self._find_significant_changes(recent_activities)
        if significant_changes:
            analysis["recommendations"].append("Update documentation for recent changes")
        
        # Calculate health score
        analysis["documentation_health"] = self._calculate_doc_health(analysis)
        
        return analysis
    
    async def _create_activity_summary(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Create summary of developer activities"""
        developer_id = task.developer_id
        timeframe = task.input_data.get("timeframe", "daily")
        
        # Get activities based on timeframe
        since = datetime.utcnow()
        if timeframe == "daily":
            since -= timedelta(days=1)
        elif timeframe == "weekly":
            since -= timedelta(weeks=1)
        elif timeframe == "monthly":
            since -= timedelta(days=30)
        
        activities = db.query(DeveloperActivity).filter(
            DeveloperActivity.developer_id == developer_id,
            DeveloperActivity.created_at >= since
        ).order_by(DeveloperActivity.created_at.desc()).all()
        
        # Generate summary using AI
        prompt = f"""
        Create a developer activity summary for the {timeframe} period.
        Activities: {[a.to_dict() for a in activities[:50]]}
        
        Include:
        1. Key accomplishments
        2. Code changes summary
        3. AI interactions
        4. Learning progress
        5. Productivity insights
        
        Format as markdown with sections.
        """
        
        response = await self.use_ai(prompt, TaskType.DOCUMENTATION)
        summary_content = response.get("content", "")
        
        # Save summary
        summary_path = f"/tmp/activity_summary_{developer_id}_{timeframe}.md"
        with open(summary_path, "w") as f:
            f.write(summary_content)
        
        await self.log_activity(
            developer_id,
            f"Generated {timeframe} activity summary",
            summary_path,
            {"activities_count": len(activities)}
        )
        
        return {
            "summary_path": summary_path,
            "activities_analyzed": len(activities),
            "timeframe": timeframe,
            "content_preview": summary_content[:500]
        }
    
    async def _update_readme(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Update project README"""
        project_id = task.input_data.get("project_id")
        project = db.query(Project).filter(Project.id == project_id).first()
        
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Get recent activities for this project
        recent_activities = db.query(DeveloperActivity).filter(
            DeveloperActivity.project_id == project_id
        ).order_by(DeveloperActivity.created_at.desc()).limit(20).all()
        
        # Read current README if exists
        readme_path = f"{project.path}/README.md"
        current_readme = ""
        try:
            with open(readme_path, "r") as f:
                current_readme = f.read()
        except FileNotFoundError:
            current_readme = self.documentation_templates["readme"]
        
        # Generate updated README
        prompt = f"""
        Update this README.md for the project:
        Project: {project.name}
        Tech Stack: {project.tech_stack}
        Recent Activities: {[a.action for a in recent_activities]}
        
        Current README:
        {current_readme}
        
        Improve and update the README while preserving important information.
        Follow best practices for README structure.
        """
        
        response = await self.use_ai(prompt, TaskType.DOCUMENTATION)
        updated_readme = response.get("content", current_readme)
        
        # Write updated README
        with open(readme_path, "w") as f:
            f.write(updated_readme)
        
        await self.log_activity(
            task.developer_id,
            "Updated README.md",
            readme_path,
            {"project_id": project_id, "changes": len(updated_readme) - len(current_readme)}
        )
        
        return {
            "readme_path": readme_path,
            "updated": True,
            "size_change": len(updated_readme) - len(current_readme)
        }
    
    async def _create_adr(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Create Architecture Decision Record"""
        decision_title = task.input_data.get("title")
        context = task.input_data.get("context")
        decision = task.input_data.get("decision")
        consequences = task.input_data.get("consequences", [])
        
        # Generate ADR content
        prompt = f"""
        Create an Architecture Decision Record (ADR) for:
        Title: {decision_title}
        Context: {context}
        Decision: {decision}
        Consequences: {consequences}
        
        Follow the ADR template format with Status, Context, Decision, and Consequences sections.
        """
        
        response = await self.use_ai(prompt, TaskType.DOCUMENTATION)
        adr_content = response.get("content", "")
        
        # Save ADR
        adr_number = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        adr_filename = f"ADR-{adr_number}-{decision_title.lower().replace(' ', '-')}.md"
        adr_path = f"/tmp/{adr_filename}"
        
        with open(adr_path, "w") as f:
            f.write(adr_content)
        
        await self.log_activity(
            task.developer_id,
            f"Created ADR: {decision_title}",
            adr_path,
            {"adr_number": adr_number}
        )
        
        return {
            "adr_path": adr_path,
            "adr_number": adr_number,
            "title": decision_title
        }
    
    async def _generate_api_docs(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Generate API documentation"""
        project_id = task.input_data.get("project_id")
        api_files = task.input_data.get("api_files", [])
        
        # Analyze API endpoints
        prompt = f"""
        Generate comprehensive API documentation for these files:
        {api_files}
        
        Include:
        1. Endpoint descriptions
        2. Request/response schemas
        3. Authentication requirements
        4. Example requests
        5. Error responses
        
        Format as OpenAPI/Swagger compatible documentation.
        """
        
        response = await self.use_ai(prompt, TaskType.DOCUMENTATION)
        api_docs = response.get("content", "")
        
        # Save API documentation
        docs_path = f"/tmp/api_docs_{project_id}.md"
        with open(docs_path, "w") as f:
            f.write(api_docs)
        
        return {
            "docs_path": docs_path,
            "endpoints_documented": len(api_files)
        }
    
    async def _auto_document(self, task: AgentTask, db: Session) -> Dict[str, Any]:
        """Automatically document recent changes"""
        developer_id = task.developer_id
        
        # Get recent undocumented activities
        recent_activities = db.query(DeveloperActivity).filter(
            DeveloperActivity.developer_id == developer_id,
            DeveloperActivity.activity_type.in_(["code", "file_edit"]),
            DeveloperActivity.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).all()
        
        documentation_updates = []
        
        for activity in recent_activities:
            if activity.lines_changed > 50:  # Significant change
                # Generate documentation for this change
                prompt = f"""
                Document this code change:
                Action: {activity.action}
                Target: {activity.target}
                Details: {activity.details}
                
                Create a brief documentation entry explaining what changed and why.
                """
                
                response = await self.use_ai(prompt, TaskType.DOCUMENTATION)
                doc_entry = response.get("content", "")
                
                documentation_updates.append({
                    "activity_id": activity.id,
                    "documentation": doc_entry
                })
        
        return {
            "documented_activities": len(documentation_updates),
            "updates": documentation_updates
        }
    
    def _get_readme_template(self) -> str:
        """Get README template"""
        return """# Project Name

## Overview
Brief description of the project.

## Features
- Feature 1
- Feature 2
- Feature 3

## Installation
```bash
# Installation instructions
```

## Usage
```bash
# Usage examples
```

## Tech Stack
- Technology 1
- Technology 2

## Contributing
Contribution guidelines.

## License
License information.
"""
    
    def _get_adr_template(self) -> str:
        """Get ADR template"""
        return """# Architecture Decision Record: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?
"""
    
    def _get_api_template(self) -> str:
        """Get API documentation template"""
        return """# API Documentation

## Base URL
`https://api.example.com/v1`

## Authentication
Bearer token required in Authorization header.

## Endpoints

### GET /endpoint
Description of endpoint.

**Request:**
```json
{
  "param": "value"
}
```

**Response:**
```json
{
  "data": "response"
}
```
"""
    
    def _has_readme(self, project_path: str) -> bool:
        """Check if project has README"""
        import os
        return os.path.exists(f"{project_path}/README.md")
    
    def _find_significant_changes(self, activities: List[Dict]) -> List[Dict]:
        """Find significant code changes"""
        return [a for a in activities if a.get("lines_changed", 0) > 50]
    
    def _calculate_doc_health(self, analysis: Dict) -> int:
        """Calculate documentation health score"""
        score = 100
        score -= len(analysis["missing_docs"]) * 20
        score -= len(analysis["outdated_docs"]) * 10
        return max(0, score)