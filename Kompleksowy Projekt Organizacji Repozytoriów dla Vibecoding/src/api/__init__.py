"""
API Module
Following Directive 2: API-First Development
"""

from fastapi import APIRouter
from .projects import router as projects_router
from .ai import router as ai_router
from .auth import router as auth_router
from .vibe import router as vibe_router

# Create main API router
router = APIRouter()

# Include sub-routers
router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
router.include_router(projects_router, prefix="/projects", tags=["Projects"])
router.include_router(ai_router, prefix="/ai", tags=["AI Services"])
router.include_router(vibe_router, prefix="/vibe", tags=["Vibecoding"])

__all__ = ["router"]