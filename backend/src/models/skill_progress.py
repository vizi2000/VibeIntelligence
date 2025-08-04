"""
Skill Progress Tracking Model
Tracks developer skill growth over time
Following vibecoding principles for personal growth
"""

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class SkillProgress(Base):
    __tablename__ = "skill_progress"

    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False)
    
    # Skill Information
    skill_name = Column(String(100), nullable=False, index=True)  # "Python", "React", "Docker"
    skill_category = Column(String(50))  # "language", "framework", "tool", "concept"
    
    # Progress Tracking
    current_level = Column(Integer, default=0)  # 0-100
    previous_level = Column(Integer, default=0)
    level_change = Column(Integer, default=0)  # Can be negative
    
    # Learning Metrics
    practice_hours = Column(Float, default=0.0)
    lines_written = Column(Integer, default=0)
    projects_used_in = Column(Integer, default=0)
    errors_encountered = Column(Integer, default=0)
    errors_resolved = Column(Integer, default=0)
    
    # AI-Assessed Metrics
    code_quality_score = Column(Float, default=0.0)  # 0-100
    best_practices_score = Column(Float, default=0.0)  # 0-100
    innovation_score = Column(Float, default=0.0)  # 0-100
    
    # Learning Sources
    learning_sources = Column(JSON, default=[])  # ["documentation", "ai_assistance", "practice"]
    ai_interactions = Column(Integer, default=0)  # Number of AI helps for this skill
    
    # Milestones
    milestones_achieved = Column(JSON, default=[])  # List of achievement objects
    next_milestone = Column(JSON, default={})  # Next goal to achieve
    
    # Evidence
    code_samples = Column(JSON, default=[])  # Links to best code examples
    assessment_notes = Column(Text)  # AI-generated assessment
    
    # Timestamps
    first_used_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, default=datetime.utcnow)
    assessed_at = Column(DateTime)  # Last AI assessment
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    developer = relationship("DeveloperProfile", back_populates="skill_history")
    
    def add_milestone(self, milestone_name: str, description: str) -> None:
        """Add a new milestone achievement"""
        self.milestones_achieved.append({
            "name": milestone_name,
            "description": description,
            "achieved_at": datetime.utcnow().isoformat(),
            "level_at_achievement": self.current_level
        })
    
    def update_level(self, new_level: int) -> None:
        """Update skill level with tracking"""
        self.previous_level = self.current_level
        self.current_level = max(0, min(100, new_level))
        self.level_change = self.current_level - self.previous_level
        self.last_used_at = datetime.utcnow()
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "skill_name": self.skill_name,
            "skill_category": self.skill_category,
            "current_level": self.current_level,
            "level_change": self.level_change,
            "practice_hours": self.practice_hours,
            "projects_used_in": self.projects_used_in,
            "code_quality_score": self.code_quality_score,
            "milestones_achieved": self.milestones_achieved,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None
        }


class SkillRecommendation(Base):
    """AI-generated skill recommendations"""
    __tablename__ = "skill_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    developer_id = Column(Integer, ForeignKey("developer_profiles.id"), nullable=False)
    
    # Recommendation Details
    skill_name = Column(String(100), nullable=False)
    recommendation_type = Column(String(50))  # "learn_new", "improve", "combine"
    priority = Column(String(20), default="medium")  # low, medium, high
    
    # Reasoning
    reason = Column(Text)  # Why this skill is recommended
    market_demand = Column(Integer, default=50)  # 0-100 market demand score
    synergy_score = Column(Integer, default=50)  # How well it fits with existing skills
    
    # Learning Path
    suggested_resources = Column(JSON, default=[])  # Learning resources
    estimated_hours = Column(Integer)  # Hours to reach proficiency
    prerequisite_skills = Column(JSON, default=[])  # Required skills first
    
    # Potential Benefits
    career_impact = Column(JSON, default={})  # Career benefits
    project_applications = Column(JSON, default=[])  # How it can be used
    monetization_potential = Column(Integer, default=50)  # 0-100
    
    # Status
    accepted = Column(String, default=None)  # None, "accepted", "rejected"
    started_learning = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # Recommendation expiry