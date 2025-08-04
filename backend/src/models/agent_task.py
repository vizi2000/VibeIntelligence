"""
Agent Task Model
Manages background agent tasks and scheduling
Following Directive 8: Multi-agent orchestration
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from enum import Enum
from ..core.database import Base


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SCHEDULED = "scheduled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentType(str, Enum):
    DOCUMENTATION = "documentation"
    SCANNER = "scanner"
    ANALYZER = "analyzer"
    MONETIZATION = "monetization"
    SKILL_TRACKER = "skill_tracker"
    TASK_SUGGESTER = "task_suggester"
    NEWS_AGGREGATOR = "news_aggregator"
    COMPLIANCE_CHECKER = "compliance_checker"
    FEASIBILITY_ANALYST = "feasibility_analyst"


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False)
    
    # Task Information
    agent_type = Column(String(50), nullable=False, index=True)
    task_name = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(20), default=TaskPriority.MEDIUM)
    
    # Scheduling
    status = Column(String(20), default=TaskStatus.PENDING, index=True)
    scheduled_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    next_run_at = Column(DateTime)  # For recurring tasks
    
    # Recurrence
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(JSON)  # {"type": "daily", "interval": 1}
    max_retries = Column(Integer, default=3)
    retry_count = Column(Integer, default=0)
    
    # Task Parameters
    input_data = Column(JSON, default={})
    output_data = Column(JSON, default={})
    context = Column(JSON, default={})  # Additional context
    
    # Execution Details
    execution_time_seconds = Column(Float)
    ai_provider = Column(String(50))
    ai_model = Column(String(100))
    tokens_used = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    
    # Error Handling
    error_message = Column(Text)
    error_details = Column(JSON)
    
    # Vibecoding Metrics
    impact_score = Column(Integer, default=0)  # Task impact 0-100
    automation_score = Column(Integer, default=0)  # How well it automates work
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    developer = relationship("DeveloperProfile", back_populates="agent_tasks")
    subtasks = relationship("AgentSubtask", back_populates="parent_task", cascade="all, delete-orphan")
    
    def schedule_next_run(self) -> None:
        """Schedule next run for recurring tasks"""
        if not self.is_recurring or not self.recurrence_pattern:
            return
            
        pattern = self.recurrence_pattern
        if pattern.get("type") == "minutes":
            self.next_run_at = datetime.utcnow() + timedelta(minutes=pattern.get("interval", 60))
        elif pattern.get("type") == "hourly":
            self.next_run_at = datetime.utcnow() + timedelta(hours=pattern.get("interval", 1))
        elif pattern.get("type") == "daily":
            self.next_run_at = datetime.utcnow() + timedelta(days=pattern.get("interval", 1))
        elif pattern.get("type") == "weekly":
            self.next_run_at = datetime.utcnow() + timedelta(weeks=pattern.get("interval", 1))
    
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return self.retry_count < self.max_retries
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "developer_id": self.developer_id,
            "agent_type": self.agent_type,
            "task_name": self.task_name,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "is_recurring": self.is_recurring,
            "execution_time_seconds": self.execution_time_seconds,
            "tokens_used": self.tokens_used,
            "cost": self.cost,
            "error_message": self.error_message,
            "impact_score": self.impact_score
        }


class AgentSubtask(Base):
    """Subtasks for complex agent operations"""
    __tablename__ = "agent_subtasks"
    
    id = Column(Integer, primary_key=True, index=True)
    parent_task_id = Column(Integer, ForeignKey("agent_tasks.id"), nullable=False)
    
    # Subtask Information
    name = Column(String(255), nullable=False)
    description = Column(Text)
    sequence_order = Column(Integer, default=0)  # Execution order
    
    # Status
    status = Column(String(20), default=TaskStatus.PENDING)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Data
    input_data = Column(JSON, default={})
    output_data = Column(JSON, default={})
    
    # Error Handling
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    parent_task = relationship("AgentTask", back_populates="subtasks")


class AgentSchedule(Base):
    """Agent scheduling preferences and patterns"""
    __tablename__ = "agent_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False)
    agent_type = Column(String(50), nullable=False)
    
    # Schedule Configuration
    enabled = Column(Boolean, default=True)
    schedule_pattern = Column(JSON, default={})  # Cron-like pattern
    
    # Time Preferences
    preferred_hours = Column(JSON, default=[])  # [9, 10, 11, ...] hours when agent should run
    blackout_periods = Column(JSON, default=[])  # Times when agent should not run
    
    # Resource Limits
    max_daily_runs = Column(Integer, default=10)
    max_tokens_per_run = Column(Integer, default=1000)
    max_cost_per_day = Column(Float, default=1.0)
    
    # Current Usage
    daily_runs_count = Column(Integer, default=0)
    daily_tokens_used = Column(Integer, default=0)
    daily_cost_used = Column(Float, default=0.0)
    last_reset_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)