# app/routers/workflow.py
"""
Workflow Router - Endpoints for complaint status management and workflow operations.

Endpoints:
- PATCH /complaints/{id}/status - Change complaint status
- POST /complaints/{id}/assign-officer - Assign to officer
- GET /complaints/{id}/history - View status history
- GET /complaints/my-queue - Officer's work queue
- GET /complaints/{id}/allowed-transitions - Get available actions
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.deps import get_db, get_current_user
from app.models.users import User
from app.models.complaints import Complaint
from app.services.workflow_service import workflow_service
from app.schemas.workflow import (
    StatusChangeRequest,
    AssignOfficerRequest,
    StatusHistoryResponse,
    StatusHistoryListResponse,
    AllowedTransitionsResponse
)
from app.schemas.complaint import ComplaintResponse
from app.enums import get_allowed_transitions, UserRole
from app.core.logging import get_logger

router = APIRouter(prefix="/complaints", tags=["Workflow"])
logger = get_logger(__name__)


# ==========================================
# CHANGE STATUS
# ==========================================

@router.patch("/{complaint_id}/status", response_model=ComplaintResponse)
def change_complaint_status(
    complaint_id: int,
    request: StatusChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change complaint status.
    
    **Permissions:**
    - **Admin:** Can change any status
    - **Department Manager:** Can manage their department's complaints
    - **Citizen:** Can only close resolved complaints
    
    **Status Flow:**
    ```
    pending → assigned → in_progress → resolved → closed
       ↓
    rejected
    ```
    
    **Examples:**
    ```json
    {
      "new_status": "assigned",
      "comment": "Assigned to Public Works department"
    }
    ```
    
    ```json
    {
      "new_status": "rejected",
      "reason": "Duplicate of complaint #123",
      "comment": "Already reported last week"
    }
    ```
    """
    logger.info(
        f"Status change request for complaint #{complaint_id}: "
        f"{request.new_status} by user {current_user.id}"
    )
    
    complaint = workflow_service.change_status(
        complaint_id=complaint_id,
        new_status=request.new_status,
        user=current_user,
        db=db,
        comment=request.comment,
        reason=request.reason
    )
    
    return complaint


# ==========================================
# ASSIGN TO OFFICER
# ==========================================

@router.post("/{complaint_id}/assign-officer", response_model=ComplaintResponse)
def assign_to_officer(
    complaint_id: int,
    request: AssignOfficerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Assign complaint to a specific officer.
    
    **Permissions:**
    - **Admin:** Can assign to any officer
    - **Department Manager:** Can assign to officers in their department
    - **Citizen:** Cannot assign
    
    **Example:**
    ```json
    {
      "officer_id": 42
    }
    ```
    """
    logger.info(
        f"Assign complaint #{complaint_id} to officer {request.officer_id} "
        f"by user {current_user.id}"
    )
    
    complaint = workflow_service.assign_to_officer(
        complaint_id=complaint_id,
        officer_id=request.officer_id,
        user=current_user,
        db=db
    )
    
    return complaint


# ==========================================
# VIEW STATUS HISTORY
# ==========================================

@router.get("/{complaint_id}/history", response_model=StatusHistoryListResponse)
def get_status_history(
    complaint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete status change history for a complaint.
    
    **Permissions:**
    - **Admin:** Can view any complaint history
    - **Department Manager:** Can view their department's complaints
    - **Citizen:** Can only view their own complaints
    
    **Returns:** Timeline of all status changes with who/when/why
    
    **Example Response:**
    ```json
    {
      "count": 3,
      "data": [
        {
          "id": 15,
          "complaint_id": 42,
          "old_status": "in_progress",
          "new_status": "resolved",
          "changed_by": 5,
          "changed_at": "2025-12-30T10:30:00",
          "comment": "Pothole filled and road resurfaced",
          "reason": null
        },
        ...
      ]
    }
    ```
    """
    history = workflow_service.get_status_history(
        complaint_id=complaint_id,
        user=current_user,
        db=db
    )
    
    return {
        "count": len(history),
        "data": history
    }


# ==========================================
# OFFICER'S WORK QUEUE
# ==========================================

@router.get("/my-queue", response_model=List[ComplaintResponse])
def get_my_work_queue(
    status: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complaints assigned to current user (officer's work queue).
    
    **Permissions:**
    - **Admin:** Sees all complaints
    - **Department Manager:** Sees all complaints in their department
    - **Officer:** Sees only complaints assigned to them
    - **Citizen:** Not allowed
    
    **Query Parameters:**
    - `status` (optional): Filter by status (e.g., "in_progress")
    
    **Example Response:**
    ```json
    [
      {
        "id": 42,
        "description": "Pothole on MG Road",
        "status": "in_progress",
        "urgency": "high",
        "assigned_to": 5,
        "created_at": "2025-12-29T08:00:00"
      },
      ...
    ]
    ```
    """
    if current_user.role == UserRole.USER:
        raise HTTPException(
            status_code=403,
            detail="Citizens do not have work queues"
        )
    
    complaints = workflow_service.get_my_queue(
        user=current_user,
        db=db,
        status_filter=status
    )
    
    logger.info(
        f"Work queue requested by user {current_user.id}: "
        f"found {len(complaints)} complaints"
    )
    
    return complaints


# ==========================================
# GET ALLOWED TRANSITIONS
# ==========================================

@router.get("/{complaint_id}/allowed-transitions", response_model=AllowedTransitionsResponse)
def get_allowed_status_transitions(
    complaint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of allowed status transitions for current user.
    
    Useful for frontend to show only valid action buttons.
    
    **Example Response:**
    ```json
    {
      "current_status": "assigned",
      "allowed_transitions": ["in_progress", "rejected"],
      "message": "You can move this complaint to: in_progress, rejected"
    }
    ```
    """
    # Get complaint
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    # Check access
    if current_user.role == UserRole.USER and complaint.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You can only view your own complaints"
        )
    
    if current_user.role == UserRole.DEPARTMENT_MANAGER:
        if complaint.department != current_user.department:
            raise HTTPException(
                status_code=403,
                detail="You can only manage your department's complaints"
            )
    
    # Get allowed transitions
    allowed = get_allowed_transitions(complaint.status, current_user.role)
    
    return {
        "current_status": complaint.status,
        "allowed_transitions": allowed,
        "message": f"You can move this complaint to: {', '.join(allowed)}" if allowed 
                   else "No transitions available (complaint is in final state)"
    }