# tests/test_departments.py
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


def test_create_department_success():
    """Test creating a department with valid data"""
    response = client.post("/departments/", json={
        "name": "Sanitation Department"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Sanitation Department"


def test_create_department_short_name():
    """Test that short name is rejected"""
    response = client.post("/departments/", json={
        "name": "AB"
    })
    assert response.status_code == 422


def test_create_department_empty_name():
    """Test that empty name is rejected"""
    response = client.post("/departments/", json={
        "name": "   "
    })
    assert response.status_code == 422


def test_get_department_success():
    """Test getting a specific department"""
    # Create department first
    create_response = client.post("/departments/", json={
        "name": "Water Supply"
    })
    dept_id = create_response.json()["id"]
    
    # Get it
    response = client.get(f"/departments/{dept_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Water Supply"


def test_get_department_not_found():
    """Test getting non-existent department"""
    response = client.get("/departments/999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_list_departments():
    """Test listing all departments"""
    # Create two departments
    client.post("/departments/", json={"name": "Dept 1"})
    client.post("/departments/", json={"name": "Dept 2"})
    
    # List all
    response = client.get("/departments/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_departments_empty():
    """Test listing when no departments exist"""
    response = client.get("/departments/")
    assert response.status_code == 200
    assert len(response.json()) == 0