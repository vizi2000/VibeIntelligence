"""
Integration tests for AI API endpoints
Testing full request/response cycle with mocked AI providers
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from src.models.project import Project


@pytest.mark.integration
@pytest.mark.ai
class TestAIEndpoints:
    """Integration tests for AI-powered endpoints"""
    
    def test_analyze_project(self, client, db_session):
        """Test project analysis endpoint with AI insights"""
        # Arrange
        # Create test project
        project = Project(
            name="Test Project",
            path="/test/path",
            project_type="Python",
            has_documentation=True,
            has_tests=True,
            vibe_score=75,
            eco_score=80
        )
        db_session.add(project)
        db_session.commit()
        
        # Mock AI service
        with patch('src.api.ai.ai_service.analyze_project') as mock_analyze:
            mock_analyze.return_value = {
                "analysis": "This project shows excellent coding practices!",
                "vibe_score": 85,
                "eco_score": 90,
                "recommendations": [
                    "Add more unit tests",
                    "Consider using type hints"
                ],
                "provider": "openrouter"
            }
            
            # Act
            response = client.post(
                "/api/v1/ai/analyze-project",
                json={"project_id": project.id}
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            
            assert data["project_name"] == "Test Project"
            assert data["vibe_score"] == 85
            assert data["eco_score"] == 90
            assert len(data["recommendations"]) == 2
            assert data["provider"] == "openrouter"
            
            # Verify project scores were updated
            db_session.refresh(project)
            assert project.vibe_score == 85
            assert project.eco_score == 90
    
    def test_analyze_project_not_found(self, client):
        """Test project analysis with non-existent project"""
        # Act
        response = client.post(
            "/api/v1/ai/analyze-project",
            json={"project_id": 999}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_generate_documentation(self, client, db_session):
        """Test AI documentation generation"""
        # Arrange
        project = Project(
            name="Undocumented Project",
            path="/test/path",
            project_type="JavaScript",
            has_documentation=False,
            technologies=["React", "Node.js"]
        )
        db_session.add(project)
        db_session.commit()
        
        with patch('src.api.ai.ai_service.generate_documentation') as mock_generate:
            mock_generate.return_value = """
# Undocumented Project 🚀

A modern JavaScript application built with React and Node.js.

## Installation
```bash
npm install
```

## Usage
```bash
npm start
```

Made with ❤️ and sustainable coding practices!
"""
            
            # Act
            response = client.post(
                "/api/v1/ai/generate-documentation",
                json={"project_id": project.id, "style": "friendly"}
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            
            assert "# Undocumented Project 🚀" in data["documentation"]
            assert "Made with ❤️" in data["documentation"]
            assert data["message"] == "Documentation generated with love! 📚✨"
            
            # Verify project was updated
            db_session.refresh(project)
            assert project.has_documentation is True
            assert project.vibe_score > 75  # Increased for adding docs
    
    def test_get_project_suggestions(self, client, db_session):
        """Test AI-powered improvement suggestions"""
        # Arrange
        project = Project(
            name="Needs Improvement",
            path="/test/path",
            has_docker=False,
            has_tests=False,
            has_documentation=False
        )
        db_session.add(project)
        db_session.commit()
        
        with patch('src.api.ai.ai_service.suggest_improvements') as mock_suggest:
            mock_suggest.return_value = [
                {
                    "type": "eco",
                    "title": "Add Docker support",
                    "description": "Containerization reduces environment setup time",
                    "impact": "high"
                },
                {
                    "type": "quality",
                    "title": "Add test suite",
                    "description": "Tests improve confidence and reduce stress",
                    "impact": "high"
                }
            ]
            
            # Act
            response = client.get(f"/api/v1/ai/project-suggestions/{project.id}")
            
            # Assert
            assert response.status_code == 200
            suggestions = response.json()
            
            assert len(suggestions) == 2
            assert suggestions[0]["type"] == "eco"
            assert suggestions[1]["type"] == "quality"
            assert all(s["impact"] == "high" for s in suggestions)
    
    def test_check_dei_compliance(self, client):
        """Test DEI compliance checking"""
        # Arrange
        problematic_code = """
        master_list = []
        slave_process = None
        # This dummy function is crazy
        """
        
        with patch('src.api.ai.ai_service.check_dei_compliance') as mock_check:
            mock_check.return_value = {
                "compliant": False,
                "score": 60,
                "issues": [
                    {
                        "type": "inclusive_language",
                        "message": "Consider using 'main' instead of 'master'",
                        "severity": "medium"
                    }
                ]
            }
            
            # Act
            response = client.post(
                "/api/v1/ai/check-dei-compliance",
                json={"code": problematic_code, "language": "python"}
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            
            assert not data["compliant"]
            assert data["score"] == 60
            assert len(data["issues"]) == 1
            assert "Let's make this more inclusive! 💝" in data["message"]
    
    def test_generate_adhd_summary(self, client):
        """Test ADHD-friendly summarization"""
        # Arrange
        long_text = "This is a very long explanation " * 50
        
        with patch('src.api.ai.ai_service.generate_adhd_summary') as mock_summary:
            mock_summary.return_value = """
