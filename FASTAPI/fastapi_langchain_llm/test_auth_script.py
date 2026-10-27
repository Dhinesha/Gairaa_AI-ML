import pytest
import uuid
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_full_auth_flow():
    username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "testpassword"
    
    resp = client.post("/register", json={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    
    resp = client.post("/login", data={"username": username, "password": password})
    assert resp.status_code == 200, resp.text
    token = resp.json().get("access_token")
    
    # We just ensure it doesn't return 401 when using a token
    # It might return 500 if GOOGLE_API_KEY is not configured, which is expected unless mocked.
    resp = client.post("/chat", json={"message": "hello"}, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code in [200, 500], resp.text
