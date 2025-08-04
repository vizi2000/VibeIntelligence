"""
Deployment tracking service
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Tuple, Dict
from datetime import datetime
import re
from pathlib import Path
from ..models.deployment import Deployment
from ..core.config import settings

class DeploymentService:
    def __init__(self, db: Session):
        self.db = db
    
    def list_deployments(self, status: Optional[str] = None) -> List[Deployment]:
        """List all deployments"""
        query = self.db.query(Deployment)
        
        if status:
            query = query.filter(Deployment.status == status)
        
        return query.all()
    
    def get_active_ports(self) -> List[int]:
        """Get list of all active ports"""
        deployments = self.db.query(Deployment.port).filter(
            Deployment.is_active == True
        ).all()
        
        return [d[0] for d in deployments]
    
    def check_port_availability(self, port: int) -> Tuple[bool, Optional[str]]:
        """Check if a port is available"""
        deployment = self.db.query(Deployment).filter(
            Deployment.port == port,
            Deployment.is_active == True
        ).first()
        
        if deployment:
            return False, deployment.service_name
        
        return True, None
    
    def register_deployment(
        self,
        port: int,
        service_name: str,
        project_path: str,
        status: str,
        container_id: Optional[str] = None,
        urls: List[str] = None
    ) -> Deployment:
        """Register a new deployment"""
        deployment = Deployment(
            port=port,
            service_name=service_name,
            project_path=project_path,
            status=status,
            container_id=container_id,
            urls=urls or [],
            started_at=datetime.utcnow(),
            is_active=True
        )
        
        self.db.add(deployment)
        self.db.commit()
        self.db.refresh(deployment)
        
        # Also update DEPLOYMENT_REGISTRY.md
        self._update_registry_file(deployment, action="add")
        
        return deployment
    
    def unregister_deployment(self, port: int) -> bool:
        """Unregister a deployment"""
        deployment = self.db.query(Deployment).filter(
            Deployment.port == port,
            Deployment.is_active == True
        ).first()
        
        if deployment:
            deployment.is_active = False
            deployment.stopped_at = datetime.utcnow()
            deployment.status = "stopped"
            self.db.commit()
            
            # Update registry file
            self._update_registry_file(deployment, action="remove")
            
            return True
        
        return False
    
    def sync_with_registry_file(self) -> Dict:
        """Sync database with DEPLOYMENT_REGISTRY.md file"""
        registry_path = Path(settings.deployment_registry_path)
        
        if not registry_path.exists():
            return {"error": "Registry file not found"}
        
        # Read and parse the registry file
        with open(registry_path, 'r') as f:
            content = f.read()
        
        # Parse active deployments from the file
        file_deployments = self._parse_registry_file(content)
        
        # Get database deployments
        db_deployments = self.db.query(Deployment).filter(
            Deployment.is_active == True
        ).all()
        
        # Sync logic
        added = 0
        updated = 0
        removed = 0
        
        # Add/update deployments from file
        for port, deployment_info in file_deployments.items():
            existing = self.db.query(Deployment).filter(
                Deployment.port == port
            ).first()
            
            if existing:
                # Update existing
                existing.service_name = deployment_info['service_name']
                existing.project_path = deployment_info['project_path']
                existing.status = deployment_info['status']
                existing.is_active = True
                updated += 1
            else:
                # Add new
                new_deployment = Deployment(
                    port=port,
                    service_name=deployment_info['service_name'],
                    project_path=deployment_info['project_path'],
                    status=deployment_info['status'],
                    is_active=True
                )
                self.db.add(new_deployment)
                added += 1
        
        # Mark deployments not in file as inactive
        db_ports = [d.port for d in db_deployments]
        for port in db_ports:
            if port not in file_deployments:
                deployment = next(d for d in db_deployments if d.port == port)
                deployment.is_active = False
                deployment.status = "stopped"
                removed += 1
        
        self.db.commit()
        
        return {
            "added": added,
            "updated": updated,
            "removed": removed,
            "total_active": len(file_deployments)
        }
    
    def _parse_registry_file(self, content: str) -> Dict[int, Dict]:
        """Parse DEPLOYMENT_REGISTRY.md content"""
        deployments = {}
        
        # Find the port allocation table
        lines = content.split('\n')
        in_table = False
        
        for line in lines:
            if '| Port' in line and '| Service Name' in line:
                in_table = True
                continue
            
            if in_table and line.strip().startswith('|'):
                # Parse table row
                parts = [p.strip() for p in line.split('|') if p.strip()]
                
                if len(parts) >= 7 and parts[0].isdigit():
                    port = int(parts[0])
                    
                    # Skip reserved ports
                    if parts[1] == '-':
                        continue
                    
                    deployments[port] = {
                        'service_name': parts[1],
                        'project_path': parts[2],
                        'status': 'running' if '🟢' in parts[3] else 'stopped',
                        'container_id': parts[5] if parts[5] != '-' else None
                    }
        
        return deployments
    
    def _update_registry_file(self, deployment: Deployment, action: str):
        """Update DEPLOYMENT_REGISTRY.md file (placeholder)"""
        # In production, this would actually update the file
        # For now, we'll just log the action
        print(f"Would {action} deployment for port {deployment.port} in registry file")