"""
Zenith Coder Exception Hierarchy
Following Directive 4: Zero Trust & Directive 2: Code Quality
"""

from typing import Optional, Dict, Any
from fastapi import status


class ZenithException(Exception):
    """Base exception for all Zenith Coder exceptions"""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class ValidationException(ZenithException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(
            error_code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details
        )


class AuthenticationException(ZenithException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            error_code="AUTHENTICATION_ERROR",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED
        )


class AuthorizationException(ZenithException):
    """Raised when user lacks required permissions"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            error_code="AUTHORIZATION_ERROR",
            message=message,
            status_code=status.HTTP_403_FORBIDDEN
        )


class ResourceNotFoundException(ZenithException):
    """Raised when requested resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: Any):
        super().__init__(
            error_code="RESOURCE_NOT_FOUND",
            message=f"{resource_type} with id {resource_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource_type": resource_type, "resource_id": str(resource_id)}
        )


class AIProviderException(ZenithException):
    """Raised when AI provider operations fail"""
    
    def __init__(self, provider: str, message: str):
        super().__init__(
            error_code="AI_PROVIDER_ERROR",
            message=f"AI Provider {provider} error: {message}",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details={"provider": provider}
        )


class RateLimitException(ZenithException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, limit: int, window: str):
        super().__init__(
            error_code="RATE_LIMIT_EXCEEDED",
            message=f"Rate limit of {limit} requests per {window} exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={"limit": limit, "window": window}
        )


class DatabaseException(ZenithException):
    """Raised when database operations fail"""
    
    def __init__(self, operation: str, message: str):
        super().__init__(
            error_code="DATABASE_ERROR",
            message=f"Database {operation} failed: {message}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"operation": operation}
        )


class VibeException(ZenithException):
    """Raised when vibe-related operations fail (v4.0)"""
    
    def __init__(self, vibe_type: str, message: str):
        super().__init__(
            error_code="VIBE_ERROR",
            message=f"Vibe {vibe_type} error: {message}",
            status_code=status.HTTP_418_IM_A_TEAPOT,  # Fun status for vibe errors
            details={"vibe_type": vibe_type}
        )


class EcoScoreException(ZenithException):
    """Raised when eco-scoring fails (Directive 17)"""
    
    def __init__(self, score: float, threshold: float):
        super().__init__(
            error_code="ECO_SCORE_VIOLATION",
            message=f"Eco score {score} below threshold {threshold}",
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            details={"score": score, "threshold": threshold}
        )