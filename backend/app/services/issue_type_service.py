# app/services/issue_type_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.issue_types import IssueType
from app.models.departments import Department
from app.schemas.issue_type import IssueTypeCreate, IssueTypeResponse


class IssueTypeService:

    @staticmethod
    def create(issue_type: IssueTypeCreate, db: Session) -> IssueType:
        """
        Create a new issue type
        - Check if department exists
        - Save to database
        - Handle errors gracefully
        """
        # ✅ CHECK: Department exists
        dept = db.query(Department).filter_by(id=issue_type.department_id).first()
        if not dept:
            raise HTTPException(status_code=404, detail="Department not found")
        
        try:
            new_issue_type = IssueType(
                name=issue_type.name,
                department_id=issue_type.department_id
            )
            db.add(new_issue_type)
            db.commit()
            db.refresh(new_issue_type)
            return new_issue_type
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create issue type")

    @staticmethod
    def list_all(db: Session) -> List[IssueType]:
        """Get all issue types"""
        return db.query(IssueType).all()

    @staticmethod
    def get_by_id(issue_id: int, db: Session) -> IssueType:
        """Get issue type by ID"""
        issue = db.query(IssueType).filter_by(id=issue_id).first()
        if not issue:
            raise HTTPException(status_code=404, detail="Issue type not found")
        return issue