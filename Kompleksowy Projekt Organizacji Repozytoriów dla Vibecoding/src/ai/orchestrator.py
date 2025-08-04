"""
AI Orchestrator
Following Directive 8: Multi-provider AI orchestration
Manages AI providers with smart routing and vibecoding features
"""

import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from enum import Enum
import asyncio
import random

from .providers import BaseAIProvider, OpenRouterProvider, HuggingFaceProvider
from ..core.exceptions import AIProviderException
from ..core.config import settings

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of AI tasks for smart routing"""
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    DOCUMENTATION = "documentation"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    ECO_SCORING = "eco_scoring"
    IDEA_GENERATION = "idea_generation"
    SUMMARIZATION = "summarization"
    GENERAL_CHAT = "general_chat"


class AIOrchestrator:
    """
    Orchestrates multiple AI providers with smart routing
    Implements vibecoding principles with fallback and load balancing
    """
    
    def __init__(self):
        self.providers: Dict[str, BaseAIProvider] = {}
        self.provider_health: Dict[str, bool] = {}
        self.task_routing: Dict[TaskType, List[str]] = {
            TaskType.CODE_GENERATION: ["openrouter", "huggingface"],
            TaskType.CODE_ANALYSIS: ["openrouter", "huggingface"],
            TaskType.DOCUMENTATION: ["openrouter", "huggingface"],
            TaskType.SENTIMENT_ANALYSIS: ["huggingface"],
            TaskType.ECO_SCORING: ["huggingface"],
            TaskType.IDEA_GENERATION: ["openrouter"],
            TaskType.SUMMARIZATION: ["huggingface", "openrouter"],
            TaskType.GENERAL_CHAT: ["openrouter", "huggingface"]
        }
        self._initialized = False
        
    async def initialize(self) -> None:
        """Initialize all available AI providers"""
        logger.info("🚀 Initializing AI Orchestrator with vibecoding...")
        
        # Initialize OpenRouter if available
        if settings.OPENROUTER_API_KEY:
            try:
                provider = OpenRouterProvider(settings.OPENROUTER_API_KEY)
                await provider.initialize()
                self.providers["openrouter"] = provider
                self.provider_health["openrouter"] = True
                logger.info("✅ OpenRouter provider ready!")
            except Exception as e:
                logger.error(f"❌ OpenRouter initialization failed: {e}")
                self.provider_health["openrouter"] = False
        
        # Initialize HuggingFace if available
        if settings.HUGGINGFACE_API_TOKEN:
            try:
                provider = HuggingFaceProvider(settings.HUGGINGFACE_API_TOKEN)
                await provider.initialize()
                self.providers["huggingface"] = provider
                self.provider_health["huggingface"] = True
                logger.info("✅ HuggingFace provider ready!")
            except Exception as e:
                logger.error(f"❌ HuggingFace initialization failed: {e}")
                self.provider_health["huggingface"] = False
        
        if not self.providers:
            raise AIProviderException("Orchestrator", "No AI providers available!")
        
        self._initialized = True
        logger.info(f"🎉 AI Orchestrator initialized with {len(self.providers)} providers!")
        
        # Start health monitoring
        asyncio.create_task(self._monitor_health())
    
    async def generate(
        self,
        prompt: str,
        task_type: TaskType = TaskType.GENERAL_CHAT,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        prefer_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response with smart routing
        
        Args:
            prompt: The input prompt
            task_type: Type of task for routing
            model: Specific model to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            context: Additional context
            stream: Whether to stream response
            prefer_provider: Preferred provider name
        """
        
        if not self._initialized:
            raise AIProviderException("Orchestrator", "Not initialized")
        
        # Get suitable providers for this task
        suitable_providers = self._get_suitable_providers(task_type, prefer_provider)
        
        if not suitable_providers:
            raise AIProviderException("Orchestrator", f"No healthy providers for {task_type.value}")
        
        # Try providers in order with fallback
        last_error = None
        for provider_name in suitable_providers:
            provider = self.providers.get(provider_name)
            if not provider:
                continue
                
            try:
                logger.info(f"🤖 Using {provider_name} for {task_type.value}")
                
                if stream:
                    # Return generator for streaming
                    return {
                        "provider": provider_name,
                        "stream": provider.stream_response(
                            prompt=prompt,
                            model=model,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            context=context
                        )
                    }
                else:
                    # Generate response
                    response = await provider.generate_response(
                        prompt=prompt,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        context=context,
                        stream=False
                    )
                    response["provider"] = provider_name
                    return response
                    
            except Exception as e:
                logger.warning(f"⚠️ {provider_name} failed: {e}")
                last_error = e
                self.provider_health[provider_name] = False
                continue
        
        # All providers failed
        raise AIProviderException(
            "Orchestrator",
            f"All providers failed. Last error: {last_error}"
        )
    
    async def analyze_vibe(self, text: str) -> Dict[str, Any]:
        """
        Analyze text vibe using specialized models (Directive 18)
        Returns sentiment, emotion, and vibe score
        """
        try:
            # Prefer HuggingFace for emotion analysis
            if "huggingface" in self.providers and self.provider_health.get("huggingface", False):
                provider = self.providers["huggingface"]
                vibe_score = await provider._analyze_vibe(text)
                
                return {
                    "vibe_score": vibe_score,
                    "vibe_emoji": self._get_vibe_emoji(vibe_score),
                    "provider": "huggingface"
                }
            
            # Fallback to basic analysis
            return {
                "vibe_score": 5,
                "vibe_emoji": "😊",
                "provider": "fallback"
            }
            
        except Exception as e:
            logger.error(f"❌ Vibe analysis failed: {e}")
            return {"vibe_score": 5, "vibe_emoji": "😐", "error": str(e)}
    
    async def get_eco_score(self, code: str) -> Dict[str, Any]:
        """
        Get eco-score for code (Directive 17)
        Analyzes efficiency and sustainability
        """
        try:
            # Prefer HuggingFace for eco analysis
            if "huggingface" in self.providers and self.provider_health.get("huggingface", False):
                provider = self.providers["huggingface"]
                eco_metrics = await provider.analyze_code_eco_impact(code)
                return eco_metrics
            
            # Fallback to simple analysis
            return {
                "eco_score": 75,
                "lines_of_code": len(code.split('\n')),
                "optimization_suggestions": ["Consider using more efficient algorithms"],
                "provider": "fallback"
            }
            
        except Exception as e:
            logger.error(f"❌ Eco-score analysis failed: {e}")
            return {"eco_score": 50, "error": str(e)}
    
    async def get_quantum_idea(self) -> str:
        """
        Get a quantum-inspired wild idea (Directive 8 v4.0)
        Uses creative models with high temperature
        """
        try:
            # Prefer OpenRouter for creative tasks
            if "openrouter" in self.providers and self.provider_health.get("openrouter", False):
                provider = self.providers["openrouter"]
                return await provider.get_quantum_idea()
            
            # Fallback to local quantum generation
            ideas = [
                "🌈 Code that adapts its complexity based on developer's caffeine levels",
                "🎭 Functions that change behavior based on the phase of the moon",
                "🌿 Version control that grows like a digital garden",
                "🎵 Debugging through musical patterns in code rhythm",
                "🔮 AI that predicts bugs before you write them"
            ]
            return random.choice(ideas)
            
        except Exception as e:
            logger.error(f"❌ Quantum idea generation failed: {e}")
            return "🌟 Even errors can spark quantum creativity!"
    
    async def summarize_for_adhd(self, text: str) -> str:
        """
        Create ADHD-friendly summary (Directive 18)
        Uses bullet points and highlights
        """
        try:
            response = await self.generate(
                prompt=f"Summarize this in 3-5 bullet points for someone with ADHD: {text}",
                task_type=TaskType.SUMMARIZATION,
                max_tokens=150,
                temperature=0.5
            )
            return response["content"]
        except Exception:
            # Fallback to simple extraction
            sentences = text.split(". ")[:3]
            return "✨ Quick Points:\n" + "\n".join(f"• {s}" for s in sentences)
    
    def _get_suitable_providers(
        self,
        task_type: TaskType,
        prefer_provider: Optional[str] = None
    ) -> List[str]:
        """Get ordered list of suitable providers for a task"""
        
        # Start with task-specific routing
        suitable = self.task_routing.get(task_type, list(self.providers.keys()))
        
        # Filter by health
        healthy = [p for p in suitable if self.provider_health.get(p, False)]
        
        # Apply preference if specified
        if prefer_provider and prefer_provider in healthy:
            healthy.remove(prefer_provider)
            healthy.insert(0, prefer_provider)
        
        return healthy
    
    def _get_vibe_emoji(self, vibe_score: int) -> str:
        """Convert vibe score to emoji"""
        if vibe_score >= 9:
            return "🤩"
        elif vibe_score >= 7:
            return "😄"
        elif vibe_score >= 5:
            return "😊"
        elif vibe_score >= 3:
            return "😐"
        else:
            return "😔"
    
    async def _monitor_health(self) -> None:
        """Monitor provider health in background"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                for name, provider in self.providers.items():
                    try:
                        is_healthy = await provider.health_check()
                        self.provider_health[name] = is_healthy
                    except Exception:
                        self.provider_health[name] = False
                        
                # Log health status
                healthy_count = sum(1 for h in self.provider_health.values() if h)
                logger.info(
                    f"💓 Provider health: {healthy_count}/{len(self.providers)} healthy"
                )
                
            except Exception as e:
                logger.error(f"❌ Health monitoring error: {e}")
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics from all providers"""
        stats = {
            "providers": {},
            "total_tokens": 0,
            "total_cost": 0.0,
            "average_eco_score": 0
        }
        
        eco_scores = []
        for name, provider in self.providers.items():
            provider_stats = provider.get_usage_stats()
            stats["providers"][name] = provider_stats
            stats["total_tokens"] += provider_stats["total_tokens"]
            stats["total_cost"] += provider_stats["total_cost"]
            
            if "eco_score" in provider_stats:
                eco_scores.append(provider_stats["eco_score"])
        
        if eco_scores:
            stats["average_eco_score"] = sum(eco_scores) // len(eco_scores)
        
        stats["vibe_level"] = "high" if stats["average_eco_score"] > 80 else "medium"
        
        return stats
    
    async def cleanup(self) -> None:
        """Cleanup all providers gracefully"""
        logger.info("🧹 Cleaning up AI Orchestrator...")
        
        cleanup_tasks = []
        for provider in self.providers.values():
            cleanup_tasks.append(provider.cleanup())
        
        await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self.providers.clear()
        self.provider_health.clear()
        self._initialized = False
        
        logger.info("👋 AI Orchestrator shutdown complete!")


# Global orchestrator instance
orchestrator = AIOrchestrator()