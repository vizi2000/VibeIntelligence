"""
Unit tests for HuggingFace AI Provider
Testing local model support and vibe analysis features
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
import asyncio

from src.ai.providers.huggingface_provider import HuggingFaceProvider
from src.core.exceptions import AIProviderException


@pytest.mark.ai
@pytest.mark.unit
class TestHuggingFaceProvider:
    """Test suite for HuggingFace provider with eco-friendly local models"""
    
    @pytest.mark.asyncio
    async def test_initialization_with_local_models(self, mock_httpx_client):
        """Test initialization with local model support"""
        # Arrange
        mock_pipeline = MagicMock()
        
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            with patch('transformers.pipeline', return_value=mock_pipeline):
                provider = HuggingFaceProvider("test-token")
                
                # Act
                await provider.initialize()
                
                # Assert
                assert provider.is_initialized
                assert provider.provider_name == "HuggingFace"
                assert "emotion" in provider.local_pipelines
    
    @pytest.mark.asyncio
    async def test_initialization_without_local_models(self, mock_httpx_client):
        """Test initialization when local models fail to load"""
        # Arrange
        with patch('httpx.AsyncClient', return_value=mock_httpx_client):
            with patch('src.ai.providers.huggingface_provider.settings.ENABLE_LOCAL_MODELS', False):
                provider = HuggingFaceProvider("test-token")
                
                # Act
                await provider.initialize()
                
                # Assert
                assert provider.is_initialized
                assert len(provider.local_pipelines) == 0  # No local models
    
    @pytest.mark.asyncio
    async def test_generate_response_with_eco_metrics(self, huggingface_provider):
        """Test response generation includes eco-friendly metrics"""
        # Act
        response = await huggingface_provider.generate_response(
            prompt="Explain sustainable coding",
            model="microsoft/phi-2",
            temperature=0.7
        )
        
        # Assert
        assert response["content"] == "Test AI response with good vibes! 🌟"
        assert response["eco_score"] == 85  # Cloud model eco score
        assert response["cost"] == 0.0  # HuggingFace is free!
        assert "vibe_score" in response
    
    @pytest.mark.asyncio
    async def test_analyze_vibe_with_local_model(self, huggingface_provider):
        """Test vibe analysis using local emotion model"""
        # Arrange
        mock_emotion_pipeline = MagicMock()
        mock_emotion_pipeline.return_value = [{"label": "joy", "score": 0.9}]
        huggingface_provider.local_pipelines["emotion"] = mock_emotion_pipeline
        
        # Act
        vibe_score = await huggingface_provider._analyze_vibe("I love coding!")
        
        # Assert
        assert vibe_score == 10  # Maximum joy
        mock_emotion_pipeline.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analyze_vibe_fallback(self, huggingface_provider):
        """Test vibe analysis fallback when local model unavailable"""
        # Arrange
        huggingface_provider.local_pipelines = {}  # No local models
        
        # Act
        vibe_score_positive = await huggingface_provider._analyze_vibe(
            "This is great and awesome!"
        )
        vibe_score_negative = await huggingface_provider._analyze_vibe(
            "This failed with an error"
        )
        
        # Assert
        assert vibe_score_positive > 5
        assert vibe_score_negative < 5
    
    @pytest.mark.asyncio
    async def test_analyze_code_eco_impact(self, huggingface_provider):
        """Test code eco-impact analysis for sustainability"""
        # Arrange
        sample_code = """
        for i in range(len(items)):
            print(items[i])
        
        import os
        import sys
        import json
        # ... 20 more imports
        """
        
        # Act
        eco_metrics = await huggingface_provider.analyze_code_eco_impact(sample_code)
        
        # Assert
        assert "eco_score" in eco_metrics
        assert "lines_of_code" in eco_metrics
        assert "optimization_suggestions" in eco_metrics
        assert len(eco_metrics["optimization_suggestions"]) > 0
        assert eco_metrics["eco_score"] < 100  # Room for improvement
    
    @pytest.mark.asyncio
    async def test_get_adhd_friendly_summary(self, huggingface_provider):
        """Test ADHD-friendly summarization (Directive 18)"""
        # Arrange
        long_text = """
        This is a very long explanation about software architecture patterns
        including microservices, monoliths, and serverless architectures.
        Each has its own benefits and drawbacks that must be considered.
        """
        
        # Act
        summary = await huggingface_provider.get_adhd_friendly_summary(long_text)
        
        # Assert
        assert summary.startswith("✨ Quick Summary:")
        assert "•" in summary or "-" in summary  # Has bullet points
        assert len(summary) < len(long_text)  # Actually shorter
    
    @pytest.mark.asyncio
    async def test_detect_dei_issues(self, huggingface_provider):
        """Test DEI issue detection (Directive 19)"""
        # Arrange
        problematic_code = """
        # This is the master branch
        blacklist = ["bad_user"]
        whitelist = ["good_user"]
        
        def crazy_function():
            # This is insane code
            dummy_value = 0
        
        <img src="logo.png">
        <button onClick="submit()">Submit</button>
        """
        
        # Act
        issues = await huggingface_provider.detect_dei_issues(problematic_code)
        
        # Assert
        assert len(issues) > 0
        
        # Check for inclusive language issues
        issue_types = [issue["type"] for issue in issues]
        assert "inclusive_language" in issue_types
        assert "accessibility" in issue_types
        
        # Verify specific detections
        issue_messages = " ".join(issue["message"] for issue in issues)
        assert "blocklist" in issue_messages  # Suggests replacement
        assert "alt text" in issue_messages  # Accessibility
        assert "keyboard" in issue_messages  # Keyboard navigation
    
    @pytest.mark.asyncio
    async def test_stream_response(self, huggingface_provider):
        """Test response streaming simulation"""
        # Act
        chunks = []
        async for chunk in huggingface_provider.stream_response(
            "Generate a haiku about testing"
        ):
            chunks.append(chunk)
            await asyncio.sleep(0.01)  # Simulate processing
        
        # Assert
        assert len(chunks) > 0
        full_response = "".join(chunks)
        assert full_response == "Test AI response with good vibes! 🌟 "
    
    @pytest.mark.asyncio
    async def test_model_loading_retry(self, huggingface_provider):
        """Test retry logic when model is loading"""
        # Arrange
        loading_response = AsyncMock()
        loading_response.status_code = 503  # Model loading
        
        success_response = AsyncMock()
        success_response.status_code = 200
        success_response.json.return_value = [{
            "generated_text": "Model loaded and ready!"
        }]
        
        # First call returns 503, second returns 200
        huggingface_provider.client.post.side_effect = [
            loading_response,
            success_response
        ]
        
        # Act
        with patch('asyncio.sleep', return_value=None):  # Skip actual sleep
            response = await huggingface_provider.generate_response("Test")
        
        # Assert
        assert response["content"] == "Model loaded and ready!"
        assert huggingface_provider.client.post.call_count == 2
    
    def test_complexity_estimation(self, huggingface_provider):
        """Test code complexity estimation"""
        # Arrange
        simple_code = "print('hello')"
        complex_code = """
        if condition:
            for item in items:
                try:
                    if item.value > 0:
                        process(item)
                except Exception:
                    handle_error()
        """
        
        # Act
        simple_complexity = huggingface_provider._estimate_complexity(simple_code)
        complex_complexity = huggingface_provider._estimate_complexity(complex_code)
        
        # Assert
        assert simple_complexity == 1  # Base complexity
        assert complex_complexity > simple_complexity
        assert complex_complexity <= 20  # Capped at 20
    
    @pytest.mark.asyncio
    @pytest.mark.vibe
    async def test_vibe_scoring_integration(self, huggingface_provider):
        """Test that all responses include vibe scoring"""
        # Arrange
        test_prompts = [
            "Write happy code",
            "Debug this error",
            "Optimize performance"
        ]
        
        # Act & Assert
        for prompt in test_prompts:
            response = await huggingface_provider.generate_response(prompt)
            assert "vibe_score" in response
            assert 1 <= response["vibe_score"] <= 10
    
    @pytest.mark.asyncio
    async def test_cleanup_with_local_models(self, huggingface_provider):
        """Test cleanup properly shuts down local models"""
        # Arrange
        mock_executor = MagicMock()
        huggingface_provider.executor = mock_executor
        huggingface_provider.local_pipelines = {"emotion": MagicMock()}
        
        # Act
        await huggingface_provider.cleanup()
        
        # Assert
        huggingface_provider.client.aclose.assert_called_once()
        mock_executor.shutdown.assert_called_once_with(wait=False)
        assert len(huggingface_provider.local_pipelines) == 0