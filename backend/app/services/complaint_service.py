# app/services/complaint_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
from sqlalchemy import desc, asc, or_
from datetime import datetime
from fuzzywuzzy import fuzz

from app.models.complaints import Complaint
from app.models.users import User
from app.models.issue_types import IssueType
from app.schemas.complaint import ComplaintCreate
from app.enums import UserRole


class ComplaintService:
    """Service layer for complaint operations"""
    
    @staticmethod
    def create(complaint_data: ComplaintCreate, db: Session, user_id: int) -> Complaint:
        """
        Create a new complaint (all authenticated users can create)
        """
        # Check if user exists
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if issue type exists
        issue_type = db.query(IssueType).filter_by(id=complaint_data.issue_type_id).first()
        if not issue_type:
            raise HTTPException(status_code=404, detail="Issue type not found")
        
        try:
            new_complaint = Complaint(
                user_id=user_id,
                issue_type_id=complaint_data.issue_type_id,
                description=complaint_data.description,
                address=complaint_data.address
            )
            
            db.add(new_complaint)
            db.commit()
            db.refresh(new_complaint)
            
            return new_complaint
        
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to create complaint")
    
    @staticmethod
    def get_by_id(complaint_id: int, db: Session, user: User) -> Complaint:
        """
        Get complaint by ID (ownership checked by middleware)
        This method should NOT be called directly - use require_complaint_access middleware
        """
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        return complaint
    
    @staticmethod
    def _apply_role_filter(query, user: User):
        """
        Apply role-based filtering to query (internal helper)
        
        - ADMIN: No filter (sees everything)
        - USER: Only their own complaints
        - DEPARTMENT_MANAGER: Only their department
        """
        if user.role == UserRole.ADMIN:
            # Admin sees all - no filter
            return query
        
        elif user.role == UserRole.USER:
            # User sees only their own
            return query.filter(Complaint.user_id == user.id)
        
        elif user.role == UserRole.DEPARTMENT_MANAGER:
            # Manager sees only their department
            return query.filter(Complaint.department == user.department)
        
        # Fallback: no access
        return query.filter(Complaint.id == -1)  # Will return empty
    
    @staticmethod
    def list_all(
        db: Session,
        user: User,  # ✅ CHANGED: Pass entire user object, not just user_id
        status: Optional[str] = None,
        urgency: Optional[str] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        sort: str = "-created_at",
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Complaint], int]:
        """
        List complaints with role-based filtering
        """
        # Validate pagination
        if page < 1:
            page = 1
        if page_size < 1:
            page_size = 20
        if page_size > 100:
            page_size = 100

        # Start base query
        query = db.query(Complaint)
        
        # ✅ APPLY ROLE-BASED FILTER (DB level)
        query = ComplaintService._apply_role_filter(query, user)

        # Apply other filters
        if status:
            query = query.filter(Complaint.status == status)

        if urgency:
            query = query.filter(Complaint.urgency == urgency)

        if from_date:
            try:
                from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
                query = query.filter(Complaint.created_at >= from_date_obj)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid from_date format. Use YYYY-MM-DD")

        if to_date:
            try:
                to_date_obj = datetime.strptime(to_date, "%Y-%m-%d").date()
                query = query.filter(Complaint.created_at <= to_date_obj)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid to_date format. Use YYYY-MM-DD")
        
        # Get total count BEFORE pagination
        total_count = query.count()

        # Apply sorting
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
            query = query.order_by(desc(Complaint.created_at))

        # Apply pagination
        skip = (page - 1) * page_size
        complaints = query.offset(skip).limit(page_size).all()

        return complaints, total_count

    @staticmethod
    def update(
        complaint_id: int,
        complaint_data: ComplaintCreate,
        db: Session,
        user: User  # ✅ CHANGED: Pass entire user object
    ) -> Complaint:
        """
        Update a complaint (ownership verified by middleware)
        """
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
      
        # Check if new issue_type_id is valid
        if complaint_data.issue_type_id != complaint.issue_type_id:
            issue_type = db.query(IssueType).filter_by(id=complaint_data.issue_type_id).first()
            if not issue_type:
                raise HTTPException(status_code=404, detail="Issue type not found")
        
        try:
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
    def delete(complaint_id: int, db: Session, user: User) -> dict:
        """
        Delete a complaint (only ADMIN via middleware)
        """
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()

        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        try:
            db.delete(complaint)
            db.commit()
            return {"message": "Complaint deleted successfully"}
        
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to delete complaint")

    @staticmethod
    def search(
        db: Session,
        user: User,  # ✅ CHANGED: Pass entire user object
        query: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[Complaint], int]:
        """
        Search complaints using fuzzy matching (role-aware)
        """
        if not query or not query.strip():
            return [], 0
        
        query = query.strip().lower()

        # Get complaints based on role
        base_query = db.query(Complaint)
        base_query = ComplaintService._apply_role_filter(base_query, user)
        all_complaints = base_query.all()

        # Calculate fuzzy match scores
        matches = []
        for complaint in all_complaints:
            description_score = 0
            address_score = 0

            if complaint.description:
                description_score = fuzz.token_set_ratio(
                    query,
                    complaint.description.lower()
                )

            if complaint.address:
                address_score = fuzz.token_set_ratio(
                    query,
                    complaint.address.lower()
                )

            max_score = max(description_score, address_score)

            if max_score > 70:
                matches.append({
                    'complaint': complaint,
                    'score': max_score
                })

        # Sort by relevance
        matches.sort(key=lambda x: x['score'], reverse=True)
        matched_complaints = [m['complaint'] for m in matches]

        # Total count
        total_count = len(matched_complaints)

        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_complaints = matched_complaints[start_idx:end_idx]

        return paginated_complaints, total_count


# Initialize service instance
complaint_service = ComplaintService()