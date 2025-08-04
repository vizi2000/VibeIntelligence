"""
Zenith Coder - Main FastAPI Application

This is the entry point for the Zenith Coder AI-powered development platform.
It orchestrates all the AI agents, project management, and development workflow automation.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from src.core.config import settings
from src.core.database import init_db
from src.core.logging_config import setup_logging
from src.api.routes import api_router
from src.ai.orchestrator import AIOrchestrator
from src.core.exceptions import ZenithException

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("🚀 Starting Zenith Coder...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Initialize AI Orchestrator
    ai_orchestrator = AIOrchestrator()
    await ai_orchestrator.initialize()
    app.state.ai_orchestrator = ai_orchestrator
    logger.info("✅ AI Orchestrator initialized")
    
    logger.info("🎯 Zenith Coder is ready to transform your development workflow!")
    
    yield
    
    # Cleanup
    logger.info("🔄 Shutting down Zenith Coder...")
    await ai_orchestrator.cleanup()
    logger.info("👋 Zenith Coder shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Zenith Coder API",
    description="""
    🚀 **Zenith Coder** - AI-Powered Development Platform
    
    An intelligent development platform that transforms chaotic development environments 
    into organized, automated, and monetization-focused ecosystems.
    
    ## Features
    
    * 🔍 **Intelligent Project Organization** - Automatic scanning and cleanup
    * 📚 **AI-Powered Documentation** - Generate and maintain docs automatically  
    * 📋 **ADHD-Friendly Task Management** - Break down tasks into manageable chunks
    * 💰 **Monetization Support** - Find opportunities and optimize for revenue
    * 🚀 **Streamlined Deployment** - Eliminate port conflicts and deployment headaches
    
    ## AI Models Supported
    
    * OpenAI GPT-4o, GPT-3.5 Turbo
    * Anthropic Claude 3.5 Sonnet
    * Google Gemini Pro
    * Hugging Face Transformers
    * OpenRouter (access to 100+ models)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "Zenith Coder Team",
        "email": "support@zenithcoder.dev",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "message": "🚀 Welcome to Zenith Coder API",
        "description": "AI-Powered Development Platform for Modern Vibecoders",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational",
        "features": [
            "Project Organization & Cleanup",
            "AI-Powered Documentation Generation",
            "ADHD-Friendly Task Management", 
            "Monetization Strategy Analysis",
            "Automated Deployment Management"
        ]
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for monitoring and load balancers."""
    try:
        # Check database connection
        from src.core.database import database
        await database.fetch_one("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"
    
    # Check AI Orchestrator
    ai_status = "healthy" if hasattr(app.state, 'ai_orchestrator') else "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" and ai_status == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "timestamp": "2025-01-08T10:00:00Z",
        "version": "1.0.0",
        "services": {
            "database": db_status,
            "ai_orchestrator": ai_status,
        },
        "uptime": "operational"
    }


@app.exception_handler(ZenithException)
async def zenith_exception_handler(request, exc: ZenithException):
    """Handle custom Zenith exceptions."""
    logger.error(f"Zenith exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP_ERROR",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. Please try again later.",
            "details": str(exc) if settings.DEBUG else None
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )

