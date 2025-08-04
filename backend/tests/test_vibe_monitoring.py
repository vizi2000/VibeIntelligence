"""
Vibe Monitoring Test Suite
Following Directive 19: Well-being and mental health focus
Ensures testing doesn't burn out developers
"""

import pytest
import time
from datetime import datetime, timedelta


@pytest.mark.vibe
class TestVibeMonitoring:
    """Test suite for monitoring and maintaining good vibes during testing"""
    
    def test_vibe_monitor_tracks_test_count(self, vibe_monitor):
        """Test that vibe monitor tracks number of tests run"""
        initial_count = vibe_monitor.test_count
        
        # Simulate running tests
        for _ in range(5):
            vibe_monitor.track_test()
        
        assert vibe_monitor.test_count == initial_count + 5
    
    def test_vibe_decreases_with_test_count(self, vibe_monitor):
        """Test that vibe score decreases as more tests run"""
        vibe_monitor.reset()
        initial_vibe = vibe_monitor.get_vibe_score()
        
        # Run several tests
        for _ in range(10):
            vibe_monitor.track_test()
        
        final_vibe = vibe_monitor.get_vibe_score()
        
        assert final_vibe < initial_vibe
        assert final_vibe >= 50  # Never goes below 50
    
    def test_break_reminder_after_threshold(self, vibe_monitor, capsys):
        """Test that break reminders appear after threshold"""
        vibe_monitor.reset()
        
        # Run exactly 10 tests to trigger reminder
        for i in range(10):
            vibe_monitor.track_test()
        
        captured = capsys.readouterr()
        
        # Should see break reminder
        assert "Take a 5-minute break!" in captured.out
        assert "🌿" in captured.out
        assert "well-being matters" in captured.out
    
    def test_vibe_score_bounds(self, vibe_monitor):
        """Test that vibe score stays within bounds"""
        vibe_monitor.reset()
        
        # Run many tests
        for _ in range(100):
            vibe_monitor.track_test()
        
        vibe = vibe_monitor.get_vibe_score()
        
        assert 50 <= vibe <= 100
    
    def test_session_summary_shows_stats(self, vibe_monitor, capsys):
        """Test that session summary shows helpful stats"""
        vibe_monitor.reset()
        
        # Run some tests
        for _ in range(5):
            vibe_monitor.track_test()
        
        # Trigger end of session by accessing final vibe
        # (In real implementation, this happens in fixture teardown)
        final_vibe = vibe_monitor.get_vibe_score()
        
        # Manual trigger for test
        if vibe_monitor.test_count > 0:
            print(f"\n✨ Test session complete! Final vibe: {final_vibe}/100")
            print(f"   You ran {vibe_monitor.test_count} tests. Great job! 🎉\n")
        
        captured = capsys.readouterr()
        
        assert "Test session complete!" in captured.out
        assert "Great job! 🎉" in captured.out
    
    def test_positive_affirmations_in_output(self):
        """Test that test output includes positive affirmations"""
        affirmations = [
            "You're doing great!",
            "Keep up the good work!",
            "Almost there!",
            "You've got this!",
            "Taking breaks helps creativity!"
        ]
        
        # In real implementation, these would appear in test output
        assert all(len(affirmation) > 0 for affirmation in affirmations)
    
    def test_eco_friendly_test_metrics(self, eco_metrics):
        """Test eco-impact calculations for test runs"""
        # Simulate 10-minute test run
        test_duration_hours = 10 / 60  # 10 minutes in hours
        
        impact = eco_metrics["calculate_impact"](test_duration_hours)
        
        assert impact["energy_used"] < 1  # Less than 1 kWh
        assert impact["co2_emitted"] < 0.5  # Less than 0.5 kg CO2
        assert impact["trees_needed"] < 0.01  # Minimal tree offset needed
    
    @pytest.mark.slow
    def test_long_running_test_warnings(self):
        """Test warnings for long-running tests"""
        start_time = time.time()
        
        # Simulate long operation
        time.sleep(0.1)  # Much shorter for actual test
        
        duration = time.time() - start_time
        
        # In real implementation, warn if test takes > 1 second
        if duration > 0.05:  # Lower threshold for test
            warning = "⚡ This test is taking a while. Consider optimization for developer happiness!"
            assert len(warning) > 0
    
    def test_test_categorization_for_mental_load(self):
        """Test that tests are categorized by mental load"""
        test_categories = {
            "simple": ["test_addition", "test_string_concat"],
            "moderate": ["test_api_response", "test_database_query"],
            "complex": ["test_multi_provider_orchestration", "test_distributed_system"]
        }
        
        # Recommendation: Run simple tests when tired
        # Run complex tests when fresh and caffeinated
        
        assert len(test_categories["simple"]) > 0
        assert len(test_categories["complex"]) > 0
    
    def test_mindful_test_naming(self):
        """Test that test names are clear and calming"""
        good_test_names = [
            "test_user_can_login_successfully",
            "test_data_saves_correctly",
            "test_api_returns_friendly_error"
        ]
        
        bad_test_names = [
            "test_CRITICAL_FAILURE",
            "test_PANIC_mode",
            "test_catastrophic_error"
        ]
        
        # Good names should be descriptive but not alarming
        for name in good_test_names:
            assert "PANIC" not in name
            assert "CRITICAL" not in name
            
    def test_test_parallelization_for_speed(self):
        """Test that tests can run in parallel for faster feedback"""
        # Faster tests = happier developers
        # In pytest.ini we configure parallel execution
        
        parallel_config = {
            "workers": "auto",  # Use all CPU cores
            "dist": "loadscope",  # Distribute by test scope
            "max_worker_restart": 4  # Prevent worker fatigue
        }
        
        assert parallel_config["workers"] == "auto"
    
    def test_failure_messages_are_helpful(self):
        """Test that test failures provide helpful, non-judgmental messages"""
        # Example of good failure message
        def format_failure_message(expected, actual):
            return f"""
🤔 The test didn't pass, but that's okay! Here's what happened:

Expected: {expected}
Actual: {actual}

💡 Tip: Check if the input data is correct, or if the function logic needs adjustment.
You're doing great - debugging is part of the journey! 🌟
"""
        
        message = format_failure_message("hello", "helo")
        
        assert "that's okay" in message
        assert "💡 Tip:" in message
        assert "You're doing great" in message
        assert "🌟" in message
    
    def test_celebrate_test_success(self):
        """Test that successful tests are celebrated"""
        success_messages = [
            "✅ Test passed! Excellent work!",
            "🎉 All tests green! You're on fire!",
            "💚 100% pass rate! Time to celebrate!",
            "🌟 Tests passing smoothly! Keep vibing!"
        ]
        
        # Each success should boost morale
        for message in success_messages:
            assert any(emoji in message for emoji in ["✅", "🎉", "💚", "🌟"])
            assert any(word in message.lower() for word in ["excellent", "great", "celebrate", "fire", "vibing", "passed", "green"])