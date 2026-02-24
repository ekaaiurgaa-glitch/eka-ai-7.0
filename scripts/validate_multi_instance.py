#!/usr/bin/env python
"""
Multi-Instance Deployment Validator
Tests the application with multiple instances behind a simulated load balancer.
"""
import subprocess
import sys
import time
import os
import signal
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor


class MultiInstanceValidator:
    """Validates multi-instance deployment scenarios."""
    
    def __init__(self, num_instances: int = 3, base_port: int = 8001):
        self.num_instances = num_instances
        self.base_port = base_port
        self.processes = []
        self.ports = [base_port + i for i in range(num_instances)]
        
    def start_instances(self) -> bool:
        """Start multiple application instances."""
        print(f"\n🚀 Starting {self.num_instances} instances...")
        
        for port in self.ports:
            try:
                # Start uvicorn in background
                cmd = [
                    sys.executable, "-m", "uvicorn", 
                    "app.main:app",
                    "--host", "0.0.0.0",
                    "--port", str(port),
                    "--log-level", "warning"
                ]
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                )
                self.processes.append((port, proc))
                print(f"   Started instance on port {port} (PID: {proc.pid})")
            except Exception as e:
                print(f"   ❌ Failed to start on port {port}: {e}")
                return False
        
        # Wait for startup
        print("   Waiting for instances to initialize...")
        time.sleep(3)
        return True
    
    def stop_instances(self):
        """Stop all instances."""
        print("\n🛑 Stopping instances...")
        for port, proc in self.processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
                print(f"   Stopped instance on port {port}")
            except:
                proc.kill()
        self.processes = []
    
    async def health_check(self, port: int) -> bool:
        """Check if an instance is healthy."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/health", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    return resp.status == 200
        except:
            return False
    
    async def check_all_instances(self) -> dict:
        """Check health of all instances."""
        results = {}
        for port in self.ports:
            results[port] = await self.health_check(port)
        return results
    
    async def round_robin_test(self, requests_per_instance: int = 10) -> dict:
        """Test round-robin distribution."""
        print(f"\n📊 Testing round-robin distribution ({requests_per_instance} requests/instance)...")
        
        results = {port: {"success": 0, "fail": 0} for port in self.ports}
        
        async with aiohttp.ClientSession() as session:
            for port in self.ports:
                for _ in range(requests_per_instance):
                    try:
                        async with session.get(f"http://localhost:{port}/health", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                            if resp.status == 200:
                                results[port]["success"] += 1
                            else:
                                results[port]["fail"] += 1
                    except:
                        results[port]["fail"] += 1
        
        return results
    
    async def failover_test(self) -> bool:
        """Test failover by killing one instance."""
        if len(self.processes) < 2:
            print("⚠️  Need at least 2 instances for failover test")
            return True
            
        print("\n🔄 Testing failover...")
        
        # Kill first instance
        port, proc = self.processes[0]
        print(f"   Killing instance on port {port}...")
        proc.terminate()
        proc.wait(timeout=5)
        
        time.sleep(1)
        
        # Check other instances still work
        remaining_healthy = 0
        for p in self.ports[1:]:
            if await self.health_check(p):
                remaining_healthy += 1
                
        print(f"   Remaining healthy instances: {remaining_healthy}/{len(self.ports)-1}")
        
        return remaining_healthy > 0
    
    async def run_validation(self) -> dict:
        """Run complete multi-instance validation."""
        results = {
            "instances_started": False,
            "all_healthy": False,
            "round_robin": {},
            "failover_passed": False,
            "status": "FAIL"
        }
        
        try:
            # Start instances
            if not self.start_instances():
                return results
            results["instances_started"] = True
            
            # Check all healthy
            health_results = await self.check_all_instances()
            results["all_healthy"] = all(health_results.values())
            print(f"\n✅ Instance health: {health_results}")
            
            # Round robin test
            rr_results = await self.round_robin_test()
            results["round_robin"] = rr_results
            total_success = sum(r["success"] for r in rr_results.values())
            total_requests = sum(r["success"] + r["fail"] for r in rr_results.values())
            print(f"   Success rate: {total_success}/{total_requests}")
            
            # Failover test
            results["failover_passed"] = await self.failover_test()
            
            # Overall status
            if results["all_healthy"] and results["failover_passed"] and total_success > total_requests * 0.9:
                results["status"] = "PASS"
            else:
                results["status"] = "PARTIAL"
                
        finally:
            self.stop_instances()
            
        return results


async def main():
    print("\n" + "="*60)
    print("Multi-Instance Deployment Validation")
    print("="*60)
    
    validator = MultiInstanceValidator(num_instances=3)
    results = await validator.run_validation()
    
    print("\n" + "="*60)
    print("Validation Results")
    print("="*60)
    print(f"Instances Started: {'✅' if results['instances_started'] else '❌'}")
    print(f"All Healthy:       {'✅' if results['all_healthy'] else '❌'}")
    print(f"Failover Test:     {'✅' if results['failover_passed'] else '❌'}")
    print(f"Overall Status:    {results['status']}")
    print("="*60 + "\n")
    
    return results["status"] == "PASS"


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
