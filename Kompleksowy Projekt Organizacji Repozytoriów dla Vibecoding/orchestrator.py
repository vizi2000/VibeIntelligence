"""
Zenith Coder AI Orchestrator

This is the central intelligence of Zenith Coder. It manages all AI agents,
routes requests to the best available models, and coordinates complex workflows
that require multiple AI capabilities.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from enum import Enum
import json
from datetime import datetime

from src.core.config import settings
from src.ai.providers.openai_provider import OpenAIProvider
from src.ai.providers.anthropic_provider import AnthropicProvider
from src.ai.providers.google_provider import GoogleProvider
from src.ai.providers.openrouter_provider import OpenRouterProvider
from src.ai.providers.huggingface_provider import HuggingFaceProvider
from src.ai.agents.documentation_agent import DocumentationAgent
from src.ai.agents.task_manager_agent import TaskManagerAgent
from src.ai.agents.monetization_agent import MonetizationAgent
from src.ai.agents.skill_analyst_agent import SkillAnalystAgent
from src.core.exceptions import ZenithException

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of AI tasks that can be orchestrated."""
    CODE_GENERATION = "code_generation"
    CODE_ANALYSIS = "code_analysis"
    DOCUMENTATION = "documentation"
    TASK_MANAGEMENT = "task_management"
    MONETIZATION_ANALYSIS = "monetization_analysis"
    SKILL_ANALYSIS = "skill_analysis"
    GENERAL_REASONING = "general_reasoning"
    SUMMARIZATION = "summarization"
    CLASSIFICATION = "classification"


