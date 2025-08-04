"""
Zenith Coder Main Application
Following all Version 4.0 Vibecoding directives
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .core.config import settings
from .core.logging_config import setup_logging
from .core.database import init_db, close_db
from .ai import orchestrator
from .api import router as api_router

# Setup vibe-aware logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    Handles startup and shutdown with good vibes
    """
    # Startup
    logger.info("🚀 Starting Zenith Coder with Vibecoding v4.0...")
    
    try:
        # Initialize database
        await init_db()
        logger.info("✅ Database connected and vibing!")
        
        # Initialize AI orchestrator
        await orchestrator.initialize()
        logger.info("✅ AI providers initialized and ready!")
        
        # Log startup success
        logger.info(
            f"🎉 Zenith Coder started successfully!",
            extra={"vibe_score": 10, "eco_score": 100}
        )
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}", extra={"vibe_score": 1})
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Zenith Coder gracefully...")
    
    try:
        # Cleanup AI providers
        await orchestrator.cleanup()
        
        # Close database
        await close_db()
        
        logger.info("🙏 Thank you for vibecoding! See you next time!")
        
    except Exception as e:
        logger.error(f"⚠️ Shutdown error: {e}")


# Create FastAPI app with vibecoding metadata
app = FastAPI(
    title="Zenith Coder API",
    description=(
        "🌟 AI-powered project organization with Vibecoding principles\n\n"
        "Following Version 4.0 directives for joyful, sustainable coding"
    ),
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add middleware for better vibes
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression for eco-friendly data transfer
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Health check endpoint
@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint with vibe status
    Returns system health and happiness levels
    """
    try:
        # Check AI providers
        ai_stats = await orchestrator.get_usage_stats()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "vibe": "high",
                "version": settings.VERSION,
                "environment": settings.ENVIRONMENT,
                "ai_providers": len(orchestrator.providers),
                "eco_score": ai_stats.get("average_eco_score", 0),
                "message": "🌟 All systems vibing!"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "vibe": "low",
                "error": str(e),
                "message": "😔 Systems need some love"
            }
        )


# Vibe check endpoint (v4.0 feature)
@app.get("/vibe", tags=["Vibecoding"])
async def vibe_check():
    """
    Check the current vibe of the system
    Returns vibe metrics and a quantum idea
    """
    quantum_idea = await orchestrator.get_quantum_idea()
    ai_stats = await orchestrator.get_usage_stats()
    
    return {
        "current_vibe": "✨ Magnificent",
        "vibe_score": 9,
        "eco_score": ai_stats.get("average_eco_score", 0),
        "quantum_idea": quantum_idea,
        "affirmation": "You're doing amazing, sweetie! 💖",
        "tokens_saved": ai_stats.get("total_tokens", 0),
        "co2_saved_grams": ai_stats.get("total_tokens", 0) * 0.001
    }


# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint with welcoming message
    """
    return {
        "message": "🌟 Welcome to Zenith Coder API!",
        "version": settings.VERSION,
        "docs": "/api/docs",
        "health": "/health",
        "vibe": "/vibe"
    }


# Custom 404 handler with helpful vibes
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404s with grace and suggestions"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "🔍 Oops! This endpoint doesn't exist yet.",
            "suggestion": "Check /api/docs for available endpoints",
            "vibe": "It's okay, we all get lost sometimes! 💫"
        }
    )


# Custom error handler with compassion
@app.exception_handler(500)
async def server_error_handler(request, exc):
    """Handle 500s with empathy"""
    logger.error(f"Server error: {exc}", extra={"vibe_score": 1})
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "😓 Something went wrong on our end.",
            "suggestion": "Take a deep breath. We're looking into it!",
            "vibe": "Even servers need a break sometimes 🌿"
        }
    )


# Run the application
if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None  # Use our custom logging
    )