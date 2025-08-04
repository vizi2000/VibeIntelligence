"""
Deployment tracking model
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from ..core.database import Base

class Deployment(Base):
    __tablename__ = "deployments"
    
    id = Column(Integer, primary_key=True, index=True)
    port = Column(Integer, unique=True, index=True)
    service_name = Column(String(255), nullable=False)
    project_path = Column(String(500))
    project_id = Column(Integer)  # FK to projects table when needed
    
    # Status
    status = Column(String(50))  # 'running', 'stopped', 'failed'
    is_active = Column(Boolean, default=True, index=True)
    
    # Container info
    container_id = Column(String(100))
    container_name = Column(String(255))
    
    # URLs and access
    urls = Column(JSON, default=list)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True))
    stopped_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Additional metadata
    environment = Column(String(50))  # 'development', 'staging', 'production'
    tech_stack = Column(JSON, default=list)
    notes = Column(String(500))