# app/services/workflow_service.py
"""
Workflow Service - Handles complaint status transitions and lifecycle management.

This service manages:
- Status changes with validation
- Auto-assignment to departments
- Status history tracking
- Workflow business rules
"""

from fastapi import HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.models.complaints import Complaint
from app.models.complaint_status_history import ComplaintStatusHistory
from app.models.users import User
from app.models.issue_types import IssueType
from app.models.departments import Department
from app.enums import ComplaintStatus, is_valid_transition, UserRole
from app.utils.audit_logger import audit_logger
from app.core.logging import get_logger

logger = get_logger(__name__)


class WorkflowService:
    """Service for managing complaint workflow and status transitions"""
    
    @staticmethod
    def change_status(
        complaint_id: int,
        new_status: str,
        user: User,
        db: Session,
        comment: Optional[str] = None,
        reason: Optional[str] = None
    ) -> Complaint:
        """
        Change complaint status with validation and history tracking.
        
        Args:
            complaint_id: ID of complaint to update
            new_status: New status to set
            user: User making the change
            db: Database session
            comment: Optional comment about the change
            reason: Optional reason (for rejections, etc.)
            
        Returns:
            Updated complaint
            
        Raises:
            HTTPException: If transition is invalid or user lacks permission
        """
        # Get complaint
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail=f"Complaint {complaint_id} not found")
        
        # Validate status transition
        current_status = complaint.status
        
        if not is_valid_transition(current_status, new_status):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status transition from '{current_status}' to '{new_status}'"
            )
        
        try:
            # Store old status
            old_status = complaint.status
            
            # Update complaint status
            complaint.status = new_status.lower()
            complaint.updated_at = datetime.utcnow()
            
            # Handle status-specific updates
            if new_status == ComplaintStatus.ASSIGNED.value:
                complaint.assigned_at = datetime.utcnow()
                # Auto-assign to department based on issue type
                if not complaint.department:
                    WorkflowService._auto_assign_department(complaint, db)
            
            elif new_status == ComplaintStatus.IN_PROGRESS.value:
                # Track who started working on it
                if not complaint.assigned_to:
                    complaint.assigned_to = user.id
            
            elif new_status == ComplaintStatus.RESOLVED.value:
                complaint.resolved_at = datetime.utcnow()
                complaint.resolved_by = user.id
                if comment:
                    complaint.resolution_notes = comment
            
            # Create history entry
            history = ComplaintStatusHistory(
                complaint_id=complaint_id,
                old_status=old_status,
                new_status=new_status.lower(),
                changed_by=user.id,
                comment=comment,
                reason=reason,
                assigned_to=complaint.assigned_to,
                changed_at=datetime.utcnow()
            )
            
            db.add(history)
            db.commit()
            db.refresh(complaint)
            
            # Audit log
            audit_logger.log_action(
                user_id=user.id,
                action="STATUS_CHANGE",
                resource_type="COMPLAINT",
                resource_id=complaint_id,
                details=f"{old_status} → {new_status}"
            )
            
            logger.info(
                f"Complaint #{complaint_id} status changed: "
                f"{old_status} → {new_status} by user {user.id}"
            )
            
            return complaint
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to change status for complaint {complaint_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to change status: {str(e)}"
            )
    
    @staticmethod
    def _auto_assign_department(complaint: Complaint, db: Session) -> None:
        """
        Auto-assign complaint to department based on issue type.
        
        Args:
            complaint: Complaint to assign
            db: Database session
        """
        try:
            # Get issue type
            issue_type = db.query(IssueType).filter(
                IssueType.id == complaint.issue_type_id
            ).first()
            
            if issue_type and issue_type.department_id:
                # Get department name
                department = db.query(Department).filter(
                    Department.id == issue_type.department_id
                ).first()
                
                if department:
                    complaint.department = department.name
                    logger.info(
                        f"Auto-assigned complaint #{complaint.id} to "
                        f"department: {department.name}"
                    )
        except Exception as e:
            logger.warning(f"Failed to auto-assign department: {e}")
            # Don't fail the whole operation if auto-assign fails
    
    @staticmethod
    def assign_to_officer(
        complaint_id: int,
        officer_id: int,
        user: User,
        db: Session
    ) -> Complaint:
        """
        Assign complaint to a specific officer.
        
        Args:
            complaint_id: Complaint to assign
            officer_id: Officer to assign to
            user: User making the assignment
            db: Database session
            
        Returns:
            Updated complaint
        """
        # Check permissions
        if user.role not in [UserRole.ADMIN, UserRole.DEPARTMENT_MANAGER]:
            raise HTTPException(
                status_code=403,
                detail="Only admins and department managers can assign to officers"
            )
        
        # Get complaint
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        # Get officer
        officer = db.query(User).filter(User.id == officer_id).first()
        if not officer:
            raise HTTPException(status_code=404, detail="Officer not found")
        
        # Dept managers can only assign to their own department
        if user.role == UserRole.DEPARTMENT_MANAGER:
            if officer.department != user.department:
                raise HTTPException(
                    status_code=403,
                    detail="Can only assign to officers in your department"
                )
        
        try:
            old_assignee = complaint.assigned_to
            complaint.assigned_to = officer_id
            complaint.assigned_at = datetime.utcnow()
            
            # If not yet assigned, change status to assigned
            if complaint.status == ComplaintStatus.OPEN.value:
                complaint.status = ComplaintStatus.ASSIGNED.value
            
            db.commit()
            db.refresh(complaint)
            
            audit_logger.log_action(
                user_id=user.id,
                action="ASSIGN_OFFICER",
                resource_type="COMPLAINT",
                resource_id=complaint_id,
                details=f"Assigned to officer {officer_id}"
            )
            
            logger.info(
                f"Complaint #{complaint_id} assigned to officer {officer_id} "
                f"by user {user.id}"
            )
            
            return complaint
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to assign officer: {e}")
            raise HTTPException(status_code=500, detail="Failed to assign officer")
    
    @staticmethod
    def get_status_history(
        complaint_id: int,
        user: User,
        db: Session
    ) -> List[ComplaintStatusHistory]:
        """
        Get status change history for a complaint.
        
        Args:
            complaint_id: Complaint ID
            user: User requesting history
            db: Database session
            
        Returns:
            List of status history entries
        """
        # Verify complaint exists and user can access it
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        
        # Check access permissions
        if user.role == UserRole.USER and complaint.user_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only view history of your own complaints"
            )
        
        if user.role == UserRole.DEPARTMENT_MANAGER:
            if complaint.department != user.department:
                raise HTTPException(
                    status_code=403,
                    detail="You can only view history of your department's complaints"
                )
        
        # Get history
        history = db.query(ComplaintStatusHistory).filter(
            ComplaintStatusHistory.complaint_id == complaint_id
        ).order_by(ComplaintStatusHistory.changed_at.desc()).all()
        
        return history
    
    @staticmethod
    def get_my_queue(
        user: User,
        db: Session,
        status_filter: Optional[str] = None
    ) -> List[Complaint]:
        """
        Get complaints assigned to the current user (officer's work queue).
        
        Args:
            user: Current user (must be officer or manager)
            db: Database session
            status_filter: Optional status to filter by
            
        Returns:
            List of complaints assigned to user
        """
        if user.role == UserRole.USER:
            raise HTTPException(
                status_code=403,
                detail="Only officers and managers have work queues"
            )
        
        query = db.query(Complaint)
        
        if user.role == UserRole.DEPARTMENT_MANAGER:
            # Managers see all complaints in their department
            query = query.filter(Complaint.department == user.department)
        else:
            # Officers see only their assigned complaints
            query = query.filter(Complaint.assigned_to == user.id)
        
        # Apply status filter
        if status_filter:
            query = query.filter(Complaint.status == status_filter.lower())
        
        # Order by urgency and creation date
        complaints = query.order_by(
            Complaint.urgency.desc(),
            Complaint.created_at.asc()
        ).all()
        
        return complaints


# Create singleton instance
workflow_service = WorkflowService()