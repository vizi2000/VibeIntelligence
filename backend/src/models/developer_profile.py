"""
Developer Profile Model
Following Directive 18: ADHD-friendly developer tracking
Stores developer information, skills, and preferences
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class DeveloperProfile(Base):
    __tablename__ = "developer_profiles"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True)
    full_name = Column(String(255))
    
    # ADHD Support Features
    adhd_mode_enabled = Column(Boolean, default=True)
    preferred_task_duration = Column(Integer, default=25)  # minutes
    break_reminder_interval = Column(Integer, default=60)  # minutes
    notification_preferences = Column(JSON, default={
        "desktop": True,
        "sound": True,
        "vibration": False
    })
    
    # Skill Tracking
    primary_languages = Column(JSON, default=[])  # ["Python", "JavaScript", "Go"]
    frameworks = Column(JSON, default=[])  # ["FastAPI", "React", "Django"]
    skill_levels = Column(JSON, default={})  # {"Python": 85, "JavaScript": 70}
    specializations = Column(JSON, default=[])  # ["AI/ML", "Backend", "DevOps"]
    
    # Work Patterns
    preferred_work_hours = Column(JSON, default={
        "start": "09:00",
        "end": "17:00",
        "timezone": "UTC"
    })
    productivity_patterns = Column(JSON, default={})  # Time-based productivity scores
    focus_score = Column(Float, default=0.0)  # 0-100 focus score
    
    # Vibecoding Metrics
    vibe_score = Column(Integer, default=50)  # 0-100
    eco_score = Column(Integer, default=50)  # 0-100
    wellbeing_score = Column(Integer, default=50)  # 0-100
    flow_state_percentage = Column(Float, default=0.0)  # % of time in flow
    
    # Project Preferences
    preferred_project_types = Column(JSON, default=[])  # ["SaaS", "AI", "Open Source"]
    monetization_interests = Column(JSON, default=[])  # ["Freelance", "Products", "Courses"]
    
    # AI Interaction Preferences
    preferred_ai_models = Column(JSON, default=[])  # ["gpt-4", "claude-3", "gemini"]
    ai_personality_preference = Column(String(50), default="friendly")  # friendly, professional, quirky
    
    # Achievements & Gamification
    total_commits = Column(Integer, default=0)
    total_projects = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)
    badges = Column(JSON, default=[])  # Achievement badges
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_active_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    activities = relationship("DeveloperActivity", back_populates="developer", cascade="all, delete-orphan")
    agent_tasks = relationship("AgentTask", back_populates="developer", cascade="all, delete-orphan")
    skill_history = relationship("SkillProgress", back_populates="developer", cascade="all, delete-orphan")
    
    def update_vibe_score(self, delta: int) -> None:
        """Update vibe score within bounds"""
        self.vibe_score = max(0, min(100, self.vibe_score + delta))
        self.updated_at = datetime.utcnow()
    
    def add_badge(self, badge_name: str, badge_data: dict) -> None:
        """Add achievement badge"""
        if not any(b.get("name") == badge_name for b in self.badges):
            self.badges.append({
                "name": badge_name,
                "data": badge_data,
                "earned_at": datetime.utcnow().isoformat()
            })
    
    def update_skill_level(self, skill: str, level: int) -> None:
        """Update skill level"""
        if not self.skill_levels:
            self.skill_levels = {}
        self.skill_levels[skill] = max(0, min(100, level))
        
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "adhd_mode_enabled": self.adhd_mode_enabled,
            "preferred_task_duration": self.preferred_task_duration,
            "primary_languages": self.primary_languages,
            "skill_levels": self.skill_levels,
            "vibe_score": self.vibe_score,
            "eco_score": self.eco_score,
            "wellbeing_score": self.wellbeing_score,
            "flow_state_percentage": self.flow_state_percentage,
            "total_commits": self.total_commits,
            "total_projects": self.total_projects,
            "completed_tasks": self.completed_tasks,
            "streak_days": self.streak_days,
            "badges": self.badges,
            "last_active_at": self.last_active_at.isoformat() if self.last_active_at else None
        }