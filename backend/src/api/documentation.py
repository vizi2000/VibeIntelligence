"""
Documentation generation API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid

from ..core.database import get_db
from ..models.agent_task import AgentTask, AgentType, TaskStatus, TaskPriority
from ..services.agent_manager import agent_manager
from ..models.project import Project

router = APIRouter()

class GenerateDocsRequest(BaseModel):
    project_id: int
    doc_type: str = "readme"  # readme, api, technical, user-guide

class GenerateDocsResponse(BaseModel):
    task_id: str
    status: str
    message: str

@router.post("/generate", response_model=GenerateDocsResponse)
async def generate_documentation(
    request: GenerateDocsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate documentation for a project"""
    
    # Get project
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create documentation task
    try:
        task = await agent_manager.create_task(
            developer_id=1,  # TODO: Get from auth
            agent_type=AgentType.DOCUMENTATION,
            task_name=f"Generate {request.doc_type} for {project.name}",
            description=f"Generate {request.doc_type} documentation for project at {project.path}",
            input_data={
                "project_id": project.id,
                "project_path": project.path,
                "project_name": project.name,
                "doc_type": request.doc_type,
                "tech_stack": project.tech_stack,
                "has_readme": project.has_documentation
            },
            priority=TaskPriority.HIGH
        )
        
        return GenerateDocsResponse(
            task_id=str(task.id),
            status="started",
            message=f"Documentation generation started for {project.name}"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{task_id}")
async def get_documentation_status(task_id: str, db: Session = Depends(get_db)):
    """Get documentation generation status"""
    
    task = db.query(AgentTask).filter(AgentTask.id == int(task_id)).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    result = {
        "task_id": str(task.id),
        "status": task.status,
        "created_at": task.created_at,
        "completed_at": task.completed_at,
        "result": task.output_data
    }
    
    if task.status == TaskStatus.FAILED:
        result["error"] = task.error_message
    
    return result

@router.get("/project/{project_id}")
async def get_project_documentation(project_id: int, db: Session = Depends(get_db)):
    """Get all documentation for a project"""
    
    # Get completed documentation tasks for this project
    from sqlalchemy import cast, String
    from sqlalchemy.dialects.postgresql import JSON
    
    tasks = db.query(AgentTask).filter(
        AgentTask.agent_type == AgentType.DOCUMENTATION.value,
        AgentTask.status == TaskStatus.COMPLETED.value,
        cast(AgentTask.input_data["project_id"], String) == str(project_id)
    ).order_by(AgentTask.completed_at.desc()).limit(10).all()
    
    docs = []
    for task in tasks:
        if task.output_data:
            docs.append({
                "id": str(task.id),
                "type": task.input_data.get("doc_type", "readme"),
                "created_at": task.completed_at,
                "content": task.output_data.get("documentation", ""),
                "file_path": task.output_data.get("file_path", "")
            })
    
    return {"project_id": project_id, "documents": docs}