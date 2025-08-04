"""
Base AI Provider Interface
Following Directive 9: Software Architecture & System Design
Implements Strategy Pattern for AI providers
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, AsyncGenerator
import logging
from datetime import datetime

from ...core.exceptions import AIProviderException

logger = logging.getLogger(__name__)


class BaseAIProvider(ABC):
    """
    Abstract base class for all AI providers
    Follows SOLID principles and enables provider swapping
    """
    
    def __init__(self, api_key: str, provider_name: str):
        self.api_key = api_key
        self.provider_name = provider_name
        self.is_initialized = False
        self.available_models: List[str] = []
        self.total_tokens_used = 0
        self.total_cost = 0.0
        
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the provider and verify connectivity"""
        pass
    
    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate response from AI model
        
        Args:
            prompt: The input prompt
            model: Specific model to use (or None for default)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            context: Additional context for the request
            stream: Whether to stream the response
            
        Returns:
            Response dictionary with 'content', 'tokens_used', 'model_used'
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is healthy and responsive"""
        pass
    
    async def stream_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream response tokens as they're generated
        Default implementation converts non-streaming to streaming
        """
        response = await self.generate_response(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            context=context,
            stream=False
        )
        
        # Simulate streaming by yielding chunks
        content = response.get("content", "")
        chunk_size = 20  # Characters per chunk
        
        for i in range(0, len(content), chunk_size):
            yield content[i:i + chunk_size]
    
    def track_usage(self, tokens: int, cost: float) -> None:
        """Track token usage and costs for monitoring"""
        self.total_tokens_used += tokens
        self.total_cost += cost
        
        # Log usage for eco-scoring (Directive 17)
        logger.info(
            f"📊 {self.provider_name} usage: {tokens} tokens, ${cost:.4f}",
            extra={"eco_impact": tokens * 0.0001}  # Simplified eco calculation
        )
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics for vibe dashboard"""
        return {
            "provider": self.provider_name,
            "total_tokens": self.total_tokens_used,
            "total_cost": self.total_cost,
            "is_active": self.is_initialized,
            "models_available": len(self.available_models),
            "eco_score": self._calculate_eco_score()
        }
    
    def _calculate_eco_score(self) -> int:
        """
        Calculate eco-score based on usage (Directive 17)
        Lower token usage = higher eco score
        """
        if self.total_tokens_used == 0:
            return 100
        
        # Simple calculation: penalize high token usage
        base_score = 100
        penalty = min(50, self.total_tokens_used // 10000)
        
        return max(50, base_score - penalty)
    
    async def cleanup(self) -> None:
        """Cleanup resources when shutting down"""
        logger.info(f"🧹 Cleaning up {self.provider_name} provider")
        self.is_initialized = False