"""
AI Service for Zenith Coder
Integrates AI capabilities with project management
Following v4.0 Vibecoding principles
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import asyncio

from ..ai.orchestrator import orchestrator, TaskType
from ..ai.providers import HuggingFaceProvider
from ..core.config import settings
from ..models.project import Project

logger = logging.getLogger(__name__)


class AIService:
    """
    AI Service integrating multiple providers for project analysis
    Implements vibecoding features: eco-scoring, sentiment analysis, etc.
    """
    
    def __init__(self):
        self.orchestrator = orchestrator
        self._initialized = False
        
    async def initialize(self):
        """Initialize AI service with configured providers"""
        if self._initialized:
            return
            
        try:
            await self.orchestrator.initialize()
            self._initialized = True
            logger.info("✅ AI Service initialized with vibecoding features!")
        except Exception as e:
            logger.error(f"❌ AI Service initialization failed: {e}")
            raise
    
    async def analyze_project(self, project: Project) -> Dict[str, Any]:
        """
        Analyze a project using AI to provide insights
        Returns vibe score, eco score, and recommendations
        """
        try:
            # Read project README if exists
            readme_path = Path(project.path) / "README.md"
            readme_content = ""
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    readme_content = f.read()[:1000]  # First 1000 chars
            
            # Generate project analysis prompt
            prompt = f"""
            Analyze this software project and provide insights:
            
            Project: {project.name}
            Type: {project.project_type}
            Path: {project.path}
            Has Documentation: {project.has_documentation}
            Has Tests: {project.has_tests}
            
            README excerpt:
            {readme_content}
            
            Provide:
            1. Brief quality assessment
            2. Sustainability/eco-friendliness score (0-100)
            3. Developer experience score (0-100)
            4. Three improvement suggestions
            """
            
            # Get AI analysis
            response = await self.orchestrator.generate(
                prompt=prompt,
                task_type=TaskType.CODE_ANALYSIS,
                temperature=0.7,
                max_tokens=300
            )
            
            # Extract vibe score from sentiment
            vibe_analysis = await self.orchestrator.analyze_vibe(response["content"])
            
            return {
                "analysis": response["content"],
                "vibe_score": vibe_analysis["vibe_score"],
                "eco_score": response.get("eco_score", 75),
                "provider": response["provider"],
                "recommendations": self._extract_recommendations(response["content"])
            }
            
        except Exception as e:
            logger.error(f"Project analysis failed: {e}")
            return {
                "analysis": "Analysis temporarily unavailable",
                "vibe_score": 5,
                "eco_score": 50,
                "error": str(e)
            }
    
    async def generate_documentation(self, project: Project) -> str:
        """
        Generate AI-powered documentation for a project
        Creates README with vibecoding principles
        """
        try:
            prompt = f"""
            Generate a comprehensive README.md for this project:
            
            Project: {project.name}
            Type: {project.project_type}
            Technologies: {project.technologies}
            
            Include:
            1. Project overview with emoji header
            2. Installation instructions
            3. Usage examples
            4. Contributing guidelines
            5. Eco-friendly deployment tips
            
            Make it welcoming, inclusive, and joy-sparking!
            """
            
            response = await self.orchestrator.generate(
                prompt=prompt,
                task_type=TaskType.DOCUMENTATION,
                temperature=0.8,
                max_tokens=500
            )
            
            return response["content"]
            
        except Exception as e:
            logger.error(f"Documentation generation failed: {e}")
            return f"# {project.name} 🚀\n\nDocumentation generation in progress..."
    
    async def suggest_improvements(self, project: Project) -> List[Dict[str, str]]:
        """
        Get AI-powered improvement suggestions
        Focuses on sustainability and developer wellness
        """
        suggestions = []
        
        # Check for eco-improvements
        if not project.has_docker:
            suggestions.append({
                "type": "eco",
                "title": "Add Docker support",
                "description": "Containerization reduces environment setup time and improves consistency",
                "impact": "high"
            })
        
        if not project.has_tests:
            suggestions.append({
                "type": "quality",
                "title": "Add test suite",
                "description": "Tests improve confidence and reduce debugging stress",
                "impact": "high"
            })
        
        if not project.has_documentation:
            suggestions.append({
                "type": "dx",
                "title": "Create documentation",
                "description": "Good docs make projects more accessible and joyful to use",
                "impact": "medium"
            })
        
        # Get AI suggestions if less than 3
        if len(suggestions) < 3:
            try:
                prompt = f"Suggest {3 - len(suggestions)} improvements for a {project.project_type} project focused on sustainability and developer wellness"
                
                response = await self.orchestrator.generate(
                    prompt=prompt,
                    task_type=TaskType.CODE_ANALYSIS,
                    temperature=0.9,
                    max_tokens=200
                )
                
                # Parse AI suggestions (simplified)
                ai_suggestions = response["content"].split('\n')
                for sugg in ai_suggestions[:3-len(suggestions)]:
                    if sugg.strip():
                        suggestions.append({
                            "type": "ai",
                            "title": sugg.strip()[:50],
                            "description": sugg.strip(),
                            "impact": "medium"
                        })
                        
            except Exception as e:
                logger.error(f"AI suggestions failed: {e}")
        
        return suggestions
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """Get AI usage statistics"""
        return await self.orchestrator.get_usage_stats()
    
    async def analyze_vibe(self, text: str) -> Dict[str, Any]:
        """Analyze the vibe/sentiment of text"""
        try:
            response = await self.orchestrator.generate(
                prompt=f"Analyze the emotional tone and vibe of this text. Rate the vibe score from 0-100 and choose an emoji: {text}",
                task_type=TaskType.SUMMARIZATION,
                temperature=0.7,
                max_tokens=100
            )
            
            # Simple parsing (in production, use structured output)
            content = response["content"]
            vibe_score = 75  # Default
            vibe_emoji = "😊"
            
            # Try to extract score from response
            import re
            score_match = re.search(r'(\d+)', content)
            if score_match:
                vibe_score = min(100, int(score_match.group(1)))
            
            # Determine emoji based on score
            if vibe_score >= 90:
                vibe_emoji = "🤩"
            elif vibe_score >= 80:
                vibe_emoji = "😄"
            elif vibe_score >= 70:
                vibe_emoji = "😊"
            elif vibe_score >= 60:
                vibe_emoji = "🙂"
            elif vibe_score >= 50:
                vibe_emoji = "😐"
            elif vibe_score >= 40:
                vibe_emoji = "😕"
            else:
                vibe_emoji = "😢"
            
            sentiment = "positive" if vibe_score >= 60 else "negative" if vibe_score < 40 else "neutral"
            
            suggestions = []
            if vibe_score < 70:
                suggestions.append("Add more positive language to boost the vibe! ✨")
                suggestions.append("Consider including encouraging words 💪")
            
            return {
                "vibe_score": vibe_score,
                "vibe_emoji": vibe_emoji,
                "sentiment": sentiment,
                "suggestions": suggestions
            }
            
        except Exception as e:
            logger.error(f"Vibe analysis error: {e}")
            return {
                "vibe_score": 75,
                "vibe_emoji": "😊",
                "sentiment": "positive",
                "suggestions": ["Keep spreading good vibes!"]
            }
    
    async def generate(
        self,
        prompt: str,
        task_type: str = "general",
        temperature: float = 0.7,
        max_tokens: int = 500,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate AI response for any prompt"""
        # Map string task type to enum
        task_type_map = {
            "general": TaskType.GENERAL,
            "code": TaskType.CODE_GENERATION,
            "analysis": TaskType.CODE_ANALYSIS,
            "summary": TaskType.SUMMARIZATION,
            "documentation": TaskType.DOCUMENTATION
        }
        
        mapped_type = task_type_map.get(task_type, TaskType.GENERAL)
        
        response = await self.orchestrator.generate(
            prompt=prompt,
            task_type=mapped_type,
            temperature=temperature,
            max_tokens=max_tokens,
            context=context
        )
        
        return response
    
    async def chat(self, message: str, context: str = "") -> Dict[str, str]:
        """Chat with AI Assistant"""
        try:
            # Build conversational prompt
            prompt = f"You are a helpful AI assistant for Zenith Coder. Be friendly, supportive, and use emojis occasionally.\n"
            if context:
                prompt += f"Context: {context}\n"
            prompt += f"User: {message}\nAssistant:"
            
            response = await self.orchestrator.generate(
                prompt=prompt,
                task_type=TaskType.GENERAL,
                temperature=0.8,
                max_tokens=200
            )
            
            return {
                "response": response["content"]
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return {
                "response": "I'm here to help! Could you please rephrase your question? 🌟"
            }
    
    async def get_quantum_idea(self) -> str:
        """Get a quantum-inspired creative idea"""
        return await self.orchestrator.get_quantum_idea()
    
    async def calculate_eco_impact(self, project_count: int, total_size_gb: float) -> Dict[str, Any]:
        """
        Calculate environmental impact of projects
        Returns CO2 estimates and offset recommendations
        """
        # Basic calculations
        co2_per_gb_year = 0.5  # kg CO2
        total_co2 = total_size_gb * co2_per_gb_year
        trees_needed = total_co2 / 20  # 1 tree absorbs ~20kg CO2/year
        
        # Get AI enhancement
        try:
            prompt = f"""
            Provide eco-friendly recommendations for managing {project_count} projects 
            totaling {total_size_gb:.1f}GB. Focus on practical sustainability tips.
            """
            
            response = await self.orchestrator.generate(
                prompt=prompt,
                task_type=TaskType.GENERAL_CHAT,
                temperature=0.7,
                max_tokens=150
            )
            
            recommendations = response["content"]
        except:
            recommendations = "Consider cloud storage with renewable energy providers"
        
        return {
            "estimated_co2_kg_year": round(total_co2, 2),
            "trees_to_offset": round(trees_needed, 1),
            "green_hosting_savings": "30-50% with renewable energy",
            "recommendations": recommendations,
            "eco_score": 85 if total_size_gb < 100 else 65
        }
    
    def _extract_recommendations(self, text: str) -> List[str]:
        """Extract recommendations from AI response"""
        recommendations = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered items or bullets
            if (line.startswith(('1.', '2.', '3.', '•', '-')) and 
                len(line) > 5):
                recommendations.append(line)
        
        return recommendations[:3]  # Top 3
    
    async def check_dei_compliance(self, code_content: str) -> Dict[str, Any]:
        """
        Check code for DEI (Diversity, Equity, Inclusion) issues
        Following v4.0 Directive 19
        """
        if "huggingface" in self.orchestrator.providers:
            provider = self.orchestrator.providers["huggingface"]
            issues = await provider.detect_dei_issues(code_content)
            
            return {
                "compliant": len(issues) == 0,
                "issues": issues,
                "score": max(0, 100 - len(issues) * 10)
            }
        
        # Fallback
        return {
            "compliant": True,
            "issues": [],
            "score": 90
        }
    
    async def generate_adhd_summary(self, text: str) -> str:
        """
        Generate ADHD-friendly summary
        Following v4.0 Directive 18
        """
        if "huggingface" in self.orchestrator.providers:
            provider = self.orchestrator.providers["huggingface"]
            return await provider.get_adhd_friendly_summary(text)
        
        # Fallback
        sentences = text.split('. ')[:3]
        return "✨ Quick Points:\n" + "\n".join(f"• {s}" for s in sentences)


# Global AI service instance
ai_service = AIService()