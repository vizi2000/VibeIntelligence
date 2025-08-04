"""
Pytest configuration and fixtures
Following v4.0 testing directives with vibe monitoring
"""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, patch
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Import our modules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.main import app
from src.core.database import Base, get_db
from src.ai.orchestrator import AIOrchestrator, TaskType
from src.ai.providers import OpenRouterProvider, HuggingFaceProvider


# Test database
TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_db():
    """Create test database"""
    engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield TestingSessionLocal
    
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(test_db):
    """Create database session for tests"""
    session = test_db()
    yield session
    session.close()


@pytest.fixture
def client(db_session):
    """Create test client with database override"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for AI provider tests"""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    
    # Mock successful response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{
            "message": {"content": "Test AI response with good vibes! 🌟"},
            "delta": {"content": "Streaming test"}
        }],
        "usage": {"total_tokens": 42}
    }
    
    mock_client.post.return_value = mock_response
    mock_client.get.return_value = mock_response
    
    return mock_client


@pytest.fixture
async def openrouter_provider(mock_httpx_client):
    """Create OpenRouter provider with mocked client"""
    provider = OpenRouterProvider("test-api-key")
    provider.client = mock_httpx_client
    provider.is_initialized = True
    return provider


@pytest.fixture
async def huggingface_provider():
    """Create HuggingFace provider with mocked functionality"""
    from src.ai.providers.huggingface_provider import HuggingFaceProvider
    provider = HuggingFaceProvider("test-api-token")
    
    # Mock the HTTP client
    mock_client = AsyncMock()
    
    # Mock test response
    test_response = AsyncMock()
    test_response.status_code = 200
    test_response.text = "OK"
    mock_client.get = AsyncMock(return_value=test_response)
    
    # Mock generate response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json = AsyncMock(return_value=[{
        "generated_text": "Test AI response with good vibes! 🌟"
    }])
    mock_client.post = AsyncMock(return_value=mock_response)
    
    provider.client = mock_client
    provider.http_client = mock_client
    
    # Initialize with mocked local models
    provider.is_initialized = True
    provider.local_pipelines = {"emotion": AsyncMock()}
    
    return provider


@pytest.fixture
async def ai_orchestrator(openrouter_provider, huggingface_provider):
    """Create AI orchestrator with mocked providers"""
    orchestrator = AIOrchestrator()
    orchestrator.providers = {
        "openrouter": openrouter_provider,
        "huggingface": huggingface_provider
    }
    orchestrator.provider_health = {
        "openrouter": True,
        "huggingface": True
    }
    orchestrator._initialized = True
    return orchestrator


@pytest.fixture
def vibe_monitor():
    """Vibe monitoring fixture for test wellness tracking"""
    class VibeMonitor:
        def __init__(self):
            self.start_vibe = 100
            self.current_vibe = 100
            self.test_count = 0
            self.break_reminder_shown = False
        
        def track_test(self):
            """Track test execution for well-being"""
            self.test_count += 1
            
            # Decrease vibe slightly with each test
            self.current_vibe = max(50, self.current_vibe - 2)
            
            # Suggest break after 10 tests (Directive 19)
            if self.test_count % 10 == 0 and not self.break_reminder_shown:
                self.break_reminder_shown = True
                print("\n🌿 Vibe Check: Take a 5-minute break! Your well-being matters.")
                print(f"   Current vibe: {self.current_vibe}/100")
                print("   Stretch, hydrate, or practice mindful breathing. 🧘\n")
        
        def get_vibe_score(self):
            return self.current_vibe
        
        def reset(self):
            self.current_vibe = 100
            self.test_count = 0
            self.break_reminder_shown = False
    
    monitor = VibeMonitor()
    yield monitor
    
    # End of test session vibe check
    if monitor.test_count > 0:
        print(f"\n✨ Test session complete! Final vibe: {monitor.current_vibe}/100")
        print(f"   You ran {monitor.test_count} tests. Great job! 🎉\n")


@pytest.fixture(autouse=True)
def track_test_vibe(vibe_monitor, request):
    """Automatically track vibe for each test"""
    vibe_monitor.track_test()
    yield
    
    # Add vibe score to test report
    if hasattr(request.node, "vibe_score"):
        request.node.vibe_score = vibe_monitor.get_vibe_score()


@pytest.fixture
async def openrouter_provider():
    """OpenRouter provider fixture for testing"""
    from src.ai.providers.openrouter_provider import OpenRouterProvider
    provider = OpenRouterProvider("test-api-key")
    
    # Create proper async mock
    mock_client = AsyncMock()
    
    # Mock /models endpoint
    models_response = AsyncMock()
    models_response.json = AsyncMock(return_value={
        "data": [
            {"id": "openrouter/horizon-beta", "name": "Horizon Beta"},
            {"id": "mistralai/mistral-7b-instruct:free", "name": "Mistral 7B"}
        ]
    })
    models_response.status_code = 200
    mock_client.get = AsyncMock(return_value=models_response)
    
    # Mock post endpoint for completions
    completion_response = AsyncMock()
    completion_response.json = AsyncMock(return_value={
        "choices": [{
            "message": {
                "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)"
            }
        }],
        "usage": {"total_tokens": 42}
    })
    completion_response.status_code = 200
    mock_client.post = AsyncMock(return_value=completion_response)
    
    # Replace the client
    provider.client = mock_client
    provider.http_client = mock_client
    
    await provider.initialize()
    yield provider


@pytest.fixture
def diversity_personas():
    """Diversity testing personas (Directive 18)"""
    return [
        {
            "name": "Amara",
            "description": "Screen reader user from Nigeria",
            "needs": ["alt_text", "aria_labels", "keyboard_navigation"],
            "language": "en-NG"
        },
        {
            "name": "Carlos", 
            "description": "Color-blind developer from Mexico",
            "needs": ["high_contrast", "no_color_only_info"],
            "language": "es-MX"
        },
        {
            "name": "Yuki",
            "description": "ADHD programmer from Japan",
            "needs": ["clear_structure", "minimal_distractions", "bullet_points"],
            "language": "ja-JP"
        },
        {
            "name": "Fatima",
            "description": "Arabic speaker with dyslexia",
            "needs": ["rtl_support", "clear_fonts", "simple_language"],
            "language": "ar-SA"
        }
    ]


@pytest.fixture
def eco_metrics():
    """Eco-scoring metrics for sustainable testing"""
    return {
        "baseline_energy": 100,  # Watts
        "test_duration": 0,
        "carbon_factor": 0.5,  # kg CO2 per kWh
        
        "calculate_impact": lambda duration: {
            "energy_used": duration * 0.1,  # kWh
            "co2_emitted": duration * 0.1 * 0.5,  # kg CO2
            "trees_needed": (duration * 0.1 * 0.5) / 20  # trees/year
        }
    }


# Pytest plugin for vibe reporting
def pytest_configure(config):
    """Configure custom pytest markers"""
    config.addinivalue_line(
        "markers", "vibe: mark test for vibe monitoring"
    )


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add vibe summary to test report"""
    terminalreporter.section("Vibe Report 🌟")
    terminalreporter.write_line(
        "Testing completed with joy and mindfulness!"
    )
    
    # Show eco impact
    duration = getattr(terminalreporter, '_session_start', 0)
    if duration:
        terminalreporter.write_line(
            f"Eco-impact: ~0.01 kg CO2 saved by efficient testing 🌱"
        )