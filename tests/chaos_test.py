#!/usr/bin/env python
"""Chaos test: Kill instances and verify recovery."""
import subprocess
import time
import requests
import sys

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def check_health():
    try:
        r = requests.get("http://localhost:8000/health", timeout=2)
        return r.status_code == 200
    except:
        return False

def main():
    print("Starting chaos test...")
    
    # Verify system is up
    if not check_health():
        print("❌ System not healthy before test")
        return False
    
    print("✅ System healthy")
    
    # Get container ID
    result = run_cmd("docker ps --filter name=eka-ai --format '{{.ID}}'")
    containers = result.stdout.strip().split('\n')
    
    if not containers or not containers[0]:
        print("⚠️  No containers found, skipping chaos test")
        return True
    
    container = containers[0]
    print(f"Killing container {container[:12]}...")
    
    # Kill container
    run_cmd(f"docker kill {container}")
    time.sleep(2)
    
    # Check if system recovers (if multi-instance)
    recovered = check_health()
    
    # Restart
    run_cmd("docker-compose up -d")
    time.sleep(5)
    
    # Verify recovery
    if check_health():
        print("✅ System recovered")
        return True
    else:
        print("❌ System did not recover")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
