"""
Project scanner service
Following Directive 6: Clear documentation and planning
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import uuid
import json
from pathlib import Path
import asyncio
import logging
from datetime import datetime

from ..models.project import Project
from ..models.scan import ScanHistory, ScanResult
from ..core.config import settings
from fastapi import BackgroundTasks
from .project_scanner import ProjectScanner

logger = logging.getLogger(__name__)

class ScannerService:
    def __init__(self, db: Session):
        self.db = db
        self.scan_status = {}  # In-memory status tracking
    
    def _serialize_datetime(self, obj):
        """JSON serializer for objects not serializable by default json code"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._serialize_datetime(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetime(item) for item in obj]
        return obj
    
    def start_scan(
        self,
        path: Optional[str] = None,
        full_scan: bool = False,
        background_tasks: BackgroundTasks = None
    ) -> str:
        """Start a project scan"""
        scan_id = str(uuid.uuid4())
        scan_path = path or settings.ai_projects_path
        
        # Create scan history entry
        scan_history = ScanHistory(
            scan_id=scan_id,
            scan_type="full" if full_scan else "incremental",
            status="running",
            base_path=scan_path
        )
        self.db.add(scan_history)
        self.db.commit()
        
        # Update in-memory status
        self.scan_status[scan_id] = {
            "status": "running",
            "progress": 0,
            "message": "Scan started"
        }
        
        # If background tasks provided, run scan asynchronously
        if background_tasks:
            background_tasks.add_task(self._perform_scan, scan_id, scan_path, full_scan)
        
        return scan_id
    
    def get_scan_status(self, scan_id: str) -> Optional[Dict]:
        """Get the status of a scan"""
        # Check in-memory status first
        if scan_id in self.scan_status:
            return self.scan_status[scan_id]
        
        # Check database
        scan = self.db.query(ScanHistory).filter(
            ScanHistory.scan_id == scan_id
        ).first()
        
        if scan:
            return {
                "status": scan.status,
                "started_at": scan.started_at.isoformat() if scan.started_at else None,
                "completed_at": scan.completed_at.isoformat() if scan.completed_at else None,
                "projects_found": scan.projects_found,
                "message": scan.error_message if scan.status == "failed" else "Scan completed"
            }
        
        return None
    
    def get_last_scan_info(self) -> Optional[Dict]:
        """Get information about the last scan"""
        last_scan = self.db.query(ScanHistory).order_by(
            ScanHistory.started_at.desc()
        ).first()
        
        if last_scan:
            return {
                "scan_id": last_scan.scan_id,
                "scan_type": last_scan.scan_type,
                "status": last_scan.status,
                "started_at": last_scan.started_at.isoformat() if last_scan.started_at else None,
                "completed_at": last_scan.completed_at.isoformat() if last_scan.completed_at else None,
                "duration_seconds": last_scan.duration_seconds,
                "projects_found": last_scan.projects_found,
                "new_projects": last_scan.new_projects,
                "duplicates_found": last_scan.duplicates_found
            }
        
        return None
    
    def analyze_duplicates(self) -> Dict:
        """Analyze projects for duplicates"""
        # Get all projects
        projects = self.db.query(Project).all()
        
        # Group by normalized name
        name_groups = {}
        for project in projects:
            # Normalize name for comparison
            normalized = project.name.lower().replace('-', '').replace('_', '').replace(' ', '')
            # Remove version numbers
            normalized = ''.join([c for c in normalized if not c.isdigit()])
            
            if normalized not in name_groups:
                name_groups[normalized] = []
            name_groups[normalized].append(project)
        
        # Find duplicate groups
        duplicate_groups = []
        for group_name, group_projects in name_groups.items():
            if len(group_projects) > 1:
                # Assign group ID
                group_id = str(uuid.uuid4())
                for project in group_projects:
                    project.duplicate_group_id = group_id
                    project.potential_duplicates = [p.path for p in group_projects if p.id != project.id]
                
                duplicate_groups.append({
                    "group_id": group_id,
                    "normalized_name": group_name,
                    "projects": [{"id": p.id, "name": p.name, "path": p.path} for p in group_projects]
                })
        
        self.db.commit()
        
        return {
            "total_groups": len(duplicate_groups),
            "total_duplicates": sum(len(g["projects"]) for g in duplicate_groups),
            "duplicate_groups": duplicate_groups[:10]  # Return first 10 groups
        }
    
    def _perform_scan(self, scan_id: str, scan_path: str, full_scan: bool):
        """
        Perform the actual scan with vibecoding joy
        Following Directive 19: Well-being with progress feedback
        """
        try:
            # Create async event loop for scanner
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Update progress
            self.scan_status[scan_id] = {
                "status": "running",
                "progress": 20,
                "message": "🔍 Discovering projects with vibecoding scanner..."
            }
            
            # Initialize scanner
            scanner = ProjectScanner(self.db)
            
            # Run the async scan
            result = loop.run_until_complete(
                scanner.scan_directory(scan_path, deep_scan=full_scan)
            )
            
            # Update scan history
            scan = self.db.query(ScanHistory).filter(
                ScanHistory.scan_id == scan_id
            ).first()
            
            if scan:
                scan.status = "completed"
                scan.completed_at = datetime.utcnow()
                scan.duration_seconds = result["scan_time"]
                scan.projects_found = result["projects_found"]
                scan.new_projects = len([p for p in result["projects"] if not p.get("existing")])
                scan.duplicates_found = result["duplicates_found"]
                
                # Store full result as JSON (with datetime serialization)
                serialized_result = self._serialize_datetime(result)
                scan.result_data = json.dumps(serialized_result)
                self.db.commit()
            
            # Update status with vibecoding message
            self.scan_status[scan_id] = {
                "status": "completed",
                "progress": 100,
                "message": f"✅ Scan complete! Found {result['projects_found']} projects with {result['vibe_level']} vibe! Eco-score: {result['eco_score']}%",
                "result": result
            }
            
            logger.info(f"Scan {scan_id} completed with {result['vibe_level']} vibe!")
            
        except Exception as e:
            logger.error(f"Scan {scan_id} failed: {e}")
            self.scan_status[scan_id] = {
                "status": "failed",
                "progress": 0,
                "message": f"❌ Scan failed: {str(e)}"
            }
            
            # Update database
            scan = self.db.query(ScanHistory).filter(
                ScanHistory.scan_id == scan_id
            ).first()
            if scan:
                scan.status = "failed"
                scan.error_message = str(e)
                self.db.commit()
        finally:
            loop.close()