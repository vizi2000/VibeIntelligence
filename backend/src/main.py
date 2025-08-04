"""
Zenith Coder - Main FastAPI Application
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from .api import projects, scanner, deployments, health
from .core.config import settings
from .core.database import engine, Base
from .mcp.integration import mcp_integration

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Zenith Coder API with Vibecoding v4.0...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize AI services if enabled
    if settings.enable_vibecoding:
        try:
            from .services.ai_service import ai_service
            await ai_service.initialize()
            print("✅ AI Services initialized!")
        except Exception as e:
            print(f"⚠️ AI Services unavailable: {e}")
    
    # Initialize MCP integration
    try:
        from .mcp.integration import mcp_integration
        await mcp_integration.initialize()
        print("✅ MCP Toolbox connected!")
    except Exception as e:
        print(f"⚠️ MCP integration unavailable: {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Zenith Coder API...")
    
    # Cleanup MCP
    try:
        await mcp_integration.cleanup()
    except Exception:
        pass

# Create FastAPI app
app = FastAPI(
    title="Zenith Coder API",
    description="AI-powered development platform for organizing and managing projects",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3100", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(scanner.router, prefix="/api/v1/scanner", tags=["scanner"])
app.include_router(deployments.router, prefix="/api/v1/deployments", tags=["deployments"])

# Include AI routes if vibecoding is enabled
if settings.enable_vibecoding:
    from .api import ai
    app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI Services"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Zenith Coder API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }