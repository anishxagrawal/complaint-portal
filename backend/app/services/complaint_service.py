# app/services/complaint_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.models.complaints import Complaint
from app.models.users import User  # ✅ ADD
from app.models.issue_types import IssueType  # ✅ ADD
from app.schemas.complaint import ComplaintCreate  # ✅ Check filename


class ComplaintService:
    """Service layer for complaint operations"""
    
    @staticmethod
    def create(complaint_data: ComplaintCreate, db: Session) -> Complaint:
        """
        Create a new complaint
        - Check if user exists
        - Check if issue type exists
        - Save to database
        - Handle errors gracefully
        """
        # ✅ CHECK 1: User exists
        user = db.query(User).filter_by(id=complaint_data.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # ✅ CHECK 2: Issue type exists
        issue_type = db.query(IssueType).filter_by(id=complaint_data.issue_type_id).first()
        if not issue_type:
            raise HTTPException(status_code=404, detail="Issue type not found")
        
        # ✅ CHECK 3: Try-except for database errors
        try:
            new_complaint = Complaint(
                user_id=complaint_data.user_id,
                issue_type_id=complaint_data.issue_type_id,
                description=complaint_data.description,
                address=complaint_data.address
            )
            
            db.add(new_complaint)
            db.commit()
            db.refresh(new_complaint)
            
            return new_complaint
        
        except Exception as e:
            db.rollback()  # Undo any partial changes
            raise HTTPException(status_code=500, detail="Failed to create complaint")
    
    @staticmethod
    def get_by_id(complaint_id: int, db: Session) -> Complaint:
        """Get complaint by ID"""
        complaint = db.query(Complaint).filter_by(id=complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        return complaint
    
    @staticmethod
    def list_all(db: Session) -> List[Complaint]:
        """Get all complaints"""
        return db.query(Complaint).all()