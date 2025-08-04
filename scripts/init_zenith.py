#!/usr/bin/env python3
"""
Initialize Zenith Coder database and load initial project data
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from src.core.database import engine, Base, SessionLocal
from src.models.project import Project
from src.models.scan import ScanHistory
from src.models.deployment import Deployment
from datetime import datetime
import uuid

def init_database():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")

def load_initial_projects():
    """Load projects from the inventory report"""
    report_path = Path(__file__).parent.parent / "project_inventory_report.json"
    
    if not report_path.exists():
        print("❌ Inventory report not found. Run the scanner first.")
        return
    
    print("Loading project inventory...")
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    db = SessionLocal()
    
    try:
        # Check if already loaded
        existing = db.query(Project).count()
        if existing > 0:
            print(f"ℹ️  Database already contains {existing} projects")
            return
        
        # Create a scan history entry
        scan = ScanHistory(
            scan_id=str(uuid.uuid4()),
            scan_type="initial_import",
            status="completed",
            base_path=report['base_path'],
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            duration_seconds=0,
            projects_found=len(report['projects']),
            new_projects=len(report['projects']),
            summary=report['summary']
        )
        db.add(scan)
        
        # Load projects
        for project_data in report['projects']:
            project = Project(
                name=project_data['name'],
                path=project_data['path'],
                relative_path=project_data.get('relative_path', ''),
                project_type=project_data.get('project_type', 'Unknown'),
                tech_stack=project_data.get('tech_stack', []),
                has_readme=project_data.get('has_readme', False),
                has_documentation=project_data.get('has_documentation', False),
                is_git_repo=project_data.get('is_git_repo', False),
                has_docker=project_data.get('has_docker', False),
                size_mb=project_data.get('size_mb', 0),
                last_modified=datetime.fromisoformat(project_data['last_modified']) 
                    if project_data.get('last_modified') != 'Unknown' else None,
                potential_duplicates=project_data.get('potential_duplicates', []),
                last_scanned_at=datetime.utcnow()
            )
            db.add(project)
        
        db.commit()
        print(f"✅ Loaded {len(report['projects'])} projects into database")
        
    except Exception as e:
        print(f"❌ Error loading projects: {e}")
        db.rollback()
    finally:
        db.close()

def load_deployments():
    """Load active deployments from DEPLOYMENT_REGISTRY.md"""
    registry_path = Path("/Users/wojciechwiesner/ai/DEPLOYMENT_REGISTRY.md")
    
    if not registry_path.exists():
        print("❌ Deployment registry not found")
        return
    
    print("Loading deployment registry...")
    
    # Parse the registry file
    with open(registry_path, 'r') as f:
        content = f.read()
    
    db = SessionLocal()
    
    try:
        # Parse deployments (simplified version)
        lines = content.split('\n')
        in_table = False
        loaded = 0
        
        for line in lines:
            if '| Port' in line and '| Service Name' in line:
                in_table = True
                continue
            
            if in_table and line.strip().startswith('|'):
                parts = [p.strip() for p in line.split('|') if p.strip()]
                
                if len(parts) >= 7 and parts[0].isdigit():
                    port = int(parts[0])
                    
                    # Skip reserved ports
                    if parts[1] == '-':
                        continue
                    
                    deployment = Deployment(
                        port=port,
                        service_name=parts[1],
                        project_path=parts[2],
                        status='running' if '🟢' in parts[3] else 'stopped',
                        container_id=parts[5] if parts[5] != '-' else None,
                        is_active=True,
                        started_at=datetime.utcnow()
                    )
                    db.add(deployment)
                    loaded += 1
        
        db.commit()
        print(f"✅ Loaded {loaded} active deployments")
        
    except Exception as e:
        print(f"❌ Error loading deployments: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main initialization function"""
    print("=" * 60)
    print("Zenith Coder Database Initialization")
    print("=" * 60)
    
    # Initialize database
    init_database()
    
    # Load initial data
    load_initial_projects()
    load_deployments()
    
    print("\n✅ Initialization complete!")
    print("\nYou can now start the backend with:")
    print("  cd backend && uvicorn src.main:app --reload --port 8100")

if __name__ == "__main__":
    main()