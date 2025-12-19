from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.department import DepartmentCreate, DepartmentResponse
from app.models.departments import Department
from app.deps import get_db

router = APIRouter(
    prefix="/departments",
    tags=["Departments"]
)

@router.post("/", response_model=DepartmentResponse)
def create_department(department: DepartmentCreate, db: Session = Depends(get_db)):
    new_department = Department(name=department.name)

    db.add(new_department)
    db.commit()
    db.refresh(new_department)

    return new_department

@router.get("/", response_model=List[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    return db.query(Department).all()
