"""
Deployment tracking endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..core.database import get_db
from ..services.deployment_service import DeploymentService
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class DeploymentResponse(BaseModel):
    port: int
    service_name: str
    project_path: str
    status: str
    container_id: Optional[str]
    started_at: Optional[datetime]
    urls: List[str]

class PortCheckRequest(BaseModel):
    port: int

class DeploymentUpdate(BaseModel):
    service_name: str
    project_path: str
    status: str
    container_id: Optional[str]
    urls: List[str]

@router.get("/", response_model=List[DeploymentResponse])
async def list_deployments(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all deployments from the registry"""
    service = DeploymentService(db)
    return service.list_deployments(status=status)

@router.get("/active-ports")
async def get_active_ports(db: Session = Depends(get_db)):
    """Get list of all ports currently in use"""
    service = DeploymentService(db)
    return {"active_ports": service.get_active_ports()}

@router.post("/check-port")
async def check_port_availability(
    request: PortCheckRequest,
    db: Session = Depends(get_db)
):
    """Check if a specific port is available"""
    service = DeploymentService(db)
    is_available, current_service = service.check_port_availability(request.port)
    
    return {
        "port": request.port,
        "available": is_available,
        "current_service": current_service
    }

@router.post("/register/{port}")
async def register_deployment(
    port: int,
    deployment: DeploymentUpdate,
    db: Session = Depends(get_db)
):
    """Register a new deployment in the registry"""
    service = DeploymentService(db)
    
    # Check if port is available
    is_available, current_service = service.check_port_availability(port)
    if not is_available:
        raise HTTPException(
            status_code=409,
            detail=f"Port {port} is already in use by {current_service}"
        )
    
    # Register the deployment
    service.register_deployment(
        port=port,
        service_name=deployment.service_name,
        project_path=deployment.project_path,
        status=deployment.status,
        container_id=deployment.container_id,
        urls=deployment.urls
    )
    
    return {"message": "Deployment registered successfully", "port": port}

@router.delete("/{port}")
async def unregister_deployment(port: int, db: Session = Depends(get_db)):
    """Unregister a deployment from the registry"""
    service = DeploymentService(db)
    success = service.unregister_deployment(port)
    
    if not success:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    return {"message": "Deployment unregistered successfully", "port": port}

@router.post("/sync-registry")
async def sync_with_registry_file(db: Session = Depends(get_db)):
    """Sync deployments with DEPLOYMENT_REGISTRY.md file"""
    service = DeploymentService(db)
    result = service.sync_with_registry_file()
    return result