✨ Quick Summary:
• Main point about the topic
• Second important detail
• Action item to remember
"""
            
            # Act
            response = client.post(
                "/api/v1/ai/generate-adhd-summary",
                json={"text": long_text}
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            
            assert "✨ Quick Summary:" in data["summary"]
            assert "•" in data["summary"]
            assert "Take breaks" in data["tip"]
    
    def test_get_quantum_idea(self, client):
        """Test quantum idea generation"""
        # Arrange
        with patch('src.api.ai.ai_service.get_quantum_idea') as mock_quantum:
            mock_quantum.return_value = "🌈 What if code could heal itself using ML?"
            
            # Act
            response = client.get("/api/v1/ai/quantum-idea")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            
            assert "🌈" in data["idea"]
            assert "Let your creativity flow!" in data["vibe"]
    
    def test_vibe_check(self, client):
        """Test system vibe check endpoint"""
        # Arrange
        with patch('src.api.ai.ai_service.get_quantum_idea') as mock_quantum:
            mock_quantum.return_value = "🌈 Quantum creativity unleashed!"
            
            # Act
            response = client.get("/api/v1/ai/vibe-check")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            
            assert data["vibe_score"] == 85
            assert data["vibe_emoji"] == "🤩"
            assert "maximum frequency" in data["message"]
            assert data["quantum_idea"] == "🌈 Quantum creativity unleashed!"
    
    def test_eco_impact(self, client, db_session):
        """Test eco-impact calculation endpoint"""
        # Arrange
        # Create test projects
        for i in range(5):
            project = Project(
                name=f"Project {i}",
                path=f"/test/path/{i}",
                size_mb=100.0
            )
            db_session.add(project)
        db_session.commit()
        
        with patch('src.api.ai.ai_service.calculate_eco_impact') as mock_eco:
            mock_eco.return_value = {
                "estimated_co2_kg_year": 2.5,
                "trees_to_offset": 0.125,
                "green_hosting_savings": "30-50% with renewable energy",
                "recommendations": "Use cloud providers with renewable energy",
                "eco_score": 85
            }
            
            # Act
            response = client.get("/api/v1/ai/eco-impact")
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            
            assert data["total_projects"] == 5
            assert data["estimated_co2_kg_year"] == 2.5
            assert data["trees_to_offset"] == 0.125
            assert data["eco_score"] == 85
            assert "Every small optimization" in data["tip"]
    
    @pytest.mark.vibe
    def test_all_endpoints_include_vibe_elements(self, client):
        """Test that all AI endpoints include vibecoding elements"""
        # Test endpoints that should work without setup
        endpoints = [
            ("/api/v1/ai/quantum-idea", "get"),
            ("/api/v1/ai/vibe-check", "get"),
        ]
        
        for endpoint, method in endpoints:
            with patch('src.api.ai.ai_service') as mock_service:
                # Mock the specific methods
                mock_service.get_quantum_idea.return_value = "Test idea"
                
                # Make request
                if method == "get":
                    response = client.get(endpoint)
                else:
                    response = client.post(endpoint, json={})
                
                # All should return valid JSON
                assert response.status_code in [200, 422]  # 422 for missing params
                
                if response.status_code == 200:
                    data = response.json()
                    # Check for vibe elements (emojis, positive language)
                    json_str = str(data)
                    vibe_indicators = ["✨", "🌟", "💚", "🌈", "vibe", "joy", "love"]
                    has_vibe = any(indicator in json_str for indicator in vibe_indicators)
                    assert has_vibe, f"Endpoint {endpoint} lacks vibe elements"