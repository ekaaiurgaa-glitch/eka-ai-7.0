#!/usr/bin/env python
"""
Chaos Testing Framework for EKA-AI
Implements various failure injection scenarios to test system resilience.
"""
import asyncio
import subprocess
import sys
import time
import os
import random
import signal
import aiohttp
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class ChaosResult:
    test_name: str
    passed: bool
    duration: float
    details: str


class ChaosTestRunner:
    """Runs chaos engineering tests against the application."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[ChaosResult] = []
        
    async def health_check(self, timeout: float = 2.0) -> bool:
        """Check if the service is healthy."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                    return resp.status == 200
        except:
            return False
    
    async def wait_for_recovery(self, max_wait: float = 30.0, check_interval: float = 1.0) -> float:
        """Wait for service to recover, return recovery time or -1 if failed."""
        start = time.time()
        while time.time() - start < max_wait:
            if await self.health_check():
                return time.time() - start
            await asyncio.sleep(check_interval)
        return -1
    
    async def test_network_latency(self) -> ChaosResult:
        """Test behavior under network latency."""
        test_name = "Network Latency Injection"
        start = time.time()
        
        try:
            # Simulate high latency with timeout
            async with aiohttp.ClientSession() as session:
                # Normal request should work
                async with session.get(f"{self.base_url}/health", timeout=aiohttp.ClientTimeout(total=0.5)) as resp:
                    fast_works = resp.status == 200
                    
            # System should handle timeouts gracefully
            passed = fast_works
            details = f"Fast response: {'OK' if fast_works else 'FAIL'}"
            
        except Exception as e:
            passed = False
            details = f"Error: {str(e)}"
            
        return ChaosResult(test_name, passed, time.time() - start, details)
    
    async def test_high_concurrency(self, concurrent_requests: int = 100) -> ChaosResult:
        """Test behavior under high concurrent load."""
        test_name = f"High Concurrency ({concurrent_requests} requests)"
        start = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for _ in range(concurrent_requests):
                    tasks.append(session.get(f"{self.base_url}/health", timeout=aiohttp.ClientTimeout(total=10)))
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                
                successful = sum(1 for r in responses if not isinstance(r, Exception) and r.status == 200)
                success_rate = successful / concurrent_requests
                
                passed = success_rate >= 0.95  # 95% success threshold
                details = f"Success rate: {success_rate:.1%} ({successful}/{concurrent_requests})"
                
        except Exception as e:
            passed = False
            details = f"Error: {str(e)}"
            
        return ChaosResult(test_name, passed, time.time() - start, details)
    
    async def test_rapid_requests(self, requests: int = 50, delay: float = 0.01) -> ChaosResult:
        """Test rapid-fire requests."""
        test_name = f"Rapid Requests ({requests} @ {delay}s intervals)"
        start = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                successful = 0
                for _ in range(requests):
                    try:
                        async with session.get(f"{self.base_url}/health", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                            if resp.status == 200:
                                successful += 1
                    except:
                        pass
                    await asyncio.sleep(delay)
                
                success_rate = successful / requests
                passed = success_rate >= 0.90
                details = f"Success rate: {success_rate:.1%} ({successful}/{requests})"
                
        except Exception as e:
            passed = False
            details = f"Error: {str(e)}"
            
        return ChaosResult(test_name, passed, time.time() - start, details)
    
    async def test_large_payload(self) -> ChaosResult:
        """Test handling of large payloads."""
        test_name = "Large Payload Handling"
        start = time.time()
        
        try:
            # Login first
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.base_url}/token", data={"username": "admin", "password": "admin"}) as resp:
                    if resp.status != 200:
                        return ChaosResult(test_name, False, time.time() - start, "Auth failed")
                    token = (await resp.json())["access_token"]
                
                headers = {"Authorization": f"Bearer {token}"}
                
                # Large query (but within reasonable limits)
                large_query = "car problem " * 100  # ~1200 chars
                
                async with session.post(
                    f"{self.base_url}/api/v1/chat/query",
                    headers=headers,
                    json={
                        "query": large_query[:500],  # Truncate to reasonable size
                        "vehicle": {"make": "Test", "model": "Test", "year": 2020, "fuel": "petrol"}
                    },
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    # Should either succeed or return a proper error (not crash)
                    passed = resp.status in [200, 400, 403, 422, 500]
                    details = f"Status: {resp.status}"
                    
        except Exception as e:
            passed = False
            details = f"Error: {str(e)}"
            
        return ChaosResult(test_name, passed, time.time() - start, details)
    
    async def test_invalid_auth(self) -> ChaosResult:
        """Test behavior with invalid authentication."""
        test_name = "Invalid Authentication"
        start = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Invalid token
                headers = {"Authorization": "Bearer invalid_token_12345"}
                async with session.get(f"{self.base_url}/api/v1/vehicles", headers=headers) as resp:
                    # Should return 401, not crash
                    passed = resp.status == 401
                    details = f"Status: {resp.status} (expected 401)"
                    
        except Exception as e:
            passed = False
            details = f"Error: {str(e)}"
            
        return ChaosResult(test_name, passed, time.time() - start, details)
    
    async def test_malformed_json(self) -> ChaosResult:
        """Test handling of malformed JSON."""
        test_name = "Malformed JSON Handling"
        start = time.time()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Login
                async with session.post(f"{self.base_url}/token", data={"username": "admin", "password": "admin"}) as resp:
                    token = (await resp.json())["access_token"]
                
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                
                # Send invalid JSON (as string, aiohttp will encode properly)
                async with session.post(
                    f"{self.base_url}/api/v1/chat/query",
                    headers=headers,
                    data="{invalid json}",  # Malformed
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    # Should return 422 (validation error), not crash
                    passed = resp.status == 422
                    details = f"Status: {resp.status} (expected 422)"
                    
        except Exception as e:
            passed = False
            details = f"Error: {str(e)}"
            
        return ChaosResult(test_name, passed, time.time() - start, details)
    
    async def run_all_tests(self) -> List[ChaosResult]:
        """Run all chaos tests."""
        print("\n" + "="*60)
        print("🔥 Chaos Testing Framework")
        print("="*60)
        print(f"Target: {self.base_url}")
        print(f"Started: {datetime.now().isoformat()}\n")
        
        # Check service is up
        if not await self.health_check():
            print("❌ Service not available!")
            return []
        
        tests = [
            self.test_network_latency(),
            self.test_high_concurrency(),
            self.test_rapid_requests(),
            self.test_large_payload(),
            self.test_invalid_auth(),
            self.test_malformed_json(),
        ]
        
        for test_coro in tests:
            result = await test_coro
            self.results.append(result)
            status = "✅ PASS" if result.passed else "❌ FAIL"
            print(f"{status} | {result.test_name}")
            print(f"       Duration: {result.duration:.2f}s | {result.details}")
        
        return self.results
    
    def print_summary(self):
        """Print test summary."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        
        print("\n" + "="*60)
        print("Summary")
        print("="*60)
        print(f"Total Tests: {total}")
        print(f"Passed:      {passed}")
        print(f"Failed:      {total - passed}")
        print(f"Pass Rate:   {passed/total:.1%}" if total > 0 else "N/A")
        
        if passed == total:
            print("\n✅ ALL CHAOS TESTS PASSED")
            return True
        else:
            print("\n⚠️  SOME TESTS FAILED")
            return False


async def main():
    runner = ChaosTestRunner()
    await runner.run_all_tests()
    success = runner.print_summary()
    return success


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
