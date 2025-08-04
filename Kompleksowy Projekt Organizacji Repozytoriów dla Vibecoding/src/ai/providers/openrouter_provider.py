"""
OpenRouter AI Provider
Following Directive 8: AI Integration with cost optimization
Uses free models to minimize costs while maintaining quality
"""

import logging
from typing import Any, Dict, List, Optional, AsyncGenerator
import httpx
import json

from .base_provider import BaseAIProvider
from ...core.exceptions import AIProviderException
from ...core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterProvider(BaseAIProvider):
    """
    OpenRouter provider implementation focusing on free models
    Implements vibecoding principles with joyful error messages
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    # Free models available on OpenRouter
    FREE_MODELS = [
        "openrouter/horizon-beta",  # Advanced free model - prioritized
        "mistralai/mistral-7b-instruct:free",
        "google/gemma-7b-it:free",
        "huggingfaceh4/zephyr-7b-beta:free",
        "undi95/toppy-m-7b:free",
        "openchat/openchat-7b:free",
        "mythomist/mythomax-l2-7b:free",
        "nousresearch/nous-capybara-7b:free"
    ]
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "OpenRouter")
        self.available_models = self.FREE_MODELS.copy()
        self.client: Optional[httpx.AsyncClient] = None
        
    async def initialize(self) -> None:
        """Initialize OpenRouter provider with free models"""
        try:
            self.client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "https://zenithcoder.ai",
                    "X-Title": "Zenith Coder"
                },
                timeout=settings.AI_REQUEST_TIMEOUT
            )
            
            # Test connection with a simple request
            response = await self.client.get("/models")
            if response.status_code == 200:
                self.is_initialized = True
                logger.info("✅ OpenRouter provider initialized with free models!")
                logger.info(f"🎉 Available free models: {', '.join(self.FREE_MODELS[:3])}...")
            else:
                raise AIProviderException("OpenRouter", f"Failed to initialize: {response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ OpenRouter initialization failed: {e}")
            raise AIProviderException("OpenRouter", str(e))
    
    async def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate response using free models"""
        
        if not self.is_initialized:
            raise AIProviderException("OpenRouter", "Provider not initialized")
        
        # Use default free model if none specified
        if not model:
            model = settings.DEFAULT_CODE_MODEL
        
        # Ensure we're using a free model
        if model not in self.FREE_MODELS:
            logger.warning(f"⚠️ Model {model} is not free, switching to {self.FREE_MODELS[0]}")
            model = self.FREE_MODELS[0]
        
        try:
            # Prepare request
            request_data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant focused on vibecoding - making coding joyful and sustainable."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                request_data["max_tokens"] = max_tokens
                
            # Add context as system message if provided
            if context:
                context_msg = f"Context: {json.dumps(context)}"
                request_data["messages"].insert(1, {"role": "system", "content": context_msg})
            
            # Make request
            response = await self.client.post("/chat/completions", json=request_data)
            
            if response.status_code != 200:
                error_data = response.json()
                raise AIProviderException("OpenRouter", f"API error: {error_data.get('error', {}).get('message', 'Unknown error')}")
            
            # Parse response
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            
            # Track usage (free models = $0 cost!)
            self.track_usage(tokens_used, 0.0)
            
            return {
                "content": content,
                "tokens_used": tokens_used,
                "model_used": model,
                "cost": 0.0,
                "eco_score": 100  # Free models are eco-friendly!
            }
            
        except httpx.TimeoutException:
            raise AIProviderException("OpenRouter", "Request timeout - try a shorter prompt! 🕐")
        except Exception as e:
            logger.error(f"❌ OpenRouter error: {e}")
            raise AIProviderException("OpenRouter", str(e))
    
    async def stream_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response for better UX (Directive 5)"""
        
        if not self.is_initialized:
            raise AIProviderException("OpenRouter", "Provider not initialized")
        
        model = model or self.FREE_MODELS[0]
        
        try:
            request_data = {
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a vibecoding assistant spreading joy through code!"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "stream": True
            }
            
            if max_tokens:
                request_data["max_tokens"] = max_tokens
            
            # Stream the response
            async with self.client.stream("POST", "/chat/completions", json=request_data) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            content = data["choices"][0]["delta"].get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            logger.error(f"❌ Streaming error: {e}")
            yield f"\n\n[Error: {str(e)}]"
    
    async def health_check(self) -> bool:
        """Check provider health with positive vibes"""
        try:
            if not self.client:
                return False
                
            response = await self.client.get("/models", timeout=5.0)
            is_healthy = response.status_code == 200
            
            if is_healthy:
                logger.info("💚 OpenRouter is healthy and ready to vibe!")
            else:
                logger.warning("💛 OpenRouter needs some TLC")
                
            return is_healthy
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    async def get_quantum_idea(self) -> str:
        """
        Generate quantum-inspired wild ideas (Directive 8 v4.0)
        Uses free models for maximum creativity with zero cost
        """
        quantum_prompts = [
            "Generate a wild, innovative coding idea that combines blockchain and biofeedback",
            "What's a crazy but potentially genius way to visualize code in AR?",
            "Imagine a programming language designed for meditation - describe it",
            "How could we use sound waves to debug code?"
        ]
        
        import random
        prompt = random.choice(quantum_prompts)
        
        try:
            response = await self.generate_response(
                prompt=prompt,
                temperature=0.9,  # High temperature for creativity
                model=self.FREE_MODELS[0]
            )
            return f"🌈 Quantum Idea: {response['content']}"
        except:
            # Fallback to local quantum generation
            ideas = [
                "Code that changes behavior based on developer's mood",
                "AI pair programmer that speaks only in haikus",
                "Version control system based on plant growth patterns",
                "Debugging through interpretive dance with motion capture"
            ]
            return f"🌈 Quantum Idea: {random.choice(ideas)}"
    
    async def cleanup(self) -> None:
        """Cleanup with gratitude"""
        if self.client:
            await self.client.aclose()
        await super().cleanup()
        logger.info("🙏 Thank you for the free AI vibes, OpenRouter!")