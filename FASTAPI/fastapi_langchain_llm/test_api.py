import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_chat_unauthorized():
    response = client.post("/chat", json={"message": "Hello"})
    assert response.status_code == 401
