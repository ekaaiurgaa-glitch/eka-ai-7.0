#!/usr/bin/env python
"""
Load Test Runner - Validates throughput claims
Uses locust for distributed load testing with detailed reporting.
"""
import subprocess
import sys
import json
import time
from datetime import datetime

def run_load_test(target_rps: int = 100, duration: int = 30, users: int = 50):
    """
    Run a load test against the application.
    
    Args:
        target_rps: Target requests per second
        duration: Test duration in seconds
        users: Number of simulated users
    """
    print(f"\n{'='*60}")
    print(f"EKA-AI Load Test")
    print(f"{'='*60}")
    print(f"Target RPS: {target_rps}")
    print(f"Duration: {duration}s")
    print(f"Users: {users}")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    # Run locust in headless mode
    cmd = [
        "locust",
        "-f", "tests/load_test.py",
        "--headless",
        "-u", str(users),
        "-r", str(users // 5),  # Spawn rate
        "-t", f"{duration}s",
        "--host", "http://localhost:8000",
        "--csv", "load_test_results",
        "--csv-full-history"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=duration + 30)
        
        # Parse results
        stats_file = "load_test_results_stats.csv"
        try:
            with open(stats_file, 'r') as f:
                lines = f.readlines()
                if len(lines) > 1:
                    # Parse aggregate stats
                    headers = lines[0].strip().split(',')
                    for line in lines[1:]:
                        if 'Aggregated' in line:
                            values = line.strip().split(',')
                            stats = dict(zip(headers, values))
                            
                            print("\n📊 Load Test Results:")
                            print(f"   Total Requests: {stats.get('Request Count', 'N/A')}")
                            print(f"   Failures: {stats.get('Failure Count', '0')}")
                            print(f"   Avg Response Time: {stats.get('Average Response Time', 'N/A')}ms")
                            print(f"   95th Percentile: {stats.get('95%', 'N/A')}ms")
                            print(f"   99th Percentile: {stats.get('99%', 'N/A')}ms")
                            print(f"   RPS: {stats.get('Requests/s', 'N/A')}")
                            
                            # Validate
                            rps = float(stats.get('Requests/s', 0))
                            failures = int(stats.get('Failure Count', 0))
                            total = int(stats.get('Request Count', 1))
                            error_rate = (failures / total) * 100 if total > 0 else 0
                            
                            print(f"\n{'='*60}")
                            if rps >= target_rps * 0.8 and error_rate < 5:
                                print(f"✅ PASS: {rps:.1f} RPS achieved with {error_rate:.2f}% errors")
                                return True
                            else:
                                print(f"⚠️  WARNING: {rps:.1f} RPS with {error_rate:.2f}% errors")
                                return False
        except FileNotFoundError:
            print("⚠️  Results file not found - locust may not have completed")
            
        print(result.stdout[-500:] if result.stdout else "No output")
        if result.stderr:
            print(f"Errors: {result.stderr[-200:]}")
            
    except subprocess.TimeoutExpired:
        print("❌ Load test timed out")
        return False
    except FileNotFoundError:
        print("⚠️  Locust not available - install with: pip install locust")
        print("   Skipping load test validation")
        return None
        
    return False


def quick_throughput_test():
    """Quick throughput test using curl."""
    import asyncio
    import aiohttp
    import time
    
    async def make_requests(url: str, num_requests: int):
        async with aiohttp.ClientSession() as session:
            start = time.time()
            tasks = []
            for _ in range(num_requests):
                tasks.append(session.get(url))
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            elapsed = time.time() - start
            
            successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
            return successful, elapsed
    
    try:
        print("\n🚀 Quick Throughput Test (health endpoint)...")
        successful, elapsed = asyncio.run(make_requests("http://localhost:8000/health", 100))
        rps = successful / elapsed
        print(f"   {successful}/100 requests in {elapsed:.2f}s = {rps:.1f} RPS")
        return rps
    except Exception as e:
        print(f"⚠️  Quick test failed: {e}")
        return 0


if __name__ == "__main__":
    # Quick test first
    quick_throughput_test()
    
    # Full load test
    success = run_load_test(target_rps=100, duration=30, users=50)
    if success is False:
        sys.exit(1)
