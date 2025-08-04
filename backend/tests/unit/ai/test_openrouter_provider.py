"""
Unit tests for OpenRouter AI Provider
Following Directive 3: >90% coverage with vibe monitoring
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock, Mock
import httpx
import json

from src.ai.providers.openrouter_provider import OpenRouterProvider
from src.core.exceptions import AIProviderException


@pytest.mark.ai
@pytest.mark.unit
class TestOpenRouterProvider:
    """Test suite for OpenRouter provider with vibecoding principles"""
    
    @pytest.mark.asyncio
    async def test_initialization_success(self, mock_httpx_client):
        """Test successful provider initialization with good vibes"""
        # Arrange
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            provider = OpenRouterProvider("test-api-key")
            
            # Act
            await provider.initialize()
            
            # Assert
            assert provider.is_initialized
            assert provider.provider_name == "OpenRouter"
            assert "openrouter/horizon-beta" in provider.available_models
            assert len(provider.available_models) == 8  # All free models
    
    @pytest.mark.asyncio
    async def test_initialization_failure(self):
        """Test initialization failure with compassionate error handling"""
        # Arrange
        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")
        
        with patch('httpx.AsyncClient', return_value=mock_client):
            provider = OpenRouterProvider("test-api-key")
            
            # Act & Assert
            with pytest.raises(AIProviderException) as exc:
                await provider.initialize()
            
            assert "Connection failed" in str(exc.value)
            assert not provider.is_initialized
    
    @pytest.mark.asyncio
    async def test_generate_response_with_horizon_beta(self, openrouter_provider, mock_httpx_client):
        """Test response generation using horizon-beta model"""
        # Arrange
        prompt = "Write a function to calculate fibonacci"
        
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{
                "message": {
                    "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
                }
            }],
            "usage": {"total_tokens": 42}
        })
        
        # Replace provider's client with mock
        openrouter_provider.client.post = AsyncMock(return_value=mock_response)
        
        # Act
        response = await openrouter_provider.generate_response(
            prompt=prompt,
            model="openrouter/horizon-beta",
            temperature=0.7,
            max_tokens=150
        )
        
        # Assert
        assert response["content"] == "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
        assert response["tokens_used"] == 42
        assert response["model_used"] == "openrouter/horizon-beta"
        assert response["cost"] == 0.0  # Free model!
        assert response["eco_score"] == 100  # Maximum eco-friendliness
        
        # Verify API call
        openrouter_provider.client.post.assert_called_once()
        call_args = openrouter_provider.client.post.call_args
        assert call_args[0][0] == "/chat/completions"
        assert call_args[1]["json"]["model"] == "openrouter/horizon-beta"
    
    @pytest.mark.asyncio
    async def test_generate_response_fallback_to_free_model(self, openrouter_provider):
        """Test fallback to free model when non-free model requested"""
        # Mock the response to ensure proper async behavior
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{
                "message": {
                    "content": "Test response using free model"
                }
            }],
            "usage": {"total_tokens": 10}
        })
        
        # Update the mock
        openrouter_provider.client.post = AsyncMock(return_value=mock_response)
        
        # Act
        response = await openrouter_provider.generate_response(
            prompt="Test prompt",
            model="gpt-4"  # Not a free model
        )
        
        # Assert
        assert response["model_used"] == "openrouter/horizon-beta"  # Fallback to first free model
        assert response["eco_score"] == 100
    
    @pytest.mark.asyncio
    async def test_stream_response(self, openrouter_provider):
        """Test streaming response for better UX (Directive 5)"""
        # Create an async iterator for the mock
        async def async_line_iterator():
            lines = [
                'data: {"choices":[{"delta":{"content":"Hello"}}]}',
                'data: {"choices":[{"delta":{"content":" world"}}]}',
                'data: [DONE]'
            ]
            for line in lines:
                yield line
        
        # Create mock stream response
        mock_stream = AsyncMock()
        mock_stream.aiter_lines = Mock(return_value=async_line_iterator())
        
        # Mock the context manager
        mock_context = AsyncMock()
        mock_context.__aenter__ = AsyncMock(return_value=mock_stream)
        mock_context.__aexit__ = AsyncMock(return_value=None)
        
        # Replace the stream method
        openrouter_provider.client.stream = Mock(return_value=mock_context)
        
        # Act
        chunks = []
        async for chunk in openrouter_provider.stream_response("Test prompt"):
            chunks.append(chunk)
        
        # Assert
        assert chunks == ["Hello", " world"]
    
    @pytest.mark.asyncio
    async def test_health_check_healthy(self, openrouter_provider):
        """Test health check returns positive vibes when healthy"""
        # Ensure the mock is properly set up
        mock_response = AsyncMock()
        mock_response.status_code = 200
        openrouter_provider.client.get = AsyncMock(return_value=mock_response)
        
        # Act
        is_healthy = await openrouter_provider.health_check()
        
        # Assert
        assert is_healthy is True
        openrouter_provider.client.get.assert_called_with("/models", timeout=5.0)
    
    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, openrouter_provider):
        """Test health check handles unhealthy state with compassion"""
        # Arrange
        openrouter_provider.client.get = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        
        # Act
        is_healthy = await openrouter_provider.health_check()
        
        # Assert
        assert is_healthy is False
    
    @pytest.mark.asyncio
    async def test_get_quantum_idea(self, openrouter_provider):
        """Test quantum idea generation for creative inspiration"""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{
                "message": {
                    "content": "Create a meditation app that syncs with plant growth"
                }
            }],
            "usage": {"total_tokens": 10}
        })
        openrouter_provider.client.post = AsyncMock(return_value=mock_response)
        
        # Act
        idea = await openrouter_provider.get_quantum_idea()
        
        # Assert
        assert idea.startswith("🌈 Quantum Idea:")
        assert len(idea) > 20  # Has actual content
        
        # Verify it tried to use AI
        openrouter_provider.client.post.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_quantum_idea_fallback(self, openrouter_provider):
        """Test quantum idea fallback when AI fails"""
        # Arrange
        openrouter_provider.client.post = AsyncMock(side_effect=Exception("API Error"))
        
        # Act
        idea = await openrouter_provider.get_quantum_idea()
        
        # Assert
        assert idea.startswith("🌈 Quantum Idea:")
        assert any(concept in idea for concept in [
            "mood", "haikus", "plant growth", "dance"
        ])
    
    @pytest.mark.asyncio
    async def test_cleanup(self, openrouter_provider):
        """Test graceful cleanup with gratitude"""
        # Mock the aclose method
        openrouter_provider.client.aclose = AsyncMock()
        
        # Act
        await openrouter_provider.cleanup()
        
        # Assert
        openrouter_provider.client.aclose.assert_called_once()
        assert not openrouter_provider.is_initialized
    
    @pytest.mark.asyncio
    async def test_error_handling_timeout(self, openrouter_provider):
        """Test timeout handling with helpful message"""
        # Arrange
        openrouter_provider.client.post = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))
        
        # Act & Assert
        with pytest.raises(AIProviderException) as exc:
            await openrouter_provider.generate_response("Test")
        
        assert "timeout" in str(exc.value).lower()
        assert "🕐" in str(exc.value)  # Includes emoji for friendliness
    
    @pytest.mark.asyncio
    async def test_error_handling_api_error(self, openrouter_provider):
        """Test API error handling with clear messaging"""
        # Arrange
        error_response = AsyncMock()
        error_response.status_code = 400
        error_response.json = AsyncMock(return_value={
            "error": {"message": "Invalid request"}
        })
        openrouter_provider.client.post = AsyncMock(return_value=error_response)
        
        # Act & Assert
        with pytest.raises(AIProviderException) as exc:
            await openrouter_provider.generate_response("Test")
        
        assert "Invalid request" in str(exc.value)
    
    @pytest.mark.asyncio
    @pytest.mark.vibe
    async def test_vibe_aware_system_prompt(self, openrouter_provider):
        """Test that system prompt includes vibecoding principles"""
        # Mock the response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{
                "message": {
                    "content": "Test response"
                }
            }],
            "usage": {"total_tokens": 10}
        })
        openrouter_provider.client.post = AsyncMock(return_value=mock_response)
        
        # Act
        await openrouter_provider.generate_response("Test prompt")
        
        # Assert
        call_args = openrouter_provider.client.post.call_args
        messages = call_args[1]["json"]["messages"]
        
        system_message = messages[0]
        assert system_message["role"] == "system"
        assert "vibecoding" in system_message["content"]
        assert "joyful" in system_message["content"]
        assert "sustainable" in system_message["content"]
    
    def test_usage_tracking(self, openrouter_provider):
        """Test token usage tracking for eco-metrics"""
        # Act
        openrouter_provider.track_usage(100, 0.0)
        openrouter_provider.track_usage(50, 0.0)
        
        # Assert
        assert openrouter_provider.total_tokens_used == 150
        assert openrouter_provider.total_cost == 0.0  # Free models!
        
        stats = openrouter_provider.get_usage_stats()
        assert stats["total_tokens"] == 150
        assert stats["total_cost"] == 0.0
        assert stats["eco_score"] == 100  # Perfect eco score for low usage