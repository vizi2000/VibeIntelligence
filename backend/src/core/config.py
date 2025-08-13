"""
Configuration settings for Zenith Coder
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "Zenith Coder"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API
    api_port: int = 8100
    api_host: str = "0.0.0.0"
    
    # Database
    database_url: str = "postgresql://zenith:zenith@localhost:5434/zenith_coder"
    
    # Redis
    redis_url: str = "redis://localhost:6381"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI Services
    openai_api_key: Optional[str] = None
    claude_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None  # Alias for compatibility
    huggingface_api_token: Optional[str] = None
    
    # AI Model Preferences
    default_code_model: str = "openrouter/horizon-beta"
    default_analysis_model: str = "openrouter/horizon-beta"
    default_docs_model: str = "openrouter/horizon-beta"
    enable_local_models: bool = True
    ENABLE_LOCAL_MODELS: bool = True  # Alias for compatibility
    
    # Performance Settings
    max_concurrent_ai_requests: int = 5
    ai_request_timeout: int = 60
    AI_REQUEST_TIMEOUT: int = 60  # Alias for compatibility
    
    # Vibecoding Settings
    enable_vibecoding: bool = True
    enable_eco_scoring: bool = True
    enable_dei_features: bool = True
    enable_wellbeing_tracking: bool = True
    enable_quantum_ideas: bool = True
    enable_neural_companion: bool = True
    vibe_flow_threshold: int = 80
    eco_score_target: int = 90
    
    # GitHub
    github_token: Optional[str] = None
    
    # File paths
    ai_projects_path: str = "/ai_projects"
    deployment_registry_path: str = "/ai_projects/DEPLOYMENT_REGISTRY.md"
    
    # Scanner settings
    scan_exclude_dirs: list = [
        "node_modules", ".git", "__pycache__", ".venv", "venv", 
        ".next", "build", "dist", "target", ".pytest_cache"
    ]
    scan_project_indicators: list = [
        "package.json", "requirements.txt", "setup.py", "Dockerfile",
        "docker-compose.yml", "pom.xml", "build.gradle", "Cargo.toml",
        "go.mod", "*.csproj", "*.sln"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"

# Create settings instance
settings = Settings()