"""
Deployment API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel
from datetime import datetime

from ..core.database import get_db
from ..models.project import Project
from ..models.deployment_config import DeploymentConfig, DeploymentStatus
from ..services.deployment_service import DeploymentService

router = APIRouter()

class DeployRequest(BaseModel):
    project_id: int
    environment: str = "staging"  # staging, production
    deployment_type: str = "docker"  # docker, kubernetes, vercel, netlify

class DeployResponse(BaseModel):
    deployment_id: str
    status: str
    message: str
    deployment_url: str = None

@router.post("/deploy", response_model=DeployResponse)
async def deploy_project(
    request: DeployRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Deploy a project"""
    
    # Get project
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get or create deployment config
    config = db.query(DeploymentConfig).filter(
        DeploymentConfig.project_id == request.project_id,
        DeploymentConfig.environment == request.environment
    ).first()
    
    if not config:
        # Create basic config
        config = DeploymentConfig(
            project_id=request.project_id,
            environment=request.environment,
            deployment_type=request.deployment_type,
            config_data={
                "auto_deploy": False,
                "branch": "main",
                "port": 3000
            }
        )
        db.add(config)
        db.commit()
    
    # Start deployment
    service = DeploymentService(db)
    try:
        deployment = service.start_deployment(
            project=project,
            config=config,
            background_tasks=background_tasks
        )
        
        return DeployResponse(
            deployment_id=deployment["id"],
            status="started",
            message=f"Deployment started for {project.name} to {request.environment}",
            deployment_url=deployment.get("preview_url")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{deployment_id}")
async def get_deployment_status(deployment_id: str, db: Session = Depends(get_db)):
    """Get deployment status"""
    
    service = DeploymentService(db)
    status = service.get_deployment_status(deployment_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return status

@router.get("/project/{project_id}/deployments")
async def get_project_deployments(
    project_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get deployment history for a project"""
    
    service = DeploymentService(db)
    deployments = service.get_project_deployments(project_id, limit)
    
    return {"project_id": project_id, "deployments": deployments}

@router.get("/environments")
async def get_available_environments():
    """Get available deployment environments"""
    
    return {
        "environments": [
            {
                "name": "staging",
                "description": "Test environment for development",
                "auto_ssl": True
            },
            {
                "name": "production",
                "description": "Live production environment",
                "auto_ssl": True,
                "requires_approval": True
            }
        ]
    }

@router.get("/types")
async def get_deployment_types():
    """Get available deployment types"""
    
    return {
        "types": [
            {
                "id": "docker",
                "name": "Docker Container",
                "description": "Deploy as Docker container",
                "supported": True
            },
            {
                "id": "kubernetes",
                "name": "Kubernetes",
                "description": "Deploy to Kubernetes cluster",
                "supported": False,
                "coming_soon": True
            },
            {
                "id": "vercel",
                "name": "Vercel",
                "description": "Deploy to Vercel platform",
                "supported": True
            },
            {
                "id": "netlify",
                "name": "Netlify",
                "description": "Deploy to Netlify platform",
                "supported": True
            }
        ]
    }