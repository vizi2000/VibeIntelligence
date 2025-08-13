"""
Deployment service for project deployments
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import json
from pathlib import Path
import asyncio

from ..models.project import Project
from ..models.deployment_config import DeploymentConfig, DeploymentStatus
from ..core.config import settings
from fastapi import BackgroundTasks
import logging

logger = logging.getLogger(__name__)

class DeploymentService:
    def __init__(self, db: Session):
        self.db = db
        self.deployment_status = {}  # In-memory status tracking
    
    def start_deployment(
        self,
        project: Project,
        config: DeploymentConfig,
        background_tasks: BackgroundTasks
    ) -> Dict[str, Any]:
        """Start a deployment"""
        
        deployment_id = str(uuid.uuid4())
        
        # Create deployment record
        deployment = {
            "id": deployment_id,
            "project_id": project.id,
            "project_name": project.name,
            "environment": config.environment,
            "deployment_type": config.deployment_type,
            "status": "pending",
            "started_at": datetime.utcnow().isoformat(),
            "config": config.config_data
        }
        
        # Store in memory
        self.deployment_status[deployment_id] = deployment
        
        # Add background task
        background_tasks.add_task(
            self._perform_deployment,
            deployment_id,
            project,
            config
        )
        
        # Generate preview URL (mock for now)
        if config.environment == "staging":
            deployment["preview_url"] = f"https://{project.name.lower()}-{deployment_id[:8]}.zenith-staging.dev"
        
        return deployment
    
    def get_deployment_status(self, deployment_id: str) -> Optional[Dict[str, Any]]:
        """Get deployment status"""
        return self.deployment_status.get(deployment_id)
    
    def get_project_deployments(self, project_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get deployment history for a project"""
        
        # Return recent deployments from memory (mock)
        deployments = []
        for dep_id, dep in self.deployment_status.items():
            if dep["project_id"] == project_id:
                deployments.append(dep)
        
        # Sort by started_at descending
        deployments.sort(key=lambda x: x["started_at"], reverse=True)
        
        return deployments[:limit]
    
    async def _perform_deployment(
        self,
        deployment_id: str,
        project: Project,
        config: DeploymentConfig
    ):
        """Perform the actual deployment"""
        
        logger.info(f"🚀 Starting deployment {deployment_id} for {project.name}")
        
        try:
            # Update status
            self.deployment_status[deployment_id]["status"] = "building"
            self.deployment_status[deployment_id]["message"] = "Building project..."
            
            # Simulate build process
            await asyncio.sleep(5)
            
            # Check project type and deployment type
            if config.deployment_type == "docker":
                await self._deploy_docker(deployment_id, project, config)
            elif config.deployment_type == "vercel":
                await self._deploy_vercel(deployment_id, project, config)
            elif config.deployment_type == "netlify":
                await self._deploy_netlify(deployment_id, project, config)
            else:
                raise ValueError(f"Unsupported deployment type: {config.deployment_type}")
            
            # Update final status
            self.deployment_status[deployment_id]["status"] = "success"
            self.deployment_status[deployment_id]["completed_at"] = datetime.utcnow().isoformat()
            self.deployment_status[deployment_id]["message"] = "Deployment successful!"
            
            logger.info(f"✅ Deployment {deployment_id} completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Deployment {deployment_id} failed: {e}")
            self.deployment_status[deployment_id]["status"] = "failed"
            self.deployment_status[deployment_id]["error"] = str(e)
            self.deployment_status[deployment_id]["message"] = f"Deployment failed: {str(e)}"
    
    async def _deploy_docker(
        self,
        deployment_id: str,
        project: Project,
        config: DeploymentConfig
    ):
        """Deploy using Docker"""
        
        # Check if project has Dockerfile
        project_path = Path(project.path)
        dockerfile = project_path / "Dockerfile"
        
        if not dockerfile.exists():
            # Generate basic Dockerfile
            self.deployment_status[deployment_id]["message"] = "Generating Dockerfile..."
            await asyncio.sleep(2)
            
            # Mock Dockerfile generation
            logger.info(f"Generated Dockerfile for {project.name}")
        
        # Mock Docker build and push
        self.deployment_status[deployment_id]["message"] = "Building Docker image..."
        await asyncio.sleep(3)
        
        self.deployment_status[deployment_id]["message"] = "Pushing to registry..."
        await asyncio.sleep(2)
        
        self.deployment_status[deployment_id]["message"] = "Deploying container..."
        await asyncio.sleep(2)
        
        # Set deployment URL
        self.deployment_status[deployment_id]["deployment_url"] = \
            f"https://{project.name.lower()}.zenith-apps.dev"
    
    async def _deploy_vercel(
        self,
        deployment_id: str,
        project: Project,
        config: DeploymentConfig
    ):
        """Deploy to Vercel"""
        
        self.deployment_status[deployment_id]["message"] = "Preparing Vercel deployment..."
        await asyncio.sleep(2)
        
        # Mock Vercel deployment
        self.deployment_status[deployment_id]["message"] = "Uploading to Vercel..."
        await asyncio.sleep(3)
        
        self.deployment_status[deployment_id]["message"] = "Building on Vercel..."
        await asyncio.sleep(4)
        
        # Set Vercel URL
        self.deployment_status[deployment_id]["deployment_url"] = \
            f"https://{project.name.lower()}-{deployment_id[:8]}.vercel.app"
    
    async def _deploy_netlify(
        self,
        deployment_id: str,
        project: Project,
        config: DeploymentConfig
    ):
        """Deploy to Netlify"""
        
        self.deployment_status[deployment_id]["message"] = "Preparing Netlify deployment..."
        await asyncio.sleep(2)
        
        # Mock Netlify deployment
        self.deployment_status[deployment_id]["message"] = "Uploading to Netlify..."
        await asyncio.sleep(3)
        
        self.deployment_status[deployment_id]["message"] = "Building on Netlify..."
        await asyncio.sleep(4)
        
        # Set Netlify URL
        self.deployment_status[deployment_id]["deployment_url"] = \
            f"https://{project.name.lower()}-{deployment_id[:8]}.netlify.app"