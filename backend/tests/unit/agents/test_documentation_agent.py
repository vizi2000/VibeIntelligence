"""
Tests for Documentation Agent
Following Directive 3: Multi-layered testing
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
import tempfile
import os

from src.agents.documentation_agent import DocumentationAgent, documentation_agent
from src.core.exceptions import DocumentationException


class TestDocumentationAgent:
    """Test suite for Documentation Agent with vibecoding principles"""
    
    @pytest.fixture
    def agent(self):
        """Create test agent instance"""
        return DocumentationAgent()
        
    @pytest.fixture
    def sample_project_info(self):
        """Sample project info for testing"""
        return {
            "name": "test-project",
            "type": "Python",
            "languages": ["Python", "JavaScript"],
            "has_tests": True,
            "has_readme": False,
            "health_score": 85,
            "path": "/test/path"
        }
        
    def test_initialization(self, agent):
        """Test agent initializes with templates and guidelines"""
        assert agent.templates is not None
        assert "readme" in agent.templates
        assert "contributing" in agent.templates
        assert "adr" in agent.templates
        
        assert agent.dei_guidelines is not None
        assert "inclusive_language" in agent.dei_guidelines
        assert "accessibility" in agent.dei_guidelines
        
    @pytest.mark.asyncio
    async def test_generate_readme_success(self, agent, sample_project_info):
        """Test successful README generation"""
        # Mock orchestrator response
        with patch('src.agents.documentation_agent.orchestrator.generate') as mock_generate:
            mock_generate.return_value = {
                "content": "Project description\nQuick start guide\nFeatures list",
                "provider": "test"
            }
            
            readme = await agent.generate_readme(sample_project_info)
            
            # Verify README contains expected elements
            assert "# test-project" in readme
            assert "🎯 What is this?" in readme
            assert "🚀 Quick Start" in readme
            assert "✨ Features" in readme
            assert "💚 Sustainability" in readme
            assert "Eco-Score: 85%" in readme
            
            # Verify AI was called with proper prompt
            mock_generate.assert_called_once()
            call_args = mock_generate.call_args
            assert "ADHD-friendly" in call_args[1]["prompt"]
            assert "test-project" in call_args[1]["prompt"]
            
    @pytest.mark.asyncio
    async def test_generate_readme_with_ai_failure(self, agent, sample_project_info):
        """Test README generation handles AI failures gracefully"""
        with patch('src.agents.documentation_agent.orchestrator.generate') as mock_generate:
            mock_generate.side_effect = Exception("AI service unavailable")
            
            with pytest.raises(DocumentationException) as exc_info:
                await agent.generate_readme(sample_project_info)
                
            assert "README generation failed" in str(exc_info.value)
            
    @pytest.mark.asyncio
    async def test_generate_contributing_guide(self, agent, sample_project_info):
        """Test CONTRIBUTING.md generation"""
        with patch('src.agents.documentation_agent.orchestrator.generate') as mock_generate:
            mock_generate.return_value = {
                "content": "Setup steps\nBug reporting guide",
                "provider": "test"
            }
            
            guide = await agent.generate_contributing_guide(sample_project_info)
            
            # Verify inclusive elements
            assert "We love your input! 💖" in guide
            assert "For ADHD Warriors:" in guide
            assert "Small PRs are perfect!" in guide
            assert "Be kind, be inclusive, spread joy!" in guide
            
    @pytest.mark.asyncio
    async def test_generate_adr(self, agent):
        """Test Architecture Decision Record generation"""
        decision_context = {
            "title": "Use Vibecoding Architecture",
            "context": "Need to improve developer joy and productivity",
            "number": "001"
        }
        
        with patch('src.agents.documentation_agent.orchestrator.generate') as mock_generate:
            mock_generate.return_value = {
                "content": "We will adopt vibecoding principles",
                "provider": "test"
            }
            
            adr = await agent.generate_adr(decision_context)
            
            # Verify ADR structure
            assert "# ADR-001: Use Vibecoding Architecture" in adr
            assert "📅 Date" in adr
            assert "🎯 Status" in adr
            assert "💡 Decision" in adr
            assert "🌟 Consequences" in adr
            
    @pytest.mark.asyncio
    async def test_analyze_documentation_quality(self, agent):
        """Test documentation quality analysis"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create test files
            readme_path = project_path / "README.md"
            readme_path.write_text("""
            # Test Project
            
            Welcome to our inclusive project! 🎉
            
            ## Quick Start
            1. Clone the repo
            2. Install deps
            3. Run!
            
            ## Contributing
            We welcome all contributions with open arms!
            
            ## Accessibility
            This project follows WCAG guidelines.
            """)
            
            (project_path / "CONTRIBUTING.md").write_text("Contributing guide")
            (project_path / "LICENSE").write_text("MIT License")
            (project_path / "CODE_OF_CONDUCT.md").write_text("Be excellent!")
            
            # Analyze
            analysis = await agent.analyze_documentation_quality(project_path)
            
            # Verify analysis
            assert analysis["has_readme"] is True
            assert analysis["has_contributing"] is True
            assert analysis["has_license"] is True
            assert analysis["has_code_of_conduct"] is True
            assert analysis["score"] >= 60
            assert analysis["dei_score"] > 0
            assert "peak_documentation_flow" in analysis["vibe_level"] or "high_vibe" in analysis["vibe_level"]
            
    @pytest.mark.asyncio
    async def test_analyze_missing_documentation(self, agent):
        """Test analysis when documentation is missing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            analysis = await agent.analyze_documentation_quality(project_path)
            
            # Verify suggestions
            assert analysis["has_readme"] is False
            assert "Add README.md" in analysis["suggestions"][0]
            assert analysis["score"] < 50
            assert analysis["vibe_level"] == "needs_documentation_love"
            
    def test_dei_guidelines_comprehensive(self, agent):
        """Test DEI guidelines are comprehensive"""
        guidelines = agent.dei_guidelines
        
        # Verify inclusive language guidelines
        assert any("they" in g for g in guidelines["inclusive_language"])
        assert any("clear language" in g for g in guidelines["inclusive_language"])
        
        # Verify accessibility guidelines
        assert any("heading" in g for g in guidelines["accessibility"])
        assert any("bullet" in g for g in guidelines["accessibility"])
        
        # Verify cultural awareness
        assert any("idiom" in g for g in guidelines["cultural_awareness"])
        assert any("timezone" in g for g in guidelines["cultural_awareness"])
        
    def test_calculate_doc_vibe(self, agent):
        """Test documentation vibe calculation"""
        # High vibe scenario
        high_analysis = {
            "score": 70,
            "dei_score": 60
        }
        assert agent._calculate_doc_vibe(high_analysis) == "peak_documentation_flow"
        
        # Low vibe scenario
        low_analysis = {
            "score": 20,
            "dei_score": 10
        }
        assert agent._calculate_doc_vibe(low_analysis) == "needs_documentation_love"
        
    @pytest.mark.asyncio
    async def test_readme_quality_analysis(self, agent):
        """Test README quality analysis features"""
        with tempfile.TemporaryDirectory() as tmpdir:
            readme_path = Path(tmpdir) / "README.md"
            readme_path.write_text("""
            # Project Name ![badge](badge.svg)
            
            ## Quick Start 🚀
            
            ```bash
            npm install
            npm start
            ```
            
            ## Contributing
            We welcome inclusive contributions!
            
            ## Accessibility
            This project is WCAG compliant.
            """)
            
            analysis = await agent._analyze_readme_quality(readme_path)
            
            # Verify quality metrics
            assert analysis["readme_quality"]["has_badges"] is True
            assert analysis["readme_quality"]["has_quick_start"] is True
            assert analysis["readme_quality"]["has_examples"] is True
            assert analysis["readme_quality"]["has_emojis"] is True
            assert analysis["dei_score"] >= 40
            assert analysis["accessibility_score"] >= 50
            
    def test_parse_ai_response_fallbacks(self, agent):
        """Test AI response parsing with fallbacks"""
        project_info = {"name": "test-proj", "health_score": 75}
        
        # Test with empty response
        result = agent._parse_ai_response("", project_info)
        assert result["project_name"] == "test-proj"
        assert result["eco_score"] == 75
        assert "vibecoding" in result["description"]
        
        # Test with partial response
        result = agent._parse_ai_response("This is a test project", project_info)
        assert result["description"] == "This is a test project"


# Integration test
@pytest.mark.integration
class TestDocumentationAgentIntegration:
    """Integration tests for Documentation Agent"""
    
    @pytest.mark.asyncio
    async def test_full_documentation_generation_flow(self):
        """Test complete documentation generation workflow"""
        project_info = {
            "name": "vibecoding-example",
            "type": "Node.js",
            "languages": ["JavaScript", "TypeScript"],
            "has_tests": True,
            "has_readme": False,
            "health_score": 90,
            "path": "/test/vibecoding-example"
        }
        
        # This would test with real AI if available
        # For unit tests, we mock
        with patch('src.agents.documentation_agent.orchestrator._initialized', True):
            with patch('src.agents.documentation_agent.orchestrator.generate') as mock_gen:
                mock_gen.return_value = {
                    "content": "Vibecoding example project for spreading joy",
                    "provider": "test"
                }
                
                # Generate all docs
                readme = await documentation_agent.generate_readme(project_info)
                contributing = await documentation_agent.generate_contributing_guide(project_info)
                
                # Verify all were generated
                assert "# vibecoding-example" in readme
                assert "Contributing to vibecoding-example" in contributing
                assert "spread joy" in contributing.lower()