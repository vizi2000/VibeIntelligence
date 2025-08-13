"""
Agent management API endpoints
Following vibecoding principles for transparency
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from ..core.database import get_db
from ..services.agent_manager import agent_manager
from ..models.agent_task import AgentTask, TaskStatus, TaskPriority, AgentType
from ..models.developer_profile import DeveloperProfile

router = APIRouter()


class CreateTaskRequest(BaseModel):
    agent_type: str
    task_name: str
    description: str
    input_data: Dict[str, Any]
    priority: str = "medium"
    scheduled_at: Optional[datetime] = None
    is_recurring: bool = False
    recurrence_pattern: Optional[Dict[str, Any]] = None


class TaskResponse(BaseModel):
    id: int
    agent_type: str
    task_name: str
    description: str
    status: str
    priority: str
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time_seconds: Optional[float]
    error_message: Optional[str]


class AgentStatusResponse(BaseModel):
    agent_type: str
    name: str
    is_running: bool
    current_task: Optional[str]
    queue_size: int


@router.get("/status", response_model=Dict[str, Any])
async def get_system_status():
    """Get overall agent system status"""
    try:
        stats = await agent_manager.get_system_stats()
        agents_status = agent_manager.get_all_agents_status()
        
        return {
            "system_stats": stats,
            "agents": agents_status,
            "is_running": agent_manager.is_running
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_stats():
    """Get agent system statistics"""
    try:
        stats = await agent_manager.get_system_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents", response_model=List[AgentStatusResponse])
async def list_agents():
    """List all available agents and their status"""
    return agent_manager.get_all_agents_status()


@router.get("/agents/{agent_type}", response_model=AgentStatusResponse)
async def get_agent_status(agent_type: str):
    """Get status of specific agent"""
    try:
        agent_type_enum = AgentType(agent_type)
        status = agent_manager.get_agent_status(agent_type_enum)
        if not status:
            raise HTTPException(status_code=404, detail="Agent not found")
        return status
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid agent type")


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    request: CreateTaskRequest,
    db: Session = Depends(get_db)
):
    """Create a new agent task"""
    try:
        # TODO: Get developer_id from auth context
        developer_id = 1  # Placeholder
        
        agent_type_enum = AgentType(request.agent_type)
        priority_enum = TaskPriority(request.priority)
        
        task = await agent_manager.create_task(
            developer_id=developer_id,
            agent_type=agent_type_enum,
            task_name=request.task_name,
            description=request.description,
            input_data=request.input_data,
            priority=priority_enum,
            scheduled_at=request.scheduled_at,
            is_recurring=request.is_recurring,
            recurrence_pattern=request.recurrence_pattern
        )
        
        return TaskResponse(
            id=task.id,
            agent_type=task.agent_type,
            task_name=task.task_name,
            description=task.description,
            status=task.status,
            priority=task.priority,
            scheduled_at=task.scheduled_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            execution_time_seconds=task.execution_time_seconds,
            error_message=task.error_message
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(
    status: Optional[str] = None,
    agent_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List agent tasks with filtering"""
    query = db.query(AgentTask)
    
    # TODO: Filter by developer_id from auth
    
    if status:
        try:
            status_enum = TaskStatus(status)
            query = query.filter(AgentTask.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
    
    if agent_type:
        try:
            agent_type_enum = AgentType(agent_type)
            query = query.filter(AgentTask.agent_type == agent_type_enum.value)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid agent type")
    
    tasks = query.order_by(AgentTask.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        TaskResponse(
            id=task.id,
            agent_type=task.agent_type,
            task_name=task.task_name,
            description=task.description,
            status=task.status,
            priority=task.priority,
            scheduled_at=task.scheduled_at,
            started_at=task.started_at,
            completed_at=task.completed_at,
            execution_time_seconds=task.execution_time_seconds,
            error_message=task.error_message
        )
        for task in tasks
    ]


@router.get("/tasks/{task_id}", response_model=Dict[str, Any])
async def get_task_details(task_id: int, db: Session = Depends(get_db)):
    """Get detailed task information"""
    task = db.query(AgentTask).filter(AgentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task": task.to_dict(),
        "input_data": task.input_data,
        "output_data": task.output_data,
        "context": task.context
    }


@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: int, db: Session = Depends(get_db)):
    """Cancel a pending or scheduled task"""
    task = db.query(AgentTask).filter(AgentTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.status not in [TaskStatus.PENDING, TaskStatus.SCHEDULED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel task in {task.status} status"
        )
    
    task.status = TaskStatus.CANCELLED
    task.completed_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Task cancelled successfully"}


@router.post("/documentation/summary")
async def create_activity_summary(
    timeframe: str = "daily",
    db: Session = Depends(get_db)
):
    """Create developer activity summary"""
    # TODO: Get developer_id from auth
    developer_id = 1
    
    task = await agent_manager.create_task(
        developer_id=developer_id,
        agent_type=AgentType.DOCUMENTATION,
        task_name=f"Activity Summary - {timeframe}",
        description=f"Generate {timeframe} activity summary",
        input_data={
            "doc_type": "activity_summary",
            "timeframe": timeframe
        },
        priority=TaskPriority.MEDIUM
    )
    
    return {"task_id": task.id, "message": f"Activity summary task created"}


@router.post("/documentation/update-readme")
async def update_project_readme(
    project_id: int,
    db: Session = Depends(get_db)
):
    """Update project README"""
    # TODO: Get developer_id from auth
    developer_id = 1
    
    task = await agent_manager.create_task(
        developer_id=developer_id,
        agent_type=AgentType.DOCUMENTATION,
        task_name=f"Update README - Project {project_id}",
        description="Update project README based on recent changes",
        input_data={
            "doc_type": "readme_update",
            "project_id": project_id
        },
        priority=TaskPriority.HIGH
    )
    
    return {"task_id": task.id, "message": "README update task created"}


@router.post("/scanner/scan-project")
async def scan_project(
    project_id: int,
    scan_type: str = "quick",
    db: Session = Depends(get_db)
):
    """Scan a project for changes and health"""
    developer_id = 1  # TODO: Get from auth
    
    task = await agent_manager.create_task(
        developer_id=developer_id,
        agent_type=AgentType.SCANNER,
        task_name=f"Scan Project {project_id}",
        description=f"Perform {scan_type} scan on project",
        input_data={
            "scan_type": scan_type,
            "project_id": project_id
        },
        priority=TaskPriority.MEDIUM
    )
    
    return {"task_id": task.id, "message": f"Project {scan_type} scan task created"}


@router.post("/analyzer/analyze-code")
async def analyze_code(
    file_path: Optional[str] = None,
    project_id: Optional[int] = None,
    analysis_type: str = "code_quality",
    db: Session = Depends(get_db)
):
    """Analyze code quality and patterns"""
    developer_id = 1  # TODO: Get from auth
    
    task = await agent_manager.create_task(
        developer_id=developer_id,
        agent_type=AgentType.ANALYZER,
        task_name=f"Code Analysis - {analysis_type}",
        description=f"Analyze code for {analysis_type}",
        input_data={
            "analysis_type": analysis_type,
            "file_path": file_path,
            "project_id": project_id
        },
        priority=TaskPriority.MEDIUM
    )
    
    return {"task_id": task.id, "message": f"Code {analysis_type} analysis task created"}


@router.post("/monetization/find-opportunities")
async def find_monetization_opportunities(
    monetization_type: str = "opportunity_scan",
    db: Session = Depends(get_db)
):
    """Find monetization opportunities"""
    developer_id = 1  # TODO: Get from auth
    
    task = await agent_manager.create_task(
        developer_id=developer_id,
        agent_type=AgentType.MONETIZATION,
        task_name="Find Monetization Opportunities",
        description=f"Scan for {monetization_type} opportunities",
        input_data={
            "monetization_type": monetization_type
        },
        priority=TaskPriority.HIGH
    )
    
    return {"task_id": task.id, "message": "Monetization scan task created"}


@router.post("/tasks/suggest")
async def suggest_tasks(
    suggestion_type: str = "daily",
    target_skill: Optional[str] = None,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get AI-powered task suggestions"""
    developer_id = 1  # TODO: Get from auth
    
    task = await agent_manager.create_task(
        developer_id=developer_id,
        agent_type=AgentType.TASK_SUGGESTER,
        task_name=f"Generate {suggestion_type} task suggestions",
        description="AI-powered task suggestions based on patterns",
        input_data={
            "suggestion_type": suggestion_type,
            "target_skill": target_skill,
            "project_id": project_id
        },
        priority=TaskPriority.MEDIUM
    )
    
    return {"task_id": task.id, "message": f"{suggestion_type} task suggestions being generated"}


@router.post("/tasks/break-down")
async def break_down_task(
    task_description: str,
    estimated_hours: float = 4,
    db: Session = Depends(get_db)
):
    """Break down large task into ADHD-friendly subtasks"""
    developer_id = 1  # TODO: Get from auth
    
    task = await agent_manager.create_task(
        developer_id=developer_id,
        agent_type=AgentType.TASK_SUGGESTER,
        task_name="Break Down Task",
        description="Break large task into manageable subtasks",
        input_data={
            "suggestion_type": "break_task",
            "task_description": task_description,
            "estimated_hours": estimated_hours
        },
        priority=TaskPriority.HIGH
    )
    
    return {"task_id": task.id, "message": "Task breakdown being generated"}