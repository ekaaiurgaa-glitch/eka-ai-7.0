"""Smoke tests for staging/production deployment verification."""
import os
import sys
import requests
import pytest


BASE_URL = os.getenv("SMOKE_TEST_URL", "http://localhost:8000")


def test_root_endpoint():
    """Verify root endpoint returns 200."""
    response = requests.get(f"{BASE_URL}/", timeout=10)
    assert response.status_code == 200, f"Root failed: {response.status_code}"
    data = response.json()
    assert "status" in data
    assert data["status"] == "operational"
    print("✅ Root endpoint OK")


def test_health_endpoint():
    """Verify health check endpoint."""
    response = requests.get(f"{BASE_URL}/health", timeout=10)
    assert response.status_code == 200, f"Health failed: {response.status_code}"
    data = response.json()
    assert data.get("status") == "healthy"
    print("✅ Health endpoint OK")


def test_chat_examples():
    """Verify chat examples endpoint."""
    response = requests.get(f"{BASE_URL}/api/v1/chat/examples", timeout=10)
    assert response.status_code == 200, f"Chat examples failed: {response.status_code}"
    data = response.json()
    assert "example1" in data
    print("✅ Chat examples OK")


def test_openapi_docs():
    """Verify OpenAPI docs are accessible."""
    response = requests.get(f"{BASE_URL}/docs", timeout=10)
    assert response.status_code == 200, f"Docs failed: {response.status_code}"
    print("✅ OpenAPI docs OK")


if __name__ == "__main__":
    print(f"Running smoke tests against: {BASE_URL}")
    try:
        test_root_endpoint()
        test_health_endpoint()
        test_chat_examples()
        test_openapi_docs()
        print("\n✅ All smoke tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Smoke test failed: {e}")
        sys.exit(1)
    except requests.RequestException as e:
        print(f"\n❌ Connection error: {e}")
        sys.exit(1)
