# app/services/complaint_service.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Tuple, Optional
from sqlalchemy import desc, asc, or_
from datetime import datetime
from fuzzywuzzy import fuzz
from app.utils.audit_logger import audit_logger

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

            audit_logger.log_action(
                user_id=user_id,
                action="CREATE",
                resource_type="COMPLAINT",
                resource_id=new_complaint.id
            )
            
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

            audit_logger.log_action(
                user_id=user.id,
                action="UPDATE",
                resource_type="COMPLAINT",
                resource_id=complaint_id
            )

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
            
            audit_logger.log_action(
                user_id=user.id,
                action="DELETE",
                resource_type="COMPLAINT",
                resource_id=complaint_id
            )

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

    # ADD THIS METHOD TO YOUR EXISTING ComplaintService class

    @staticmethod
    def assign_complaint(
        complaint_id: int,
        department: str,
        db: Session,
        user: User
    ) -> Complaint:
        """
        Assign complaint to a department (ADMIN + DEPT_MGR)
        
        Role Logic:
        - ADMIN: Can assign to any department
        - DEPARTMENT_MANAGER: Can only assign to their own department
        - USER: Cannot assign (403 error)
        """
        from app.utils.audit_logger import audit_logger
        
        # ✅ ROLE CHECK: Only ADMIN and DEPT_MGR can assign
        if user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_MANAGER]:
            raise HTTPException(
                status_code=403,
                detail="Only admins and department managers can assign complaints"
            )
        
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        # ✅ DEPT_MGR can only assign to THEIR department
        if user.role == UserRole.DEPARTMENT_MANAGER:
            if department != user.department:
                raise HTTPException(
                    status_code=403,
                    detail="Department managers can only assign to their own department"
                )
        
        try:
            old_department = complaint.department
            complaint.department = department
            db.commit()
            db.refresh(complaint)
            
            # ✅ AUDIT LOG
            audit_logger.log_action(
                user_id=user.id,
                action="ASSIGN",
                resource_type="COMPLAINT",
                resource_id=complaint_id,
                details=f"Assigned from {old_department} to {department}"
            )
            
            return complaint

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail="Failed to assign complaint")


# Initialize service instance
complaint_service = ComplaintService()