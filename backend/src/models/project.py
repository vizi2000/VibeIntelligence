"""
Project model
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    path = Column(String(500), nullable=False, unique=True)
    relative_path = Column(String(500))
    project_type = Column(String(100), index=True)
    tech_stack = Column(JSON, default=list)
    
    # Documentation and structure
    has_readme = Column(Boolean, default=False)
    has_documentation = Column(Boolean, default=False)
    has_tests = Column(Boolean, default=False)
    is_git_repo = Column(Boolean, default=False)
    has_docker = Column(Boolean, default=False)
    technologies = Column(JSON, default=list)  # List of detected technologies
    
    # Metrics
    size_mb = Column(Float, default=0.0)
    file_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=False, index=True)
    is_archived = Column(Boolean, default=False)
    
    # Vibecoding metrics (v4.0)
    vibe_score = Column(Integer, default=75)  # 0-100 happiness score
    eco_score = Column(Integer, default=80)   # 0-100 sustainability score
    health_score = Column(Integer, default=0)  # 0-100 project health score
    
    # Duplicates
    duplicate_group_id = Column(String(100), index=True)
    potential_duplicates = Column(JSON, default=list)
    
    # Timestamps
    last_modified = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_scanned_at = Column(DateTime(timezone=True))
    
    # Additional metadata
    metadata_json = Column(JSON, default=dict)
    
    # Relationships
    deployment_configs = relationship("DeploymentConfig", back_populates="project")