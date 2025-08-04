#!/usr/bin/env python3
"""
Test runner with vibecoding feedback
"""

import subprocess
import sys

def run_tests():
    """Run tests and show results"""
    print("🚀 Running Zenith Coder tests with vibecoding v4.0...")
    print("=" * 60)
    
    # Run pytest with minimal output
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--no-cov", "-x"],
        capture_output=True,
        text=True
    )
    
    # Count results
    output = result.stdout
    passed = output.count(" PASSED")
    failed = output.count(" FAILED")
    errors = output.count(" ERROR")
    
    print(f"\n📊 Test Results:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  ⚠️  Errors: {errors}")
    
    # Show failures if any
    if failed > 0 or errors > 0:
        print("\n🔍 Issues found:")
        lines = output.split('\n')
        for line in lines:
            if "FAILED" in line or "ERROR" in line:
                print(f"  • {line.strip()}")
    
    # Vibe check
    total = passed + failed + errors
    if total > 0:
        vibe_score = int((passed / total) * 100)
        print(f"\n🌟 Vibe Score: {vibe_score}/100")
        
        if vibe_score >= 90:
            print("💚 Excellent vibe! Keep up the great work!")
        elif vibe_score >= 70:
            print("💛 Good vibe! A few tweaks needed.")
        else:
            print("🧡 Vibe needs boost! Let's fix those tests.")
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)