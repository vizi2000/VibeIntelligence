"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..core.database import get_db
from ..core.config import settings
import os
import psutil

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Check application health status"""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Get system info
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "version": settings.app_version,
        "database": db_status,
        "system": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "disk_percent": disk.percent
        }
    }

@router.get("/health/detailed")
async def detailed_health_check():
    """Get detailed system information"""
    return {
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug
        },
        "paths": {
            "ai_projects": settings.ai_projects_path,
            "deployment_registry": settings.deployment_registry_path
        },
        "services": {
            "database": bool(settings.database_url),
            "redis": bool(settings.redis_url),
            "openai": bool(settings.openai_api_key),
            "github": bool(settings.github_token)
        }
    }