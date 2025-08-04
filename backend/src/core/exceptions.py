"""
Custom exceptions for Zenith Coder
"""

class ZenithCoderException(Exception):
    """Base exception for all Zenith Coder errors"""
    pass

class AIProviderException(ZenithCoderException):
    """Exception raised by AI providers"""
    pass

class DatabaseException(ZenithCoderException):
    """Exception raised for database operations"""
    pass

class ValidationException(ZenithCoderException):
    """Exception raised for validation errors"""
    pass

class AuthenticationException(ZenithCoderException):
    """Exception raised for authentication errors"""
    pass

class ConfigurationException(ZenithCoderException):
    """Exception raised for configuration errors"""
    pass

class DeploymentException(ZenithCoderException):
    """Exception raised for deployment operations"""
    pass

class ScannerException(ZenithCoderException):
    """Exception raised for scanner operations"""
    pass

class MCPException(ZenithCoderException):
    """Exception raised for MCP integration errors"""
    pass

class VibeException(ZenithCoderException):
    """Exception raised when vibe is too low"""
    pass

class DocumentationException(ZenithCoderException):
    """Exception raised for documentation generation errors"""
    pass