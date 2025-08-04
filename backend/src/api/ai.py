"""
AI-powered endpoints for Zenith Coder
Following v4.0 Vibecoding principles
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel

from ..core.database import get_db
from ..services.ai_service import ai_service
from ..services.project_service import ProjectService
from ..core.config import settings

router = APIRouter()


class AnalysisRequest(BaseModel):
    project_id: int
    
class DocumentationRequest(BaseModel):
    project_id: int
    style: str = "friendly"  # friendly, professional, technical
    
class CodeAnalysisRequest(BaseModel):
    code: str
    language: str = "python"
    
class VibeCheckResponse(BaseModel):
    vibe_score: int
    vibe_emoji: str
    message: str
    quantum_idea: str


@router.post("/analyze-project", response_model=Dict[str, Any])
async def analyze_project(
    request: AnalysisRequest,
    db: Session = Depends(get_db)
):
    """
    Analyze a project using AI for insights and recommendations
    Returns vibe score, eco score, and improvement suggestions
    """
    # Get project
    project_service = ProjectService(db)
    project = project_service.get_project(request.project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Analyze with AI
    analysis = await ai_service.analyze_project(project)
    
    # Update project scores in database
    project.vibe_score = analysis.get("vibe_score", 75)
    project.eco_score = analysis.get("eco_score", 80)
    db.commit()
    
    return {
        "project_id": project.id,
        "project_name": project.name,
        "analysis": analysis["analysis"],
        "vibe_score": analysis["vibe_score"],
        "eco_score": analysis["eco_score"],
        "recommendations": analysis.get("recommendations", []),
        "provider": analysis.get("provider", "unknown")
    }


@router.post("/generate-documentation", response_model=Dict[str, str])
async def generate_documentation(
    request: DocumentationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered documentation for a project
    Creates vibecoding-friendly README with emojis and inclusive language
    """
    # Get project
    project_service = ProjectService(db)
    project = project_service.get_project(request.project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Generate documentation
    documentation = await ai_service.generate_documentation(project)
    
    # Update project status
    project.has_documentation = True
    project.vibe_score = min(100, project.vibe_score + 10)  # Reward for docs!
    db.commit()
    
    return {
        "project_id": project.id,
        "project_name": project.name,
        "documentation": documentation,
        "message": "Documentation generated with love! 📚✨"
    }


@router.get("/project-suggestions/{project_id}", response_model=List[Dict[str, str]])
async def get_project_suggestions(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get AI-powered improvement suggestions for a project
    Focuses on sustainability, wellness, and code quality
    """
    # Get project
    project_service = ProjectService(db)
    project = project_service.get_project(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get suggestions
    suggestions = await ai_service.suggest_improvements(project)
    
    return suggestions


@router.post("/check-dei-compliance", response_model=Dict[str, Any])
async def check_dei_compliance(request: CodeAnalysisRequest):
    """
    Check code for DEI (Diversity, Equity, Inclusion) compliance
    Identifies non-inclusive language and accessibility issues
    """
    result = await ai_service.check_dei_compliance(request.code)
    
    return {
        "compliant": result["compliant"],
        "score": result["score"],
        "issues": result["issues"],
        "message": "Great job on inclusion! 🌈" if result["compliant"] else "Let's make this more inclusive! 💝"
    }


@router.post("/generate-adhd-summary", response_model=Dict[str, str])
async def generate_adhd_summary(text: str):
    """
    Generate ADHD-friendly summary with bullet points
    Makes long text more accessible and digestible
    """
    summary = await ai_service.generate_adhd_summary(text)
    
    return {
        "summary": summary,
        "tip": "Take breaks every 25 minutes for best focus! 🧘"
    }


@router.get("/quantum-idea", response_model=Dict[str, str])
async def get_quantum_idea():
    """
    Get a quantum-inspired creative coding idea
    Sparks innovation and out-of-the-box thinking
    """
    idea = await ai_service.get_quantum_idea()
    
    return {
        "idea": idea,
        "vibe": "Let your creativity flow! 🌊✨"
    }


@router.get("/vibe-check", response_model=VibeCheckResponse)
async def vibe_check():
    """
    Check the current vibe of the system
    Returns overall wellness metrics and a quantum idea
    """
    # Get quantum idea
    quantum_idea = await ai_service.get_quantum_idea()
    
    # Calculate system vibe (mock for now)
    vibe_score = 85
    
    vibe_emoji = "🤩" if vibe_score > 80 else "😊" if vibe_score > 60 else "😐"
    
    messages = {
        80: "System is vibing at maximum frequency! 🎉",
        60: "Good vibes flowing steadily! 🌊",
        40: "Vibes could use a boost - try a quantum idea! 🚀",
        0: "Low vibe alert - time for a break! 🌿"
    }
    
    message = next(msg for score, msg in sorted(messages.items(), reverse=True) if vibe_score > score)
    
    return VibeCheckResponse(
        vibe_score=vibe_score,
        vibe_emoji=vibe_emoji,
        message=message,
        quantum_idea=quantum_idea
    )


@router.get("/eco-impact", response_model=Dict[str, Any])
async def get_eco_impact(db: Session = Depends(get_db)):
    """
    Calculate environmental impact of all projects
    Provides sustainability metrics and recommendations
    """
    # Get project stats
    project_service = ProjectService(db)
    stats = project_service.get_statistics()
    
    # Calculate eco impact
    total_projects = stats["total_projects"]
    # Estimate size (mock - would calculate from actual data)
    estimated_size_gb = total_projects * 0.5  # 500MB average per project
    
    eco_impact = await ai_service.calculate_eco_impact(total_projects, estimated_size_gb)
    
    return {
        "total_projects": total_projects,
        "estimated_storage_gb": estimated_size_gb,
        **eco_impact,
        "tip": "Every small optimization helps the planet! 🌍💚"
    }