class AIOrchestrator:
    """
    Central AI orchestrator that manages all AI providers and agents.
    
    This class implements the strategy pattern to dynamically select
    the best AI model for each task based on capabilities, cost, and availability.
    """
    
    def __init__(self):
        self.providers: Dict[str, Any] = {}
        self.agents: Dict[str, Any] = {}
        self.model_routing_rules: Dict[TaskType, List[str]] = {}
        self.request_queue = asyncio.Queue()
        self.active_requests: Dict[str, Any] = {}
        self.is_initialized = False
        
    async def initialize(self) -> None:
        """Initialize all AI providers and agents."""
        try:
            logger.info("🤖 Initializing AI Orchestrator...")
            
            # Initialize providers based on available API keys
            await self._initialize_providers()
            
            # Initialize specialized agents
            await self._initialize_agents()
            
            # Setup routing rules
            self._setup_routing_rules()
            
            # Start request processor
            asyncio.create_task(self._process_requests())
            
            self.is_initialized = True
            logger.info(f"✅ AI Orchestrator initialized with {len(self.providers)} providers and {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI Orchestrator: {e}")
            raise ZenithException(
                error_code="AI_INIT_FAILED",
                message="Failed to initialize AI Orchestrator",
                details=str(e)
            )
    
    async def _initialize_providers(self) -> None:
        """Initialize AI providers based on available API keys."""
        
        # OpenAI Provider
        if settings.OPENAI_API_KEY:
            try:
                self.providers["openai"] = OpenAIProvider(settings.OPENAI_API_KEY)
                await self.providers["openai"].initialize()
                logger.info("✅ OpenAI provider initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize OpenAI provider: {e}")
        
        # Anthropic Provider (Claude)
        if settings.CLAUDE_API_KEY:
            try:
                self.providers["anthropic"] = AnthropicProvider(settings.CLAUDE_API_KEY)
                await self.providers["anthropic"].initialize()
                logger.info("✅ Anthropic provider initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Anthropic provider: {e}")
        
        # Google Provider (Gemini)
        if settings.GEMINI_API_KEY:
            try:
                self.providers["google"] = GoogleProvider(settings.GEMINI_API_KEY)
                await self.providers["google"].initialize()
                logger.info("✅ Google provider initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Google provider: {e}")
        
        # OpenRouter Provider
        if settings.OPENROUTER_API_KEY:
            try:
                self.providers["openrouter"] = OpenRouterProvider(settings.OPENROUTER_API_KEY)
                await self.providers["openrouter"].initialize()
                logger.info("✅ OpenRouter provider initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize OpenRouter provider: {e}")
        
        # Hugging Face Provider
        if settings.HUGGINGFACE_API_TOKEN and settings.ENABLE_LOCAL_MODELS:
            try:
                self.providers["huggingface"] = HuggingFaceProvider(settings.HUGGINGFACE_API_TOKEN)
                await self.providers["huggingface"].initialize()
                logger.info("✅ Hugging Face provider initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize Hugging Face provider: {e}")
        
        if not self.providers:
            raise ZenithException(
                error_code="NO_AI_PROVIDERS",
                message="No AI providers could be initialized. Please check your API keys.",
                details="At least one AI provider is required for Zenith Coder to function."
            )
    
    async def _initialize_agents(self) -> None:
        """Initialize specialized AI agents."""
        
        # Documentation Agent
        self.agents["documentation"] = DocumentationAgent(self)
        
        # Task Manager Agent
        self.agents["task_manager"] = TaskManagerAgent(self)
        
        # Monetization Agent
        self.agents["monetization"] = MonetizationAgent(self)
        
        # Skill Analyst Agent
        self.agents["skill_analyst"] = SkillAnalystAgent(self)
        
        logger.info(f"✅ Initialized {len(self.agents)} specialized agents")
    
    def _setup_routing_rules(self) -> None:
        """Setup routing rules for different task types."""
        
        # Preferred models for each task type (in order of preference)
        self.model_routing_rules = {
            TaskType.CODE_GENERATION: [
                "anthropic/claude-3-5-sonnet-20241022",  # Best for code
                "openai/gpt-4o",
                "google/gemini-pro"
            ],
            TaskType.CODE_ANALYSIS: [
                "anthropic/claude-3-5-sonnet-20241022",
                "openai/gpt-4o",
                "google/gemini-pro"
            ],
            TaskType.DOCUMENTATION: [
                "anthropic/claude-3-5-sonnet-20241022",
                "openai/gpt-4o",
                "google/gemini-pro"
            ],
            TaskType.GENERAL_REASONING: [
                "openai/gpt-4o",  # Best for reasoning
                "anthropic/claude-3-5-sonnet-20241022",
                "google/gemini-pro"
            ],
            TaskType.SUMMARIZATION: [
                "openai/gpt-4o-mini",  # Cost-effective for summarization
                "anthropic/claude-3-haiku-20240307",
                "google/gemini-pro"
            ],
            TaskType.CLASSIFICATION: [
                "huggingface/local",  # Use local models for classification
                "openai/gpt-4o-mini",
                "google/gemini-pro"
            ]
        }
    
    async def execute_task(
        self,
        task_type: TaskType,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        model_override: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute an AI task using the best available model.
        
        Args:
            task_type: Type of task to execute
            prompt: The prompt to send to the AI
            context: Additional context for the task
            model_override: Override automatic model selection
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Dict containing the response and metadata
        """
        if not self.is_initialized:
            raise ZenithException(
                error_code="AI_NOT_INITIALIZED",
                message="AI Orchestrator not initialized"
            )
        
        # Generate unique request ID
        request_id = f"{task_type.value}_{datetime.now().timestamp()}"
        
        try:
            # Select the best model for this task
            selected_model = model_override or await self._select_best_model(task_type)
            
            # Get the appropriate provider
            provider = await self._get_provider_for_model(selected_model)
            
            # Prepare the request
            request_data = {
                "id": request_id,
                "task_type": task_type.value,
                "model": selected_model,
                "prompt": prompt,
                "context": context or {},
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timestamp": datetime.now().isoformat()
            }
            
            # Track active request
            self.active_requests[request_id] = request_data
            
            logger.info(f"🎯 Executing {task_type.value} task with {selected_model}")
            
            # Execute the request
            response = await provider.generate_response(
                prompt=prompt,
                model=selected_model,
                temperature=temperature,
                max_tokens=max_tokens,
                context=context
            )
            
            # Clean up
            del self.active_requests[request_id]
            
            return {
                "request_id": request_id,
                "task_type": task_type.value,
                "model_used": selected_model,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            # Clean up on error
            if request_id in self.active_requests:
                del self.active_requests[request_id]
            
            logger.error(f"❌ Task execution failed: {e}")
            
            return {
                "request_id": request_id,
                "task_type": task_type.value,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    async def _select_best_model(self, task_type: TaskType) -> str:
        """Select the best available model for a task type."""
        
        # Get preferred models for this task type
        preferred_models = self.model_routing_rules.get(task_type, [])
        
        # Find the first available model
        for model in preferred_models:
            provider_name = model.split("/")[0] if "/" in model else model
            if provider_name in self.providers:
                # Check if provider is healthy
                provider = self.providers[provider_name]
                if await provider.health_check():
                    return model
        
        # Fallback to any available provider
        for provider_name, provider in self.providers.items():
            if await provider.health_check():
                return f"{provider_name}/default"
        
        raise ZenithException(
            error_code="NO_AVAILABLE_MODELS",
            message="No AI models are currently available"
        )
    
    async def _get_provider_for_model(self, model: str) -> Any:
        """Get the provider instance for a specific model."""
        provider_name = model.split("/")[0] if "/" in model else model
        
        if provider_name not in self.providers:
            raise ZenithException(
                error_code="PROVIDER_NOT_FOUND",
                message=f"Provider {provider_name} not available"
            )
        
        return self.providers[provider_name]
    
    async def _process_requests(self) -> None:
        """Background task to process queued requests."""
        while True:
            try:
                # Process any queued requests
                if not self.request_queue.empty():
                    request = await self.request_queue.get()
                    # Process request...
                    
                await asyncio.sleep(0.1)  # Small delay to prevent busy waiting
                
            except Exception as e:
                logger.error(f"Error in request processor: {e}")
                await asyncio.sleep(1)  # Longer delay on error
    
    async def get_status(self) -> Dict[str, Any]:
        """Get the current status of the AI Orchestrator."""
        provider_status = {}
        for name, provider in self.providers.items():
            try:
                is_healthy = await provider.health_check()
                provider_status[name] = {
                    "status": "healthy" if is_healthy else "unhealthy",
                    "model_count": len(getattr(provider, 'available_models', [])),
                }
            except Exception as e:
                provider_status[name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return {
            "initialized": self.is_initialized,
            "providers": provider_status,
            "agents": list(self.agents.keys()),
            "active_requests": len(self.active_requests),
            "queue_size": self.request_queue.qsize()
        }
    
    async def cleanup(self) -> None:
        """Cleanup resources."""
        logger.info("🧹 Cleaning up AI Orchestrator...")
        
        # Cleanup providers
        for provider in self.providers.values():
            if hasattr(provider, 'cleanup'):
                await provider.cleanup()
        
        # Clear active requests
        self.active_requests.clear()
        
        logger.info("✅ AI Orchestrator cleanup complete")

