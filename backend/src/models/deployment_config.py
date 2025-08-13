"""
Deployment configuration model
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum
from ..core.database import Base


class DeploymentStatus(str, Enum):
    PENDING = "pending"
    BUILDING = "building"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DeploymentConfig(Base):
    __tablename__ = "deployment_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Configuration
    environment = Column(String(50), nullable=False)  # staging, production
    deployment_type = Column(String(50), nullable=False)  # docker, kubernetes, vercel, netlify
    config_data = Column(JSON, default={})  # Platform-specific config
    
    # Auto-deployment
    auto_deploy = Column(Boolean, default=False)
    deploy_branch = Column(String(100), default="main")
    
    # Deployment limits
    max_daily_deployments = Column(Integer, default=10)
    daily_deployment_count = Column(Integer, default=0)
    last_deployment_reset = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="deployment_configs")