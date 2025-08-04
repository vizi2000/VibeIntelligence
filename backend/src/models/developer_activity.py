"""
Developer Activity Tracking Model
Tracks all developer actions for documentation agent
Following vibecoding principles for transparency
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class DeveloperActivity(Base):
    __tablename__ = "developer_activities"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False)
    
    # Activity Information
    activity_type = Column(String(50), nullable=False, index=True)  # code, prompt, command, file_edit
    action = Column(String(255), nullable=False)  # Specific action taken
    target = Column(String(500))  # File path, function name, etc.
    
    # Context
    project_id = Column(Integer, ForeignKey("projects.id"))
    session_id = Column(String(100), index=True)  # Group activities by session
    
    # Detailed Data
    details = Column(JSON, default={})  # Additional structured data
    prompt_used = Column(Text)  # AI prompts for transparency
    ai_response = Column(Text)  # AI responses for documentation
    code_before = Column(Text)  # Code state before change
    code_after = Column(Text)  # Code state after change
    
    # Metrics
    duration_seconds = Column(Integer)  # Time spent on activity
    lines_changed = Column(Integer, default=0)
    complexity_score = Column(Float, default=0.0)  # Code complexity
    focus_score = Column(Float, default=0.0)  # Focus level during activity
    
    # AI Integration
    ai_provider = Column(String(50))  # openrouter, openai, gemini
    ai_model = Column(String(100))  # Specific model used
    tokens_used = Column(Integer, default=0)
    ai_cost = Column(Float, default=0.0)
    
    # Vibecoding Metrics
    vibe_impact = Column(Integer, default=0)  # -10 to +10
    eco_impact = Column(Integer, default=0)  # Environmental impact score
    learning_value = Column(Integer, default=0)  # Educational value 0-10
    
    # Status
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    developer = relationship("DeveloperProfile", back_populates="activities")
    project = relationship("Project", backref="activities")
    
    def calculate_duration(self) -> None:
        """Calculate duration from timestamps"""
        if self.completed_at and self.started_at:
            delta = self.completed_at - self.started_at
            self.duration_seconds = int(delta.total_seconds())
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "developer_id": self.developer_id,
            "activity_type": self.activity_type,
            "action": self.action,
            "target": self.target,
            "project_id": self.project_id,
            "session_id": self.session_id,
            "details": self.details,
            "duration_seconds": self.duration_seconds,
            "lines_changed": self.lines_changed,
            "ai_provider": self.ai_provider,
            "ai_model": self.ai_model,
            "tokens_used": self.tokens_used,
            "vibe_impact": self.vibe_impact,
            "success": self.success,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class ActivitySummary(Base):
    """Daily activity summaries for quick access"""
    __tablename__ = "activity_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    
    # Summary Statistics
    total_activities = Column(Integer, default=0)
    total_duration_seconds = Column(Integer, default=0)
    total_lines_changed = Column(Integer, default=0)
    total_commits = Column(Integer, default=0)
    total_ai_tokens = Column(Integer, default=0)
    total_ai_cost = Column(Float, default=0.0)
    
    # Activity Breakdown
    activity_breakdown = Column(JSON, default={})  # {"code": 45, "prompt": 30, ...}
    language_breakdown = Column(JSON, default={})  # {"Python": 60, "JavaScript": 40}
    
    # Productivity Metrics
    average_focus_score = Column(Float, default=0.0)
    peak_productivity_hour = Column(Integer)  # 0-23
    flow_state_minutes = Column(Integer, default=0)
    
    # Vibecoding Scores
    daily_vibe_score = Column(Integer, default=50)
    daily_eco_score = Column(Integer, default=50)
    daily_learning_score = Column(Integer, default=50)
    
    # Highlights
    key_achievements = Column(JSON, default=[])  # Notable accomplishments
    main_projects = Column(JSON, default=[])  # Projects worked on
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)