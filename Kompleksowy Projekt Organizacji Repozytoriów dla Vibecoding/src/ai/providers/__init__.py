"""
AI Providers Package
Following Directive 8: AI Integration
"""

from .base_provider import BaseAIProvider
from .openrouter_provider import OpenRouterProvider
from .huggingface_provider import HuggingFaceProvider

__all__ = [
    "BaseAIProvider",
    "OpenRouterProvider", 
    "HuggingFaceProvider"
]