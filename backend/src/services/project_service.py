"""
Project management service
"""

from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from ..models.project import Project

class ProjectService:
    def __init__(self, db: Session):
        self.db = db
    
    def list_projects(
        self,
        skip: int = 0,
        limit: int = 100,
        project_type: Optional[str] = None,
        has_documentation: Optional[bool] = None,
        is_active: Optional[bool] = None
    ) -> List[Project]:
        """List projects with optional filtering"""
        query = self.db.query(Project)
        
        if project_type:
            query = query.filter(Project.project_type == project_type)
        if has_documentation is not None:
            query = query.filter(Project.has_documentation == has_documentation)
        if is_active is not None:
            query = query.filter(Project.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """Get a project by ID"""
        return self.db.query(Project).filter(Project.id == project_id).first()
    
    def get_duplicate_groups(self) -> List[List[Project]]:
        """Get groups of duplicate projects"""
        # Get all projects with duplicate_group_id
        projects_with_dups = self.db.query(Project).filter(
            Project.duplicate_group_id.isnot(None)
        ).all()
        
        # Group by duplicate_group_id
        groups = {}
        for project in projects_with_dups:
            group_id = project.duplicate_group_id
            if group_id not in groups:
                groups[group_id] = []
            groups[group_id].append(project)
        
        return list(groups.values())
    
    def activate_project(self, project_id: int) -> Optional[Project]:
        """Mark a project as active"""
        project = self.get_project(project_id)
        if project:
            project.is_active = True
            project.is_archived = False
            self.db.commit()
            self.db.refresh(project)
        return project
    
    def archive_project(self, project_id: int) -> Optional[Project]:
        """Archive a project"""
        project = self.get_project(project_id)
        if project:
            project.is_active = False
            project.is_archived = True
            self.db.commit()
            self.db.refresh(project)
        return project
    
    def get_statistics(self) -> Dict:
        """Get project statistics"""
        total = self.db.query(Project).count()
        active = self.db.query(Project).filter(Project.is_active == True).count()
        archived = self.db.query(Project).filter(Project.is_archived == True).count()
        documented = self.db.query(Project).filter(Project.has_documentation == True).count()
        with_docker = self.db.query(Project).filter(Project.has_docker == True).count()
        with_git = self.db.query(Project).filter(Project.is_git_repo == True).count()
        
        # Get project type distribution
        type_counts = {}
        types = self.db.query(Project.project_type, self.db.func.count(Project.id))\
            .group_by(Project.project_type).all()
        for ptype, count in types:
            type_counts[ptype or 'Unknown'] = count
        
        return {
            "total_projects": total,
            "active_projects": active,
            "archived_projects": archived,
            "documented_projects": documented,
            "projects_with_docker": with_docker,
            "projects_with_git": with_git,
            "project_types": type_counts
        }