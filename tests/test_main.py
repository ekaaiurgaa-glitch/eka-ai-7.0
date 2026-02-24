from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome to EKA-AI Platform" in data["message"]
    assert data["status"] == "operational"
