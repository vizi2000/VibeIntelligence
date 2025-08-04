"""
AI Module Package
Following Directive 8: AI Integration and Orchestration
"""

from .orchestrator import AIOrchestrator, TaskType, orchestrator
from .providers import BaseAIProvider, OpenRouterProvider, HuggingFaceProvider

__all__ = [
    "AIOrchestrator",
    "TaskType",
    "orchestrator",
    "BaseAIProvider",
    "OpenRouterProvider",
    "HuggingFaceProvider"
]