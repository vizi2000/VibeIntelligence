"""
Test utilities and helpers
Following vibecoding principles for joyful testing
"""

import asyncio
import functools
from typing import Any, Dict, List
import random


class TestDataGenerator:
    """Generate diverse test data following DEI principles"""
    
    @staticmethod
    def get_diverse_names() -> List[str]:
        """Get culturally diverse names for testing"""
        return [
            "Amara Okafor",  # Nigerian
            "Carlos García",  # Mexican  
            "Yuki Tanaka",  # Japanese
            "Fatima Al-Rashid",  # Arabic
            "Priya Sharma",  # Indian
            "João Silva",  # Brazilian
            "Anna Kowalski",  # Polish
            "Li Wei",  # Chinese
        ]
    
    @staticmethod
    def get_inclusive_project_names() -> List[str]:
        """Get inclusive project names avoiding problematic terms"""
        return [
            "Global Connect",
            "Unity Builder",
            "Harmony API",
            "Bridge Framework",
            "Nexus Platform",
            "Synergy Tools",
            "Collaborative Suite",
            "Inclusive Design System"
        ]
    
    @staticmethod
    def get_positive_descriptions() -> List[str]:
        """Get positive, encouraging descriptions"""
        return [
            "An innovative solution that brings joy to coding! 🌟",
            "Sustainable and eco-friendly architecture 🌱",
            "Built with accessibility and inclusion in mind 💝",
            "Optimized for developer happiness and productivity 🚀",
            "Clean code that sparks creativity ✨",
            "A welcoming project for contributors of all backgrounds 🤝"
        ]


class AsyncTestHelper:
    """Helper for async test operations"""
    
    @staticmethod
    def async_test(timeout: int = 5):
        """Decorator for async tests with timeout"""
        def decorator(func):
            @functools.wraps(func)
            async def wrapper(*args, **kwargs):
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout
                )
            return wrapper
        return decorator
    
    @staticmethod
    async def gather_with_errors(*coroutines):
        """Gather results even if some fail"""
        results = await asyncio.gather(
            *coroutines,
            return_exceptions=True
        )
        
        successes = []
        errors = []
        
        for result in results:
            if isinstance(result, Exception):
                errors.append(result)
            else:
                successes.append(result)
        
        return successes, errors


class VibeAssertions:
    """Custom assertions that maintain good vibes"""
    
    @staticmethod
    def assert_with_encouragement(condition: bool, message: str = ""):
        """Assert with encouraging message on failure"""
        if not condition:
            encouragement = random.choice([
                "Don't worry, you'll get it! 💪",
                "Every bug is a learning opportunity! 🐛➡️🦋",
                "You're one step closer to the solution! 🎯",
                "Take a deep breath, you've got this! 🌟"
            ])
            
            full_message = f"{message}\n\n{encouragement}" if message else encouragement
            raise AssertionError(full_message)
    
    @staticmethod
    def assert_vibe_in_range(vibe_score: int, min_vibe: int = 0, max_vibe: int = 100):
        """Assert vibe score is in healthy range"""
        VibeAssertions.assert_with_encouragement(
            min_vibe <= vibe_score <= max_vibe,
            f"Vibe score {vibe_score} outside range [{min_vibe}, {max_vibe}]. "
            f"Remember: It's okay to not be at 100% all the time!"
        )
    
    @staticmethod
    def assert_eco_friendly(eco_score: int, threshold: int = 70):
        """Assert eco score meets sustainability goals"""
        VibeAssertions.assert_with_encouragement(
            eco_score >= threshold,
            f"Eco score {eco_score} below threshold {threshold}. "
            f"Small optimizations can make a big difference! 🌱"
        )


class MockDataFactory:
    """Factory for creating mock data with good vibes"""
    
    @staticmethod
    def create_happy_project(**kwargs) -> Dict[str, Any]:
        """Create a project with positive attributes"""
        defaults = {
            "name": random.choice(TestDataGenerator.get_inclusive_project_names()),
            "description": random.choice(TestDataGenerator.get_positive_descriptions()),
            "vibe_score": random.randint(80, 100),
            "eco_score": random.randint(75, 95),
            "has_tests": True,
            "has_documentation": True,
            "owner": random.choice(TestDataGenerator.get_diverse_names())
        }
        defaults.update(kwargs)
        return defaults
    
    @staticmethod
    def create_struggling_project(**kwargs) -> Dict[str, Any]:
        """Create a project that needs love (for improvement tests)"""
        defaults = {
            "name": "Project Needing Care",
            "description": "A project with potential that needs some TLC 🌱",
            "vibe_score": random.randint(40, 60),
            "eco_score": random.randint(30, 50),
            "has_tests": False,
            "has_documentation": False,
            "needs_love": True
        }
        defaults.update(kwargs)
        return defaults


def vibe_check(test_func):
    """Decorator to add vibe checking to tests"""
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        print(f"\n🌟 Running {test_func.__name__} with good vibes...")
        
        try:
            result = test_func(*args, **kwargs)
            print(f"✅ {test_func.__name__} passed! Keep vibing!")
            return result
        except Exception as e:
            print(f"💝 {test_func.__name__} needs attention: {str(e)}")
            print("   Remember: Every challenge is a growth opportunity!")
            raise
    
    return wrapper


# Test data constants following inclusive principles
INCLUSIVE_ERROR_MESSAGES = {
    "not_found": "We couldn't find what you're looking for, but we're here to help! 🔍",
    "validation": "The input needs a small adjustment. You're almost there! 🎯",
    "server_error": "Something went wrong on our end. Taking a deep breath and trying again... 🌿",
    "unauthorized": "Let's get you logged in so you can continue your journey! 🗝️"
}

ECO_FRIENDLY_DEFAULTS = {
    "max_file_size_mb": 50,  # Encourage smaller, efficient files
    "cache_duration_seconds": 3600,  # Reduce repeated computations
    "batch_size": 100,  # Process in eco-friendly batches
    "compression_enabled": True  # Save bandwidth and storage
}

WELLBEING_CONSTANTS = {
    "max_test_duration_minutes": 5,  # Prevent test fatigue
    "break_interval_tests": 10,  # Suggest break after this many tests
    "focus_time_minutes": 25,  # Pomodoro-style testing
    "celebration_threshold": 0.95  # Celebrate at 95% pass rate
}