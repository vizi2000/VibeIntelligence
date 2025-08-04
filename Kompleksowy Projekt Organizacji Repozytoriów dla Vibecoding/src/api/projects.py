"""
Projects API Routes
Following Directive 3: Modular Architecture
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from pathlib import Path

from .auth import get_current_user
from ..core.exceptions import ValidationException

router = APIRouter()


# Pydantic models
class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    path: str
    language: Optional[str] = None
    framework: Optional[str] = None
    category: Optional[str] = None
    tags: List[str] = []
    
class ProjectCreate(ProjectBase):
    pass
    
class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    
class ProjectResponse(ProjectBase):
    id: str
    size_mb: float
    file_count: int
    last_modified: datetime
    vibe_score: int = 75
    eco_score: int = 80
    created_at: datetime
    updated_at: datetime
    
class ProjectStats(BaseModel):
    total_projects: int
    total_size_gb: float
    languages: Dict[str, int]
    frameworks: Dict[str, int]
    average_vibe_score: float
    eco_impact: Dict[str, Any]


# Temporary project storage (replace with database)
PROJECTS_DB = {}


def calculate_project_scores(project: dict) -> dict:
    """
    Calculate vibe and eco scores for a project
    Following Directive 17: Eco-friendly practices
    """
    # Base scores
    vibe_score = 75
    eco_score = 80
    
    # Adjust based on project characteristics
    if project.get("has_tests"):
        vibe_score += 10
        eco_score += 5
    
    if project.get("has_docs"):
        vibe_score += 10
        
    if project.get("uses_renewable_energy"):
        eco_score += 15
        
    # Penalize large projects
    size_mb = project.get("size_mb", 0)
    if size_mb > 100:
        eco_score -= min(20, size_mb // 50)
    
    return {
        "vibe_score": min(100, vibe_score),
        "eco_score": max(0, eco_score)
    }


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    language: Optional[str] = None,
    sort_by: str = Query("name", regex="^(name|size|vibe_score|eco_score|updated)$")
):
    """
    List all projects with filtering and sorting
    Implements smart pagination for eco-friendly data transfer
    """
    # Filter projects (mock implementation)
    projects = list(PROJECTS_DB.values())
    
    # Apply filters
    if search:
        projects = [
            p for p in projects
            if search.lower() in p["name"].lower() or
               search.lower() in p.get("description", "").lower()
        ]
    
    if category:
        projects = [p for p in projects if p.get("category") == category]
        
    if language:
        projects = [p for p in projects if p.get("language") == language]
    
    # Sort projects
    sort_key = {
        "name": lambda x: x["name"],
        "size": lambda x: x.get("size_mb", 0),
        "vibe_score": lambda x: x.get("vibe_score", 0),
        "eco_score": lambda x: x.get("eco_score", 0),
        "updated": lambda x: x.get("updated_at", datetime.min)
    }
    projects.sort(key=sort_key[sort_by], reverse=sort_by != "name")
    
    # Paginate
    total = len(projects)
    projects = projects[skip:skip + limit]
    
    return projects


@router.get("/stats", response_model=ProjectStats)
async def get_project_stats(current_user: dict = Depends(get_current_user)):
    """
    Get project statistics with eco-impact analysis
    Following Directive 17: Environmental consciousness
    """
    projects = list(PROJECTS_DB.values())
    
    if not projects:
        return ProjectStats(
            total_projects=0,
            total_size_gb=0,
            languages={},
            frameworks={},
            average_vibe_score=0,
            eco_impact={"status": "No data yet"}
        )
    
    # Calculate stats
    total_size_mb = sum(p.get("size_mb", 0) for p in projects)
    
    # Count languages and frameworks
    languages = {}
    frameworks = {}
    vibe_scores = []
    
    for project in projects:
        if lang := project.get("language"):
            languages[lang] = languages.get(lang, 0) + 1
            
        if fw := project.get("framework"):
            frameworks[fw] = frameworks.get(fw, 0) + 1
            
        vibe_scores.append(project.get("vibe_score", 75))
    
    # Calculate eco impact
    co2_per_gb = 0.5  # kg CO2 per GB stored
    trees_needed = (total_size_mb / 1024) * co2_per_gb / 20  # 1 tree absorbs ~20kg CO2/year
    
    return ProjectStats(
        total_projects=len(projects),
        total_size_gb=round(total_size_mb / 1024, 2),
        languages=languages,
        frameworks=frameworks,
        average_vibe_score=sum(vibe_scores) / len(vibe_scores),
        eco_impact={
            "estimated_co2_kg_per_year": round((total_size_mb / 1024) * co2_per_gb, 2),
            "trees_to_offset": round(trees_needed, 1),
            "green_hosting_savings": "30% with renewable energy",
            "optimization_potential": "High" if total_size_mb > 10000 else "Medium"
        }
    )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get project details with vibe analysis"""
    project = PROJECTS_DB.get(project_id)
    
    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found - but don't worry, we'll help you find it! 🔍"
        )
    
    return project


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    project_data: ProjectCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a new project with automatic vibe scoring
    Awards eco credits for sustainable project practices
    """
    # Generate ID
    project_id = f"proj_{len(PROJECTS_DB) + 1}"
    
    # Create project
    project = {
        "id": project_id,
        **project_data.dict(),
        "size_mb": 0,  # Will be calculated on scan
        "file_count": 0,
        "last_modified": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "owner_id": current_user["id"]
    }
    
    # Calculate scores
    scores = calculate_project_scores(project)
    project.update(scores)
    
    PROJECTS_DB[project_id] = project
    
    # Award eco credits for creating organized project
    current_user["eco_credits"] = current_user.get("eco_credits", 0) + 10
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update project information with vibe preservation"""
    project = PROJECTS_DB.get(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Update fields
    update_data = project_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        project[field] = value
    
    project["updated_at"] = datetime.utcnow()
    
    # Recalculate scores
    scores = calculate_project_scores(project)
    project.update(scores)
    
    return project


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete project (with eco-friendly reminder)
    Suggests archiving instead of deleting
    """
    if project_id not in PROJECTS_DB:
        raise HTTPException(status_code=404, detail="Project not found")
    
    project = PROJECTS_DB[project_id]
    
    # Eco-friendly suggestion
    if project.get("size_mb", 0) > 50:
        return {
            "message": "Project marked for deletion",
            "suggestion": "Consider archiving instead of deleting to preserve your work! 🌱",
            "eco_tip": "Archived projects use 70% less resources than active ones",
            "confirm_delete": False
        }
    
    del PROJECTS_DB[project_id]
    
    return {
        "message": "Project deleted successfully",
        "vibe": "It's okay to let go sometimes 🍃"
    }


@router.post("/{project_id}/scan")
async def scan_project(
    project_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Scan project directory for updates
    Analyzes code quality and eco-impact
    """
    project = PROJECTS_DB.get(project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Mock scan results
    scan_results = {
        "files_scanned": 150,
        "size_mb": 25.4,
        "languages_detected": ["Python", "JavaScript"],
        "frameworks_detected": ["FastAPI", "React"],
        "has_tests": True,
        "has_docs": True,
        "code_quality": {
            "complexity": "Low",
            "maintainability": "High",
            "test_coverage": "85%"
        },
        "eco_analysis": {
            "unused_dependencies": 3,
            "large_files": 2,
            "optimization_suggestions": [
                "Remove unused dependency 'old-package'",
                "Compress images in assets/ folder",
                "Consider lazy loading for large modules"
            ]
        },
        "vibe_analysis": {
            "positive_comments": 45,
            "helpful_docstrings": 120,
            "emoji_count": 23,
            "vibe_words": ["awesome", "great", "thanks", "helpful"]
        }
    }
    
    # Update project with scan results
    project.update({
        "size_mb": scan_results["size_mb"],
        "file_count": scan_results["files_scanned"],
        "language": scan_results["languages_detected"][0] if scan_results["languages_detected"] else None,
        "framework": scan_results["frameworks_detected"][0] if scan_results["frameworks_detected"] else None,
        "last_modified": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    })
    
    # Recalculate scores based on scan
    scores = calculate_project_scores(project)
    project.update(scores)
    
    return {
        "message": "Project scanned successfully! 🔍",
        "scan_results": scan_results,
        "new_vibe_score": project["vibe_score"],
        "new_eco_score": project["eco_score"],
        "recommendation": "Your project is looking great! Consider the eco suggestions for even better vibes 🌱"
    }


@router.post("/import")
async def import_projects(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Import projects from inventory file
    Supports JSON format from project scanner
    """
    if not file.filename.endswith('.json'):
        raise ValidationException("import", "Only JSON files are supported")
    
    try:
        contents = await file.read()
        data = json.loads(contents)
        
        imported_count = 0
        for project_data in data.get("projects", []):
            # Create project from import
            project_id = f"proj_{len(PROJECTS_DB) + 1}"
            
            project = {
                "id": project_id,
                "name": project_data.get("name", "Unknown"),
                "path": project_data.get("path", ""),
                "description": project_data.get("description"),
                "size_mb": project_data.get("size_mb", 0),
                "file_count": project_data.get("file_count", 0),
                "language": project_data.get("primary_language"),
                "framework": project_data.get("framework"),
                "tags": project_data.get("technologies", []),
                "category": project_data.get("category"),
                "last_modified": datetime.fromisoformat(project_data.get("last_modified", datetime.utcnow().isoformat())),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "owner_id": current_user["id"]
            }
            
            # Calculate scores
            scores = calculate_project_scores(project)
            project.update(scores)
            
            PROJECTS_DB[project_id] = project
            imported_count += 1
        
        # Award eco credits for bulk organization
        eco_bonus = min(100, imported_count * 2)
        current_user["eco_credits"] = current_user.get("eco_credits", 0) + eco_bonus
        
        return {
            "message": f"Successfully imported {imported_count} projects! 🎉",
            "imported_count": imported_count,
            "eco_credits_earned": eco_bonus,
            "vibe": "Great job organizing your digital garden! 🌿"
        }
        
    except json.JSONDecodeError:
        raise ValidationException("import", "Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")