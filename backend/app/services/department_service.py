# app/services/department_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.departments import Department
from app.schemas.department import DepartmentCreate, DepartmentResponse


class DepartmentService:

    @staticmethod
    def create(department: DepartmentCreate, db: Session) -> Department:
        """Create a new department"""
        try:
            new_department = Department(name=department.name)
            db.add(new_department)
            db.commit()
            db.refresh(new_department)
            return new_department
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create department")

    @staticmethod
    def list_all(db: Session) -> List[Department]:
        """Get all departments"""
        return db.query(Department).all()

    @staticmethod
    def get_by_id(dept_id: int, db: Session) -> Department:
        """Get department by ID"""
        dept = db.query(Department).filter_by(id=dept_id).first()
        if not dept:
            raise HTTPException(status_code=404, detail="Department not found")
        return dept