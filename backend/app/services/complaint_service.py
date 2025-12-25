# app/services/complaint_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Tuple

from sqlalchemy import desc, asc
from datetime import datetime

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
    def list_all(
        db: Session, 
        user_id: int,
        status: str = None,
        urgency: str = None,
        from_date: str = None,
        to_date: str = None,
        sort: str = "-created_at",
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Complaint], int]:
        """
        Get user's complaints with filtering, sorting, pagination
        
        Args:
            db: Database session
            user_id: Current user's ID
            status: Filter by status (OPEN, ASSIGNED, RESOLVED, CLOSED)
            urgency: Filter by urgency (LOW, MEDIUM, HIGH, CRITICAL)
            from_date: Filter complaints from this date (YYYY-MM-DD)
            to_date: Filter complaints until this date (YYYY-MM-DD)
            sort: Sort field (created_at, -created_at, urgency, -urgency, etc.)
            page: Page number (1-indexed)
            page_size: Items per page (max 100)
        
        Returns:
            Tuple of (complaints_list, total_count)
        """

        # ✅ STEP 1: Validate pagination params
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        if page_size > 100:
            page_size = 100 # Cap at 100

        # ✅ STEP 2: Start base query (only user's complaints)
        query = db.query(Complaint).filter(Complaint.user_id == user_id)

        # ✅ STEP 3: Add filters (if provided)

        # Filter by status
        if status:
            query = query.filter(Complaint.status == status)

        # Filter by urgency
        if urgency:
            query = query.filter(Complaint.urgency == urgency)

        # Filter by from_date (complaints created on or after this date)
        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
                query = query.filter(Complaint.created_at >= from_date_obj)
            
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid from_date format. Use YYYY-MM-DD")

        # Filter by to_date (complaints created on or before this date)
        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
                query = query.filter(Complaint.created_at <= to_date_obj)
            
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid to_date format. Use YYYY-MM-DD")
        
        # ✅ STEP 4: Get total count BEFORE pagination
        total_count = query.count()

        # ✅ STEP 5: Apply sorting
        if sort == "created_at":
            query = query.order_by(asc(Complaint.created_at))
        elif sort == "-created_at":
            query = query.order_by(desc(Complaint.created_at))
        elif sort == "urgency":
            query = query.order_by(asc(Complaint.urgency))
        elif sort == "-urgency":
            query = query.order_by(desc(Complaint.urgency))
        elif sort == "status":
            query = query.order_by(asc(Complaint.status))
        elif sort == "-status":
            query = query.order_by(desc(Complaint.status))
        elif sort == "updated_at":
            query = query.order_by(asc(Complaint.updated_at))
        elif sort == "-updated_at":
            query = query.order_by(desc(Complaint.updated_at)) 
        else:
            # Default: newest first
            query = query.order_by(desc(Complaint.created_at))

        # ✅ STEP 6: Apply pagination
        skip = (page - 1) * page_size
        complaints = query.offset(skip).limit(page_size).all()

        # ✅ STEP 7: Return tuple (complaints, total_count)
        return complaints, total_count

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
