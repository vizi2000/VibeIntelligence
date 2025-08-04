"""
Project management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..models.project import Project
from ..services.project_service import ProjectService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ProjectResponse(BaseModel):
    id: int
    name: str
    path: str
    project_type: str
    tech_stack: List[str]
    has_documentation: bool
    has_docker: bool
    is_git_repo: bool
    size_mb: float
    last_modified: datetime
    is_active: bool
    potential_duplicates: List[str]

class ProjectCreate(BaseModel):
    name: str
    path: str
    project_type: str
    tech_stack: List[str]

@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    project_type: Optional[str] = None,
    has_documentation: Optional[bool] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List all projects with optional filtering"""
    service = ProjectService(db)
    projects = service.list_projects(
        skip=skip,
        limit=limit,
        project_type=project_type,
        has_documentation=has_documentation,
        is_active=is_active
    )
    return projects

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project by ID"""
    service = ProjectService(db)
    project = service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/duplicates", response_model=List[List[ProjectResponse]])
async def get_duplicate_groups(db: Session = Depends(get_db)):
    """Get all groups of duplicate projects"""
    service = ProjectService(db)
    return service.get_duplicate_groups()

@router.put("/{project_id}/activate")
async def activate_project(project_id: int, db: Session = Depends(get_db)):
    """Mark a project as active"""
    service = ProjectService(db)
    project = service.activate_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project activated", "project_id": project_id}

@router.put("/{project_id}/archive")
async def archive_project(project_id: int, db: Session = Depends(get_db)):
    """Archive a project"""
    service = ProjectService(db)
    project = service.archive_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project archived", "project_id": project_id}

@router.get("/stats/summary")
async def get_project_statistics(db: Session = Depends(get_db)):
    """Get summary statistics about all projects"""
    service = ProjectService(db)
    return service.get_statistics()