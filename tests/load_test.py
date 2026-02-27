from locust import HttpUser, task, between
import random

class EKAWorkshopUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get token"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "admin@workshop.com",
            "password": "admin123"
        })
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            self.token = None
    
    @task(3)
    def health_check(self):
        """Health endpoint - most frequent"""
        self.client.get("/health")
    
    @task(2)
    def list_jobs(self):
        """List job cards"""
        if self.token:
            self.client.get("/api/v1/job-cards", headers={"Authorization": f"Bearer {self.token}"})
    
    @task(2)
    def dashboard(self):
        """Workshop dashboard"""
        if self.token:
            self.client.get("/api/v1/dashboard/workshop", headers={"Authorization": f"Bearer {self.token}"})
    
    @task(1)
    def list_vehicles(self):
        """List vehicles"""
        if self.token:
            self.client.get("/api/v1/vehicles", headers={"Authorization": f"Bearer {self.token}"})
    
    @task(1)
    def list_invoices(self):
        """List invoices"""
        if self.token:
            self.client.get("/api/v1/invoices", headers={"Authorization": f"Bearer {self.token}"})
