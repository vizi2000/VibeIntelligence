"""
Scan history model
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Float
from sqlalchemy.sql import func
from ..core.database import Base

class ScanHistory(Base):
    __tablename__ = "scan_history"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(100), unique=True, index=True)
    scan_type = Column(String(50))  # 'full', 'incremental', 'targeted'
    status = Column(String(50))  # 'running', 'completed', 'failed'
    
    # Scan details
    base_path = Column(String(500))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    
    # Results
    projects_found = Column(Integer, default=0)
    new_projects = Column(Integer, default=0)
    updated_projects = Column(Integer, default=0)
    duplicates_found = Column(Integer, default=0)
    
    # Errors and logs
    error_message = Column(Text)
    scan_log = Column(JSON, default=list)
    
    # Summary statistics
    summary = Column(JSON, default=dict)
    
    # Vibecoding additions
    result_data = Column(JSON, default=dict)


class ScanResult(Base):
    """
    Detailed scan results with vibecoding metrics
    Following Directive 17: Eco-awareness
    """
    __tablename__ = "scan_results"
    
    id = Column(String(100), primary_key=True, index=True)  # scan_id
    path = Column(String(500))
    projects_found = Column(Integer, default=0)
    duplicates_found = Column(Integer, default=0)
    total_files = Column(Integer, default=0)
    scan_duration = Column(Float)
    
    # Vibecoding metrics
    eco_score = Column(Integer, default=100)
    vibe_level = Column(String(50))
    
    # Full result data
    result_data = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    
class FileInfo(Base):
    """File information from scans"""
    __tablename__ = "file_info"
    
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(500), index=True)
    size_bytes = Column(Integer)
    hash = Column(String(64))
    last_modified = Column(DateTime(timezone=True))
    project_id = Column(Integer)