# tests/test_users.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_user_success():
    """Test creating a user with valid data"""
    response = client.post("/users/", json={
        "full_name": "John Doe",
        "phone_number": "+919876543210",
        "email": "john@example.com",
        "residential_address": "123 Main St"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "john@example.com"

def test_create_user_duplicate_email():
    """Test that duplicate email is rejected"""
    # First user
    client.post("/users/", json={...})
    
    # Second user with same email
    response = client.post("/users/", json={...})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_get_user_not_found():
    """Test getting non-existent user"""
    response = client.get("/users/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]