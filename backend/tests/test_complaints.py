# tests/test_complaints.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Create and drop tables for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_data():
    """Create test data: department, issue type, and user"""
    # Create department
    dept_response = client.post("/departments/", json={
        "name": "Test Department"
    })
    dept_id = dept_response.json()["id"]
    
    # Create issue type
    issue_response = client.post("/issue-types/", json={
        "name": "Test Issue",
        "department_id": dept_id
    })
    issue_id = issue_response.json()["id"]
    
    # Create user
    user_response = client.post("/users/", json={
        "full_name": "John Doe",
        "phone_number": "+919876543210",
        "email": "john@example.com",
        "residential_address": "123 Main Street"
    })
    user_id = user_response.json()["id"]
    
    return {
        "user_id": user_id,
        "issue_id": issue_id,
        "dept_id": dept_id
    }


def test_create_complaint_success(test_data):
    """Test creating a complaint with valid data"""
    response = client.post("/complaints/", json={
        "user_id": test_data["user_id"],
        "issue_type_id": test_data["issue_id"],
        "description": "Garbage overflowing on Main Street for 3 days",
        "address": "123 Main Street"
    })
    assert response.status_code == 201
    assert response.json()["status"] == "OPEN"
    assert response.json()["urgency"] == "MEDIUM"


def test_create_complaint_invalid_user(test_data):
    """Test that invalid user is rejected"""
    response = client.post("/complaints/", json={
        "user_id": 999,
        "issue_type_id": test_data["issue_id"],
        "description": "Test complaint",
        "address": "123 Main Street"
    })
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_create_complaint_invalid_issue_type(test_data):
    """Test that invalid issue type is rejected"""
    response = client.post("/complaints/", json={
        "user_id": test_data["user_id"],
        "issue_type_id": 999,
        "description": "Test complaint",
        "address": "123 Main Street"
    })
    assert response.status_code == 404
    assert "Issue type not found" in response.json()["detail"]


def test_create_complaint_short_description(test_data):
    """Test that short description is rejected"""
    response = client.post("/complaints/", json={
        "user_id": test_data["user_id"],
        "issue_type_id": test_data["issue_id"],
        "description": "Bad",
        "address": "123 Main Street"
    })
    assert response.status_code == 422


def test_create_complaint_short_address(test_data):
    """Test that short address is rejected"""
    response = client.post("/complaints/", json={
        "user_id": test_data["user_id"],
        "issue_type_id": test_data["issue_id"],
        "description": "This is a valid complaint",
        "address": "AB"
    })
    assert response.status_code == 422


def test_get_complaint_success(test_data):
    """Test getting a specific complaint"""
    # Create complaint
    create_response = client.post("/complaints/", json={
        "user_id": test_data["user_id"],
        "issue_type_id": test_data["issue_id"],
        "description": "Test complaint description",
        "address": "123 Main Street"
    })
    complaint_id = create_response.json()["id"]
    
    # Get it
    response = client.get(f"/complaints/{complaint_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "OPEN"


def test_get_complaint_not_found():
    """Test getting non-existent complaint"""
    response = client.get("/complaints/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_list_complaints(test_data):
    """Test listing all complaints"""
    # Create two complaints
    client.post("/complaints/", json={
        "user_id": test_data["user_id"],
        "issue_type_id": test_data["issue_id"],
        "description": "First complaint description here",
        "address": "123 Main Street"
    })
    client.post("/complaints/", json={
        "user_id": test_data["user_id"],
        "issue_type_id": test_data["issue_id"],
        "description": "Second complaint description here",
        "address": "456 Oak Avenue"
    })
    
    # List all
    response = client.get("/complaints/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_complaints_empty():
    """Test listing when no complaints exist"""
    response = client.get("/complaints/")
    assert response.status_code == 200
    assert len(response.json()) == 0