# app/routers/departments.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.department import DepartmentCreate, DepartmentResponse
from app.services.department_service import DepartmentService
from app.deps import get_db

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.post("/", response_model=DepartmentResponse, status_code=201)
def create(department: DepartmentCreate, db: Session = Depends(get_db)):
    return DepartmentService.create(department, db)

@router.get("/", response_model=List[DepartmentResponse])
def list_departments(db: Session = Depends(get_db)):
    return DepartmentService.list_all(db)

@router.get("/{dept_id}", response_model=DepartmentResponse)
def get_department(dept_id: int, db: Session = Depends(get_db)):
    return DepartmentService.get_by_id(dept_id, db)  # ✅ Fixed: dept_id not id