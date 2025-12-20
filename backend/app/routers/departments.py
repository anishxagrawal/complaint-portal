from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.department import DepartmentCreate, DepartmentResponse
from app.models.departments import Department
from app.deps import get_db

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/", response_model=DepartmentResponse, status_code=201)
def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    try:
        new_department = Department(name=department.name)
        db.add(new_department)
        db.commit()
        db.refresh(new_department)
        return new_department
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create department")

@router.get("/", response_model=List[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()

@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(dept_id: int, db: Session = Depends(get_db)):
    dept = db.query(Department).filter_by(id=dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept