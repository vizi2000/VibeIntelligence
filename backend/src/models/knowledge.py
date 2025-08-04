"""
Knowledge Management Models for Issues and Solutions
Following Directive 13 & 14 (Knowledge Management)
"""

from sqlalchemy import Column, String, Text, DateTime, Integer, Float, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime

from ..core.database import Base


class Issue(Base):
    """Stores identified issues and problems"""
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), index=True)  # e.g., "test_failure", "bug", "performance"
    subcategory = Column(String(50))  # e.g., "async", "import", "config"
    
    # Issue details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    error_message = Column(Text)
    stack_trace = Column(Text)
    
    # Context
    file_path = Column(String(500))
    line_number = Column(Integer)
    function_name = Column(String(255))
    
    # Metadata
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    frequency = Column(Integer, default=1)  # How often this issue occurs
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Vibecoding metrics
    vibe_impact = Column(Integer, default=0)  # How much this affects developer vibe (0-100)
    eco_impact = Column(Float, default=0.0)  # Environmental impact score
    
    # Vector embedding for semantic search
    embedding = Column(JSON)  # Store as JSON array
    
    # Relationships
    solutions = relationship("Solution", back_populates="issue", cascade="all, delete-orphan")
    occurrences = relationship("IssueOccurrence", back_populates="issue", cascade="all, delete-orphan")
    
    # Indexes for fast searching
    __table_args__ = (
        Index('idx_issue_category_severity', 'category', 'severity'),
        Index('idx_issue_file_path', 'file_path'),
    )


class Solution(Base):
    """Stores solutions for issues"""
    __tablename__ = "solutions"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, index=True)
    
    # Solution details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    code_snippet = Column(Text)  # Example code
    
    # Solution metadata
    solution_type = Column(String(50))  # e.g., "code_fix", "config_change", "dependency_update"
    effectiveness = Column(Float, default=1.0)  # 0-1 score of how well it works
    applied_count = Column(Integer, default=0)  # How many times applied
    success_count = Column(Integer, default=0)  # How many times it worked
    
    # Implementation details
    steps = Column(JSON)  # List of steps to implement
    prerequisites = Column(JSON)  # List of prerequisites
    side_effects = Column(JSON)  # Potential side effects
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Vibecoding metrics
    implementation_time = Column(Integer)  # Estimated minutes to implement
    complexity_score = Column(Integer, default=5)  # 1-10 scale
    developer_satisfaction = Column(Float)  # 0-5 stars from feedback
    
    # Vector embedding for semantic search
    embedding = Column(JSON)
    
    # Relationships
    issue = relationship("Issue", back_populates="solutions")
    feedback = relationship("SolutionFeedback", back_populates="solution", cascade="all, delete-orphan")


class IssueOccurrence(Base):
    """Tracks individual occurrences of issues"""
    __tablename__ = "issue_occurrences"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False, index=True)
    
    # Occurrence details
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    context = Column(JSON)  # Additional context data
    environment = Column(String(50))  # e.g., "development", "testing", "production"
    
    # Who/what encountered it
    user_id = Column(String(255))
    session_id = Column(String(255))
    
    # Resolution
    resolved = Column(String(10), default="pending")  # pending, resolved, ignored
    solution_id = Column(Integer, ForeignKey("solutions.id"))
    resolution_time = Column(Integer)  # Minutes to resolve
    
    # Relationships
    issue = relationship("Issue", back_populates="occurrences")


class SolutionFeedback(Base):
    """Stores feedback on solution effectiveness"""
    __tablename__ = "solution_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    solution_id = Column(Integer, ForeignKey("solutions.id"), nullable=False, index=True)
    
    # Feedback data
    rating = Column(Integer)  # 1-5 stars
    worked = Column(String(10))  # yes, no, partial
    time_to_implement = Column(Integer)  # Actual minutes
    comment = Column(Text)
    
    # Metadata
    user_id = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    solution = relationship("Solution", back_populates="feedback")


class KnowledgePattern(Base):
    """Stores learned patterns from issues and solutions"""
    __tablename__ = "knowledge_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Pattern details
    pattern_type = Column(String(50))  # e.g., "error_pattern", "fix_pattern"
    pattern = Column(JSON)  # Structured pattern data
    confidence = Column(Float, default=0.5)  # 0-1 confidence score
    
    # Related issues/solutions
    related_issues = Column(JSON)  # List of issue IDs
    related_solutions = Column(JSON)  # List of solution IDs
    
    # Usage metrics
    times_matched = Column(Integer, default=0)
    times_helpful = Column(Integer, default=0)
    
    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    
    # Vector embedding for pattern matching
    embedding = Column(JSON)