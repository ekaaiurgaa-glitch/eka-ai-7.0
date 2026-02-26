#!/usr/bin/env python
"""Run all 10/10 verification tests."""
import subprocess
import sys

def run(cmd, name):
    print(f"\n{'='*60}")
    print(f"Running: {name}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    tests = [
        ("pytest -v", "Unit & Integration Tests"),
        ("python tests/validate_ml.py", "ML Validation (80/20 split)"),
        ("python tests/chaos_test.py", "Chaos Test (Failover)"),
        ("locust -f tests/load_test.py --headless --users 100 --spawn-rate 10 --run-time 30s --host http://localhost:8000", "Load Test (100 users)"),
    ]
    
    results = []
    for cmd, name in tests:
        success = run(cmd, name)
        results.append((name, success))
    
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}")
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {name}")
    
    all_pass = all(success for _, success in results)
    
    if all_pass:
        print(f"\n🏆 10/10 VERIFIED")
        return 0
    else:
        print(f"\n⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
