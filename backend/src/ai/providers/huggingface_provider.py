"""
HuggingFace AI Provider
Following Directive 8: AI Integration with local model support
Enables eco-friendly local inference and specialized models
"""

import logging
from typing import Any, Dict, List, Optional, AsyncGenerator
import httpx
import json
from transformers import pipeline, AutoTokenizer
import torch
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .base_provider import BaseAIProvider
from ...core.exceptions import AIProviderException
from ...core.config import settings

logger = logging.getLogger(__name__)


class HuggingFaceProvider(BaseAIProvider):
    """
    HuggingFace provider for local and cloud model inference
    Supports vibecoding with emotion detection and eco-scoring
    """
    
    API_URL = "https://api-inference.huggingface.co"
    
    # Free/efficient models for various tasks
    RECOMMENDED_MODELS = {
        "text-generation": "microsoft/phi-2",
        "sentiment-analysis": "nlptown/bert-base-multilingual-uncased-sentiment",
        "code-generation": "Salesforce/codegen-350M-mono",
        "summarization": "sshleifer/distilbart-cnn-12-6",
        "emotion": "j-hartmann/emotion-english-distilroberta-base",
        "toxicity": "unitary/toxic-bert",
        "eco-impact": "climatebert/distilroberta-base-climate-detector"
    }
    
    def __init__(self, api_key: str):
        super().__init__(api_key, "HuggingFace")
        self.client: Optional[httpx.AsyncClient] = None
        self.local_pipelines: Dict[str, Any] = {}
        self.executor = ThreadPoolExecutor(max_workers=2)
        
    async def initialize(self) -> None:
        """Initialize HuggingFace provider with local and cloud support"""
        try:
            # Setup HTTP client for API inference
            self.client = httpx.AsyncClient(
                base_url=self.API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=settings.AI_REQUEST_TIMEOUT
            )
            
            # Test API connection
            test_response = await self.client.post(
                "/models/gpt2",
                json={"inputs": "Hello"}
            )
            
            if test_response.status_code in [200, 503]:  # 503 = model loading
                self.is_initialized = True
                logger.info("✅ HuggingFace provider initialized!")
                
                # Initialize local models if enabled
                if settings.ENABLE_LOCAL_MODELS:
                    await self._initialize_local_models()
            else:
                raise AIProviderException("HuggingFace", f"API test failed: {test_response.status_code}")
                
        except Exception as e:
            logger.error(f"❌ HuggingFace initialization failed: {e}")
            raise AIProviderException("HuggingFace", str(e))
    
    async def _initialize_local_models(self) -> None:
        """Initialize lightweight local models for vibe analysis"""
        try:
            logger.info("🤖 Loading local models for vibecoding...")
            
            # Load emotion detection model (small, fast)
            loop = asyncio.get_event_loop()
            self.local_pipelines["emotion"] = await loop.run_in_executor(
                self.executor,
                pipeline,
                "text-classification",
                "j-hartmann/emotion-english-distilroberta-base"
            )
            
            logger.info("💚 Local emotion model loaded for vibe detection!")
            
        except Exception as e:
            logger.warning(f"⚠️ Local model loading failed (will use API): {e}")
    
    async def generate_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate response using HuggingFace models"""
        
        if not self.is_initialized:
            raise AIProviderException("HuggingFace", "Provider not initialized")
        
        # Default to efficient model
        if not model:
            model = self.RECOMMENDED_MODELS.get("text-generation", "gpt2")
        
        try:
            # Prepare request
            request_data = {
                "inputs": prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens or 150,
                    "return_full_text": False
                }
            }
            
            # Add context if provided
            if context:
                request_data["inputs"] = f"{json.dumps(context)}\n\n{prompt}"
            
            # Make API request
            response = await self.client.post(
                f"/models/{model}",
                json=request_data
            )
            
            # Handle model loading
            if response.status_code == 503:
                # Model is loading, wait and retry
                await asyncio.sleep(5)
                response = await self.client.post(
                    f"/models/{model}",
                    json=request_data
                )
            
            if response.status_code != 200:
                raise AIProviderException("HuggingFace", f"API error: {response.status_code}")
            
            # Parse response
            data = await response.json()
            
            # Extract content based on response format
            if isinstance(data, list) and len(data) > 0:
                content = data[0].get("generated_text", "")
            else:
                content = str(data)
            
            # Calculate eco-friendly metrics
            tokens_used = len(content.split())
            eco_score = 95 if "local" in model else 85  # Local models are more eco-friendly
            
            # Analyze vibe if emotion model is loaded
            vibe_score = await self._analyze_vibe(content)
            
            self.track_usage(tokens_used, 0.0)  # HF is free!
            
            return {
                "content": content,
                "tokens_used": tokens_used,
                "model_used": model,
                "cost": 0.0,
                "eco_score": eco_score,
                "vibe_score": vibe_score
            }
            
        except Exception as e:
            logger.error(f"❌ HuggingFace error: {e}")
            raise AIProviderException("HuggingFace", str(e))
    
    async def _analyze_vibe(self, text: str) -> int:
        """Analyze emotional vibe of text (1-10 scale)"""
        try:
            if "emotion" in self.local_pipelines:
                # Use local model
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    self.local_pipelines["emotion"],
                    text[:512]  # Limit text length
                )
                
                # Map emotions to vibe scores
                emotion_map = {
                    "joy": 10, "surprise": 8, "love": 9,
                    "optimism": 8, "neutral": 5, "confusion": 4,
                    "fear": 3, "sadness": 2, "anger": 1
                }
                
                emotion = result[0]["label"].lower()
                return emotion_map.get(emotion, 5)
            
            # Fallback to simple analysis
            positive_words = ["happy", "great", "awesome", "success", "joy"]
            negative_words = ["error", "fail", "bad", "wrong", "issue"]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            vibe = 5 + positive_count - negative_count
            return max(1, min(10, vibe))
            
        except Exception:
            return 5  # Neutral if analysis fails
    
    async def analyze_code_eco_impact(self, code: str) -> Dict[str, Any]:
        """
        Analyze code for eco-impact (Directive 17)
        Uses lightweight models for sustainability
        """
        try:
            # Simple heuristics for eco-scoring
            lines = code.split('\n')
            
            eco_metrics = {
                "lines_of_code": len(lines),
                "complexity_score": self._estimate_complexity(code),
                "optimization_suggestions": [],
                "estimated_carbon_mg": len(code) * 0.01  # Rough estimate
            }
            
            # Check for inefficient patterns
            if "for i in range(len(" in code:
                eco_metrics["optimization_suggestions"].append(
                    "Consider using enumerate() instead of range(len())"
                )
            
            if code.count("import") > 20:
                eco_metrics["optimization_suggestions"].append(
                    "Many imports detected - consider lazy loading"
                )
            
            # Calculate final eco score
            base_score = 100
            penalty = eco_metrics["complexity_score"] * 5
            bonus = len(eco_metrics["optimization_suggestions"]) * 3
            
            eco_metrics["eco_score"] = max(0, min(100, base_score - penalty + bonus))
            
            return eco_metrics
            
        except Exception as e:
            logger.error(f"❌ Eco-impact analysis failed: {e}")
            return {"eco_score": 50, "error": str(e)}
    
    def _estimate_complexity(self, code: str) -> int:
        """Estimate code complexity (simplified cyclomatic complexity)"""
        complexity = 1  # Base complexity
        
        # Count decision points
        decision_keywords = [
            "if ", "elif ", "else:", "for ", "while ",
            "try:", "except:", "case ", "match "
        ]
        
        for keyword in decision_keywords:
            complexity += code.count(keyword)
        
        return min(complexity, 20)  # Cap at 20
    
    async def get_adhd_friendly_summary(self, text: str) -> str:
        """
        Generate ADHD-friendly summary (Directive 18 v4.0)
        Uses bullet points and highlights key info
        """
        try:
            # Use summarization model
            response = await self.generate_response(
                prompt=f"Summarize this in bullet points (max 5 points): {text}",
                model=self.RECOMMENDED_MODELS["summarization"],
                max_tokens=100
            )
            
            content = response["content"]
            
            # Format as bullet points if not already
            if "•" not in content and "-" not in content:
                lines = content.split(". ")
                content = "\n".join(f"• {line.strip()}" for line in lines if line)
            
            return f"✨ Quick Summary:\n{content}"
            
        except Exception:
            # Fallback to simple extraction
            sentences = text.split(". ")[:3]
            return "✨ Quick Summary:\n" + "\n".join(f"• {s}" for s in sentences)
    
    async def detect_dei_issues(self, code: str) -> List[Dict[str, str]]:
        """
        Detect potential DEI issues in code (Directive 19 v4.0)
        Checks for inclusive language and accessibility
        """
        issues = []
        
        # Check for non-inclusive terms
        problematic_terms = {
            "blacklist": "blocklist",
            "whitelist": "allowlist",
            "master": "main",
            "slave": "replica",
            "dummy": "placeholder",
            "crazy": "unexpected",
            "insane": "extreme"
        }
        
        code_lower = code.lower()
        for term, replacement in problematic_terms.items():
            if term in code_lower:
                issues.append({
                    "type": "inclusive_language",
                    "message": f"Consider using '{replacement}' instead of '{term}'",
                    "severity": "medium"
                })
        
        # Check for accessibility in UI code
        if "img" in code and "alt=" not in code:
            issues.append({
                "type": "accessibility",
                "message": "Images should have alt text for screen readers",
                "severity": "high"
            })
        
        if "onClick" in code and "onKeyPress" not in code:
            issues.append({
                "type": "accessibility", 
                "message": "Interactive elements should support keyboard navigation",
                "severity": "medium"
            })
        
        return issues
    
    async def stream_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[str, None]:
        """Stream response (currently converts batch to stream)"""
        
        # HuggingFace API doesn't support true streaming yet
        # Simulate it by yielding chunks
        response = await self.generate_response(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            context=context
        )
        
        content = response["content"]
        chunk_size = 10  # Words per chunk
        words = content.split()
        
        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            yield chunk + " "
            await asyncio.sleep(0.1)  # Simulate streaming delay
    
    async def health_check(self) -> bool:
        """Check provider health with good vibes"""
        try:
            if not self.client:
                return False
            
            # Quick API check
            response = await self.client.get("/")
            is_healthy = response.status_code in [200, 302]
            
            if is_healthy:
                logger.info("💚 HuggingFace is vibing and ready!")
            else:
                logger.warning("💛 HuggingFace needs some love")
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            return False
    
    async def cleanup(self) -> None:
        """Cleanup resources with gratitude"""
        if self.client:
            await self.client.aclose()
        
        # Cleanup local models
        self.local_pipelines.clear()
        self.executor.shutdown(wait=False)
        
        await super().cleanup()
        logger.info("🙏 Thank you HuggingFace for the amazing models!")