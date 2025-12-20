import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.users import User

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Create and drop tables for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


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
    client.post("/users/", json={
        "full_name": "John Doe",
        "phone_number": "+919876543210",
        "email": "john@example.com",
        "residential_address": "123 Main St"
    })
    
    # Second user with same email
    response = client.post("/users/", json={
        "full_name": "Jane Doe",
        "phone_number": "+919999999999",
        "email": "john@example.com",  # Duplicate
        "residential_address": "456 Oak Avenue"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_get_user_not_found():
    """Test getting non-existent user"""
    response = client.get("/users/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]