from locust import HttpUser, task, between
import json

class EKAUser(HttpUser):
    wait_time = between(1, 2)
    
    def on_start(self):
        # Login
        response = self.client.post("/token", data={
            "username": "admin",
            "password": "admin"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def health_check(self):
        self.client.get("/health")
    
    @task(2)
    def list_vehicles(self):
        self.client.get("/api/v1/vehicles", headers=self.headers)
    
    @task(1)
    def chat_query(self):
        self.client.post("/api/v1/chat/query", headers=self.headers, json={
            "query": "brake noise when stopping",
            "vehicle": {"make": "Maruti", "model": "Swift", "year": 2019, "fuel": "petrol"}
        })
