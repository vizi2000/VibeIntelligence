#!/usr/bin/env python3
"""
Zenith Coder Test Runner
Following Directive 3: Testing & Reliability with >90% coverage
Includes vibe monitoring and well-being breaks
"""

import sys
import subprocess
import time
from datetime import datetime
import os

# Vibe-aware testing configuration
VIBE_CONFIG = {
    "max_duration_minutes": 30,  # Prevent test marathons
    "break_after_minutes": 15,   # Mandatory break reminder
    "celebration_threshold": 0.9,  # 90% pass rate
    "eco_mode": True              # Minimize resource usage
}


def print_vibe_banner():
    """Print encouraging banner before tests"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║                 🌟 Zenith Coder Test Suite 🌟                   ║
║                                                                 ║
║         "Testing with joy, sustainability, and care"            ║
║                                                                 ║
║  Remember: Take breaks, stay hydrated, and keep vibing! 💚     ║
╚════════════════════════════════════════════════════════════════╝
    """)


def run_test_suite(test_type: str = "all"):
    """Run tests with vibe monitoring"""
    
    start_time = time.time()
    
    # Test commands based on type
    commands = {
        "unit": [
            "pytest", "tests/unit", "-v", "--tb=short",
            "--cov=src", "--cov-report=term-missing",
            "--cov-report=html:htmlcov", "--cov-fail-under=90",
            "-m", "unit"
        ],
        "integration": [
            "pytest", "tests/integration", "-v",
            "-m", "integration"
        ],
        "diversity": [
            "pytest", "tests/diversity", "-v",
            "-m", "diversity"
        ],
        "vibe": [
            "pytest", "tests", "-v",
            "-m", "vibe"
        ],
        "all": [
            "pytest", "tests", "-v", "--tb=short",
            "--cov=src", "--cov-report=term-missing",
            "--cov-report=html:htmlcov", "--cov-report=xml",
            "--cov-fail-under=90",
            "--maxfail=10",  # Stop after 10 failures to prevent frustration
            "-n", "auto"     # Use all CPU cores for speed
        ],
        "quick": [
            "pytest", "tests/unit", "-v", "--tb=short",
            "-m", "not slow", "--maxfail=1",
            "-n", "auto"
        ]
    }
    
    if test_type not in commands:
        print(f"❌ Unknown test type: {test_type}")
        print(f"   Available: {', '.join(commands.keys())}")
        return False
    
    print(f"\n🚀 Running {test_type} tests...\n")
    
    # Set environment for testing
    env = os.environ.copy()
    env["ENVIRONMENT"] = "test"
    env["ENABLE_VIBECODING"] = "true"
    
    # Run tests
    try:
        result = subprocess.run(
            commands[test_type],
            env=env,
            capture_output=False
        )
        
        duration = time.time() - start_time
        
        # Check if break is needed
        if duration > VIBE_CONFIG["break_after_minutes"] * 60:
            print("\n" + "="*60)
            print("🌿 VIBE CHECK: You've been testing for a while!")
            print("   Time for a 5-minute break. Stretch, hydrate, breathe!")
            print("="*60 + "\n")
        
        # Show results with encouragement
        if result.returncode == 0:
            print_success_message(duration)
            return True
        else:
            print_encouragement_message()
            return False
            
    except KeyboardInterrupt:
        print("\n\n💫 Test run interrupted - that's okay! Take a break if needed.")
        return False
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        print("   Don't worry, we'll figure this out together!")
        return False


def print_success_message(duration: float):
    """Print celebration message for successful tests"""
    minutes = duration / 60
    
    messages = [
        f"🎉 All tests passed in {minutes:.1f} minutes! You're amazing!",
        f"✨ Tests completed successfully! Great job!",
        f"💚 100% success! Your code is vibing high!",
        f"🌟 Excellent work! All tests green in {minutes:.1f} minutes!"
    ]
    
    import random
    print("\n" + "="*60)
    print(random.choice(messages))
    print("="*60 + "\n")
    
    # Eco impact
    co2_saved = minutes * 0.001  # Rough estimate
    print(f"🌱 Eco-impact: ~{co2_saved:.3f}kg CO2 saved by efficient testing")


def print_encouragement_message():
    """Print encouragement for failed tests"""
    messages = [
        "💝 Some tests need attention, but you've got this!",
        "🌟 Every failed test is a learning opportunity!",
        "🤗 Don't worry - debugging is part of the journey!",
        "💪 You're one step closer to the solution!"
    ]
    
    import random
    print("\n" + "="*60)
    print(random.choice(messages))
    print("\n🔍 Tips for debugging:")
    print("   1. Check the test output above for specific errors")
    print("   2. Run individual failed tests with: pytest path/to/test.py::test_name")
    print("   3. Take a short break and come back with fresh eyes")
    print("   4. Remember: You're doing great!")
    print("="*60 + "\n")


def generate_coverage_report():
    """Generate and display coverage report"""
    print("\n📊 Generating coverage report...")
    
    try:
        # Generate HTML report
        subprocess.run(["coverage", "html"], capture_output=True)
        
        # Try to open in browser
        import webbrowser
        webbrowser.open("htmlcov/index.html")
        
        print("✅ Coverage report opened in browser!")
        print("   Also available at: htmlcov/index.html")
        
    except Exception as e:
        print("⚠️ Could not generate coverage report:", e)


def main():
    """Main test runner with CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run Zenith Coder tests with vibe monitoring 🌟"
    )
    parser.add_argument(
        "type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "diversity", "vibe", "quick"],
        help="Type of tests to run"
    )
    parser.add_argument(
        "--no-vibe",
        action="store_true",
        help="Skip vibe monitoring (not recommended!)"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report after tests"
    )
    
    args = parser.parse_args()
    
    # Show vibe banner unless disabled
    if not args.no_vibe:
        print_vibe_banner()
    
    # Record start time for well-being monitoring
    session_start = datetime.now()
    
    # Run tests
    success = run_test_suite(args.type)
    
    # Generate coverage if requested
    if args.coverage and success:
        generate_coverage_report()
    
    # Final vibe check
    session_duration = (datetime.now() - session_start).total_seconds() / 60
    
    if session_duration > VIBE_CONFIG["max_duration_minutes"]:
        print("\n" + "🌺"*30)
        print("🎯 You've been testing for a while - amazing dedication!")
        print("   Consider taking a longer break to recharge.")
        print("   Your well-being is more important than any code! 💖")
        print("🌺"*30 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()