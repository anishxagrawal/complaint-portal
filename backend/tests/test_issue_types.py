# tests/test_issue_types.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, SessionLocal
from app.models.departments import Department

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_teardown():
    """Create and drop tables for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_department():
    """Create a test department"""
    response = client.post("/departments/", json={
        "name": "Test Department"
    })
    return response.json()["id"]


def test_create_issue_type_success(test_department):
    """Test creating an issue type with valid data"""
    response = client.post("/issue-types/", json={
        "name": "Garbage Collection",
        "department_id": test_department
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Garbage Collection"


def test_create_issue_type_invalid_department():
    """Test that invalid department is rejected"""
    response = client.post("/issue-types/", json={
        "name": "Test Issue",
        "department_id": 999
    })
    assert response.status_code == 404
    assert "Department not found" in response.json()["detail"]


def test_create_issue_type_short_name(test_department):
    """Test that short name is rejected"""
    response = client.post("/issue-types/", json={
        "name": "AB",
        "department_id": test_department
    })
    assert response.status_code == 422


def test_get_issue_type_success(test_department):
    """Test getting a specific issue type"""
    # Create issue type
    create_response = client.post("/issue-types/", json={
        "name": "Road Repair",
        "department_id": test_department
    })
    issue_id = create_response.json()["id"]
    
    # Get it
    response = client.get(f"/issue-types/{issue_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Road Repair"


def test_get_issue_type_not_found():
    """Test getting non-existent issue type"""
    response = client.get("/issue-types/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_list_issue_types(test_department):
    """Test listing all issue types"""
    # Create two issue types
    client.post("/issue-types/", json={
        "name": "Issue 1",
        "department_id": test_department
    })
    client.post("/issue-types/", json={
        "name": "Issue 2",
        "department_id": test_department
    })
    
    # List all
    response = client.get("/issue-types/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_issue_types_empty():
    """Test listing when no issue types exist"""
    response = client.get("/issue-types/")
    assert response.status_code == 200
    assert len(response.json()) == 0