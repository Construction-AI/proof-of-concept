import requests
from typing import Optional, Any

class APIClient:
    def __init__(self, base_url: str = "http://backend:8000/api/v1", token: Optional[str] = None):
        self.base_url = base_url
        self.token = token

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    def get_me(self):
        return requests.get(f"{self.base_url}/auth/me", headers=self.headers)

    def login(self, username: str, password: str):
        payload = {"username": username, "password": password}
        return requests.post(f"{self.base_url}/auth/token", data=payload)

    def get_projects(self):
        return requests.get(f"{self.base_url}/projects/", headers=self.headers)
    
    def post_rag(self, endpoint: str, payload: dict[str, Any]):
        return requests.post(f"{self.base_url}{endpoint}", json=payload, headers=self.headers)
    
    def get_health(self):
        return requests.get(f"{self.base_url}/health")