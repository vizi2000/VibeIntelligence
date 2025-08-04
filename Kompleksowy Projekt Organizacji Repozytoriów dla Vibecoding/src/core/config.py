"""
Zenith Coder Configuration Management

This module handles all application configuration using Pydantic Settings.
It loads configuration from environment variables and provides type-safe access.
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseSettings, validator, Field
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # =============================================================================
    # APPLICATION SETTINGS
    # =============================================================================
    APP_NAME: str = "Zenith Coder"
    VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    
    # =============================================================================
    # SERVER SETTINGS
    # =============================================================================
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"],
        env="ALLOWED_HOSTS"
    )
    
    # =============================================================================
    # DATABASE SETTINGS
    # =============================================================================
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=30, env="DATABASE_MAX_OVERFLOW")
    
    # =============================================================================
    # REDIS SETTINGS
    # =============================================================================
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")
    
    # =============================================================================
    # AI API KEYS
    # =============================================================================
    OPENAI_API_KEY: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    CLAUDE_API_KEY: Optional[str] = Field(default=None, env="CLAUDE_API_KEY")
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, env="OPENROUTER_API_KEY")
    HUGGINGFACE_API_TOKEN: Optional[str] = Field(default=None, env="HUGGINGFACE_API_TOKEN")
    
    # =============================================================================
    # AI MODEL PREFERENCES
    # =============================================================================
    DEFAULT_CODE_MODEL: str = Field(default="mistralai/mistral-7b-instruct:free", env="DEFAULT_CODE_MODEL")
    DEFAULT_ANALYSIS_MODEL: str = Field(default="google/gemma-7b-it:free", env="DEFAULT_ANALYSIS_MODEL")
    DEFAULT_DOCS_MODEL: str = Field(default="mistralai/mistral-7b-instruct:free", env="DEFAULT_DOCS_MODEL")
    ENABLE_LOCAL_MODELS: bool = Field(default=True, env="ENABLE_LOCAL_MODELS")
    
    # =============================================================================
    # EXTERNAL INTEGRATIONS
    # =============================================================================
    GITHUB_TOKEN: Optional[str] = Field(default=None, env="GITHUB_TOKEN")
    DUCKDNS_TOKEN: Optional[str] = Field(default=None, env="DUCKDNS_TOKEN")
    DUCKDNS_DOMAIN: Optional[str] = Field(default=None, env="DUCKDNS_DOMAIN")
    
    # =============================================================================
    # FEATURE FLAGS
    # =============================================================================
    ENABLE_EXPERIMENTAL_FEATURES: bool = Field(default=False, env="ENABLE_EXPERIMENTAL_FEATURES")
    ENABLE_TELEMETRY: bool = Field(default=True, env="ENABLE_TELEMETRY")
    ENABLE_AUTO_DOCS: bool = Field(default=True, env="ENABLE_AUTO_DOCS")
    ENABLE_FREELANCE_FINDER: bool = Field(default=True, env="ENABLE_FREELANCE_FINDER")
    
    # Vibecoding Features (v4.0)
    ENABLE_VIBECODING: bool = Field(default=True, env="ENABLE_VIBECODING")
    ENABLE_ECO_SCORING: bool = Field(default=True, env="ENABLE_ECO_SCORING")
    ENABLE_DEI_FEATURES: bool = Field(default=True, env="ENABLE_DEI_FEATURES")
    ENABLE_WELLBEING_TRACKING: bool = Field(default=True, env="ENABLE_WELLBEING_TRACKING")
    ENABLE_QUANTUM_IDEAS: bool = Field(default=True, env="ENABLE_QUANTUM_IDEAS")
    ENABLE_NEURAL_COMPANION: bool = Field(default=True, env="ENABLE_NEURAL_COMPANION")
    
    # =============================================================================
    # PERFORMANCE SETTINGS
    # =============================================================================
    MAX_CONCURRENT_AI_REQUESTS: int = Field(default=5, env="MAX_CONCURRENT_AI_REQUESTS")
    AI_REQUEST_TIMEOUT: int = Field(default=60, env="AI_REQUEST_TIMEOUT")
    RATE_LIMIT_PER_MINUTE: int = Field(default=100, env="RATE_LIMIT_PER_MINUTE")
    
    # =============================================================================
    # SECURITY SETTINGS
    # =============================================================================
    ENABLE_API_KEY_AUTH: bool = Field(default=False, env="ENABLE_API_KEY_AUTH")
    API_KEY: Optional[str] = Field(default=None, env="API_KEY")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # =============================================================================
    # LOGGING SETTINGS
    # =============================================================================
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # =============================================================================
    # PATHS AND DIRECTORIES
    # =============================================================================
    PROJECT_ROOT: str = Field(default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    UPLOAD_DIR: str = Field(default="uploads", env="UPLOAD_DIR")
    TEMP_DIR: str = Field(default="temp", env="TEMP_DIR")
    LOGS_DIR: str = Field(default="logs", env="LOGS_DIR")
    
    # =============================================================================
    # VIBECODING SETTINGS (v4.0)
    # =============================================================================
    VIBE_FLOW_THRESHOLD: int = Field(default=80, env="VIBE_FLOW_THRESHOLD")
    ECO_SCORE_TARGET: int = Field(default=90, env="ECO_SCORE_TARGET")
    DEI_ACCESSIBILITY_TARGET: int = Field(default=95, env="DEI_ACCESSIBILITY_TARGET")
    WELLBEING_BREAK_INTERVAL: int = Field(default=1800, env="WELLBEING_BREAK_INTERVAL")  # 30 minutes
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v):
        """Parse allowed hosts from string or list."""
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL (for Alembic)."""
        return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"
    
    def get_ai_model_config(self) -> Dict[str, Any]:
        """Get AI model configuration."""
        return {
            "code_generation": self.DEFAULT_CODE_MODEL,
            "analysis": self.DEFAULT_ANALYSIS_MODEL,
            "documentation": self.DEFAULT_DOCS_MODEL,
            "enable_local": self.ENABLE_LOCAL_MODELS,
            "timeout": self.AI_REQUEST_TIMEOUT,
            "max_concurrent": self.MAX_CONCURRENT_AI_REQUESTS
        }
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers based on API keys."""
        providers = []
        if self.OPENAI_API_KEY:
            providers.append("openai")
        if self.CLAUDE_API_KEY:
            providers.append("anthropic")
        if self.GEMINI_API_KEY:
            providers.append("google")
        if self.OPENROUTER_API_KEY:
            providers.append("openrouter")
        if self.HUGGINGFACE_API_TOKEN:
            providers.append("huggingface")
        return providers
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Create global settings instance
settings = Settings()

# Validate critical settings
if not settings.SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Log configuration on startup
if settings.DEBUG:
    print(f"🔧 Zenith Coder Configuration:")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Debug Mode: {settings.DEBUG}")
    print(f"   Available AI Providers: {settings.get_available_providers()}")
    print(f"   Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'configured'}")
    print(f"   Redis: {settings.REDIS_URL}")
    print(f"   CORS Origins: {settings.CORS_ORIGINS}")

