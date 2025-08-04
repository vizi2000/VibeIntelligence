"""
Unit tests for AI Orchestrator
Testing multi-provider orchestration with smart routing
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock, Mock
import asyncio

from src.ai.orchestrator import AIOrchestrator, TaskType
from src.core.exceptions import AIProviderException


@pytest.mark.ai
@pytest.mark.unit
class TestAIOrchestrator:
    """Test suite for AI orchestrator with vibecoding principles"""
    
    @pytest.mark.asyncio
    async def test_initialization_with_providers(self):
        """Test orchestrator initialization with multiple providers"""
        # Arrange
        with patch('src.ai.orchestrator.settings') as mock_settings:
            mock_settings.OPENROUTER_API_KEY = "test-key"
            mock_settings.HUGGINGFACE_API_TOKEN = "test-token"
            mock_settings.AI_REQUEST_TIMEOUT = 60
            
            orchestrator = AIOrchestrator()
            
            # Mock provider initialization
            with patch.object(orchestrator, 'providers', {}):
                mock_or_provider = AsyncMock()
                mock_hf_provider = AsyncMock()
                
                with patch('src.ai.orchestrator.OpenRouterProvider', return_value=mock_or_provider):
                    with patch('src.ai.orchestrator.HuggingFaceProvider', return_value=mock_hf_provider):
                        # Act
                        await orchestrator.initialize()
                        
                        # Assert
                        assert orchestrator._initialized
                        mock_or_provider.initialize.assert_called_once()
                        mock_hf_provider.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_smart_routing_by_task_type(self, ai_orchestrator):
        """Test that tasks are routed to appropriate providers"""
        # Test sentiment analysis routes to HuggingFace
        suitable = ai_orchestrator._get_suitable_providers(
            TaskType.SENTIMENT_ANALYSIS
        )
        assert suitable[0] == "huggingface"
        
        # Test idea generation routes to OpenRouter
        suitable = ai_orchestrator._get_suitable_providers(
            TaskType.IDEA_GENERATION
        )
        assert suitable[0] == "openrouter"
    
    @pytest.mark.asyncio
    async def test_generate_with_fallback(self, ai_orchestrator):
        """Test fallback to secondary provider on failure"""
        # Arrange
        # Make OpenRouter fail
        ai_orchestrator.providers["openrouter"].generate_response = AsyncMock(side_effect=Exception("API Error"))
        
        # Act
        response = await ai_orchestrator.generate(
            prompt="Test prompt",
            task_type=TaskType.CODE_GENERATION
        )
        
        # Assert
        assert response["provider"] == "huggingface"  # Fallback worked
        assert response["content"] == "Test AI response with good vibes! 🌟"
    
    @pytest.mark.asyncio
    async def test_generate_streaming(self, ai_orchestrator):
        """Test streaming response generation"""
        # Arrange
        async def mock_stream():
            for chunk in ["Hello", " ", "World"]:
                yield chunk
        
        ai_orchestrator.providers["openrouter"].stream_response = Mock(return_value=mock_stream())
        
        # Act
        response = await ai_orchestrator.generate(
            prompt="Test",
            stream=True
        )
        
        # Assert
        assert response["provider"] == "openrouter"
        assert "stream" in response
        
        # Verify streaming works
        chunks = []
        async for chunk in response["stream"]:
            chunks.append(chunk)
        assert chunks == ["Hello", " ", "World"]
    
    @pytest.mark.asyncio
    async def test_analyze_vibe(self, ai_orchestrator):
        """Test vibe analysis with HuggingFace preference"""
        # Act
        result = await ai_orchestrator.analyze_vibe("I'm so happy coding!")
        
        # Assert
        assert result["vibe_score"] == 5  # Mock doesn't have _analyze_vibe
        assert result["vibe_emoji"] == "😊"
        assert result["provider"] in ["huggingface", "fallback"]
    
    @pytest.mark.asyncio
    async def test_get_eco_score(self, ai_orchestrator):
        """Test eco-score calculation for sustainability"""
        # Arrange
        sample_code = "def efficient_function(): return 42"
        
        # Mock HuggingFace provider's eco analysis
        mock_eco_result = {
            "eco_score": 95,
            "lines_of_code": 1,
            "optimization_suggestions": []
        }
        ai_orchestrator.providers["huggingface"].analyze_code_eco_impact = AsyncMock(
            return_value=mock_eco_result
        )
        
        # Act
        result = await ai_orchestrator.get_eco_score(sample_code)
        
        # Assert
        assert result["eco_score"] == 95
        assert result["lines_of_code"] == 1
    
    @pytest.mark.asyncio
    async def test_get_quantum_idea(self, ai_orchestrator):
        """Test quantum idea generation with creativity"""
        # Mock the get_quantum_idea method
        ai_orchestrator.providers["openrouter"].get_quantum_idea = AsyncMock(
            return_value="🌈 Quantum Idea: Test quantum idea with good vibes!"
        )
        
        # Act
        idea = await ai_orchestrator.get_quantum_idea()
        
        # Assert
        assert isinstance(idea, str)
        assert len(idea) > 10
        assert "🌈 Quantum Idea:" in idea
        
        # Should try OpenRouter first
        ai_orchestrator.providers["openrouter"].get_quantum_idea.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_summarize_for_adhd(self, ai_orchestrator):
        """Test ADHD-friendly summarization"""
        # Arrange
        long_text = "This is a very long text " * 20
        
        # Act
        summary = await ai_orchestrator.summarize_for_adhd(long_text)
        
        # Assert
        assert len(summary) < len(long_text)
        assert summary == "Test AI response with good vibes! 🌟"
    
    @pytest.mark.asyncio
    async def test_health_monitoring(self, ai_orchestrator):
        """Test background health monitoring"""
        # Arrange
        # Mock health_check methods on providers
        for provider in ai_orchestrator.providers.values():
            provider.health_check = AsyncMock(return_value=True)
        
        # Mock sleep to skip the delay but allow one iteration
        call_count = 0
        async def mock_sleep(delay):
            nonlocal call_count
            call_count += 1
            if call_count > 1:  # Allow the loop to run once, then break
                raise asyncio.CancelledError()
        
        with patch('asyncio.sleep', side_effect=mock_sleep):
            # Act
            try:
                await ai_orchestrator._monitor_health()
            except asyncio.CancelledError:
                pass  # Expected after one iteration
            
            # Assert
            for provider in ai_orchestrator.providers.values():
                provider.health_check.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_provider_preference(self, ai_orchestrator):
        """Test that preferred provider is used when specified"""
        # Act
        response = await ai_orchestrator.generate(
            prompt="Test",
            task_type=TaskType.GENERAL_CHAT,
            prefer_provider="huggingface"
        )
        
        # Assert
        assert response["provider"] == "huggingface"
    
    @pytest.mark.asyncio
    async def test_all_providers_fail(self, ai_orchestrator):
        """Test error when all providers fail"""
        # Arrange
        for provider in ai_orchestrator.providers.values():
            provider.generate_response = AsyncMock(side_effect=Exception("Provider error"))
        
        # Act & Assert
        with pytest.raises(AIProviderException) as exc:
            await ai_orchestrator.generate("Test")
        
        assert "All providers failed" in str(exc.value)
    
    @pytest.mark.asyncio
    async def test_usage_statistics(self, ai_orchestrator):
        """Test aggregated usage statistics"""
        # Arrange
        ai_orchestrator.providers["openrouter"].get_usage_stats = Mock(return_value={
            "total_tokens": 100,
            "total_cost": 0.0,
            "eco_score": 100
        })
        ai_orchestrator.providers["huggingface"].get_usage_stats = Mock(return_value={
            "total_tokens": 50,
            "total_cost": 0.0,
            "eco_score": 90
        })
        
        # Act
        stats = await ai_orchestrator.get_usage_stats()
        
        # Assert
        assert stats["total_tokens"] == 150
        assert stats["total_cost"] == 0.0
        assert stats["average_eco_score"] == 95
        assert stats["vibe_level"] == "high"
    
    def test_vibe_emoji_conversion(self, ai_orchestrator):
        """Test vibe score to emoji conversion"""
        # Test various vibe scores
        assert ai_orchestrator._get_vibe_emoji(10) == "🤩"
        assert ai_orchestrator._get_vibe_emoji(8) == "😄"
        assert ai_orchestrator._get_vibe_emoji(6) == "😊"
        assert ai_orchestrator._get_vibe_emoji(4) == "😐"
        assert ai_orchestrator._get_vibe_emoji(2) == "😔"
    
    @pytest.mark.asyncio
    async def test_cleanup(self, ai_orchestrator):
        """Test orchestrator cleanup"""
        # Act
        await ai_orchestrator.cleanup()
        
        # Assert
        for provider in ["openrouter", "huggingface"]:
            # Providers should be cleaned up
            assert provider not in ai_orchestrator.providers
        
        assert not ai_orchestrator._initialized
    
    @pytest.mark.asyncio
    @pytest.mark.vibe
    async def test_task_routing_for_all_types(self, ai_orchestrator):
        """Test that all task types have valid routing"""
        # Test each task type
        for task_type in TaskType:
            suitable = ai_orchestrator._get_suitable_providers(task_type)
            
            # Assert
            assert len(suitable) > 0, f"No providers for {task_type}"
            assert all(p in ["openrouter", "huggingface"] for p in suitable)