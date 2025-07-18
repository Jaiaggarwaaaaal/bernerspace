import pytest
from fastapi.testclient import TestClient
from core.main import app
from src.config.auth import get_current_user_email

async def override_get_current_user_email():
    return "test@example.com"

app.dependency_overrides[get_current_user_email] = override_get_current_user_email

client = TestClient(app)

def test_list_projects():
    response = client.get("/projects/")
    assert response.status_code == 200
    assert response.json() == []