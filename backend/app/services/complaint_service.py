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
    def create(complaint_data: ComplaintCreate, db: Session,user_id: int) -> Complaint:
        """
        Create a new complaint
        - Check if user exists
        - Check if issue type exists
        - Save to database
        - Handle errors gracefully
        """

        # ✅ CHECK 1: User exists (use user_id parameter)
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # ✅ CHECK 2: Issue type exists
        issue_type = db.query(IssueType).filter_by(id=complaint_data.issue_type_id).first()
        if not issue_type:
            raise HTTPException(status_code=404, detail="Issue type not found")
        
        # ✅ CHECK 3: Try-except for database errors
        try:
            new_complaint = Complaint(
                user_id=user_id, # ← Use parameter, NOT complaint_data.user_id
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
    def get_by_id(complaint_id: int, db: Session, user_id: int) -> Complaint:
        """Get complaint by ID"""
        complaint = db.query(Complaint).filter(
                Complaint.id == complaint_id,
                Complaint.user_id == user_id # ← NEW: Check ownership
            ).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        return complaint
    
    @staticmethod
    def list_all(db: Session, user_id: int) -> List[Complaint]:
        """Get all complaints"""
        return db.query(Complaint).filter(
            Complaint.user_id == user_id
        ).all()

    @staticmethod
    def update(complaint_id: int, complaint_data: ComplaintCreate, db: Session, user_id: int) -> Complaint:
        """Update a complaint - only if user owns it"""

        # Check if complaint exists and belong to user
        complaint = db.query(Complaint). filter(
            Complaint.id == complaint_id,
            Complaint.user_id == user_id
        ).first()

        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found or unauthorized")
      
        # Check if new issue_type_is is valid
        if complaint_data.issue_type_id != complaint.issue_type_id:
            issue_type = db.query(IssueType).filter_by(id=complaint_data.issue_type_id).first()
            if not issue_type:
                raise HTTPException(status_code=404, detail="Issue type not found")
        

        try:
            # Update fields
            complaint.issue_type_id = complaint_data.issue_type_id
            complaint.description = complaint_data.description
            complaint.address = complaint_data.address

            db.commit()
            db.refresh(complaint)
            return complaint

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to update complaint")
        
    @staticmethod
    def delete(complaint_id: int, db: Session, user_id: int) -> dict:
        """Delete a complaint - only if user owns it"""

        # Check if complaint exists and belong to user
        complaint = db.query(Complaint).filter(
            Complaint.id == complaint_id,
            Complaint.user_id == user_id
        ).first()

        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found or unauthorized")
        
        try:
            db.delete(complaint)
            db.commit()
            return {"message": "Complaint deleted successfully"}
        
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete complaint")
