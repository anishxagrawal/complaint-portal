# app/routers/complaints.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from math import ceil

from app.schemas.complaint import (
    ComplaintCreate, 
    ComplaintResponse,
    PaginatedComplaintResponse,
    PaginationMetadata,
    ComplaintAssign
)
from app.services.complaint_service import ComplaintService
from app.deps import get_db, get_current_user
from app.models.users import User
from app.models.complaints import Complaint
from app.middleware.permissions import require_permission, require_complaint_access, require_any_permission
from app.enums import Permission 

router = APIRouter(prefix="/complaints", tags=["Complaint"])


# ============================================
# CREATE COMPLAINT (All authenticated users)
# ============================================
@router.post("/", response_model=ComplaintResponse, status_code=201)
def post_complaints(
    complaint_data: ComplaintCreate, 
    current_user: User = Depends(require_permission(Permission.CREATE_COMPLAINT)),
    db: Session = Depends(get_db)
):
    """Create a new complaint. All users can create complaints."""
    return ComplaintService.create(complaint_data, db, current_user.id)


# ============================================
# SEARCH COMPLAINTS (Role-aware)
# ============================================
@router.get("/search", response_model=PaginatedComplaintResponse)
def search_complaint(
    q: str,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_any_permission(
        Permission.VIEW_ALL_COMPLAINTS,
        Permission.VIEW_OWN_COMPLAINTS,
        Permission.VIEW_DEPARTMENT_COMPLAINTS
    )),
    db: Session = Depends(get_db)
):
    """
    Search complaints (filtered by user's role).
    - ADMIN: Searches all complaints
    - USER: Searches only their own
    - DEPT_MGR: Searches their department
    """
    complaints, total_count = ComplaintService.search(
        db=db,
        user=current_user,
        query=q,
        page=page,
        page_size=page_size
    )

    total_pages = ceil(total_count / page_size) if total_count > 0 else 1

    return PaginatedComplaintResponse(
        data=complaints,
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total_count,
            pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    )


# ============================================
# GET SINGLE COMPLAINT (Ownership check via middleware)
# ============================================
@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint: Complaint = Depends(require_complaint_access)
):
    """
    Get a specific complaint.
    - ADMIN: Any complaint
    - USER: Only their own
    - DEPT_MGR: Only their department
    
    Access control is enforced by require_complaint_access middleware.
    """
    return complaint


# ============================================
# LIST ALL COMPLAINTS (Role-aware)
# ============================================
@router.get("/", response_model=PaginatedComplaintResponse)
def list_complaints(
    status: Optional[str] = None,
    urgency: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,   
    sort: str = "-created_at",
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_any_permission(
        Permission.VIEW_ALL_COMPLAINTS,
        Permission.VIEW_OWN_COMPLAINTS,
        Permission.VIEW_DEPARTMENT_COMPLAINTS
    )),
    db: Session = Depends(get_db)
):
    """
    List complaints (filtered by role).
    - ADMIN: All complaints
    - USER: Only their own
    - DEPT_MGR: Only their department
    """
    complaints, total_count = ComplaintService.list_all(
        db=db,
        user=current_user,
        status=status,
        urgency=urgency,
        from_date=from_date,
        to_date=to_date,
        sort=sort,
        page=page,
        page_size=page_size
    )

    total_pages = ceil(total_count / page_size) if total_count > 0 else 1

    return PaginatedComplaintResponse(
        data=complaints,
        pagination=PaginationMetadata(
            page=page,
            page_size=page_size,
            total=total_count,
            pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
    )


# ============================================
# UPDATE COMPLAINT (Permission + Ownership check)
# ============================================
@router.put("/{complaint_id}", response_model=ComplaintResponse)
def update_complaint(
    complaint_data: ComplaintCreate,
    complaint: Complaint = Depends(require_complaint_access),
    current_user: User = Depends(require_permission(Permission.UPDATE_COMPLAINT)),
    db: Session = Depends(get_db)
):
    """
    Update a complaint.
    - USER: Can update their own
    - DEPT_MGR: Can update their dept complaints
    - ADMIN: Can update any
    
    Both permission AND ownership are checked.
    """
    return ComplaintService.update(complaint.id, complaint_data, db, current_user)


# ============================================
# DELETE COMPLAINT (Admin only)
# ============================================
@router.delete("/{complaint_id}")
def delete_complaint(
    complaint_id: int,
    current_user: User = Depends(require_permission(Permission.DELETE_COMPLAINT)),
    db: Session = Depends(get_db)
):
    """Delete a complaint. Admin only."""
    return ComplaintService.delete(complaint_id, db, current_user)


# ============================================
# ASSIGN COMPLAINT (Admin + Dept Manager)
# ============================================
@router.patch("/{complaint_id}/assign", response_model=ComplaintResponse)
def assign_complaint(
    complaint_id: int,
    assign_data: ComplaintAssign,
    # ✅ CHANGED: enforce permission at router level
    current_user: User = Depends(require_permission(Permission.ASSIGN_COMPLAINT)),
    db: Session = Depends(get_db)
):
    """
    Assign complaint to a department.
    
    Access control:
    - ADMIN: Can assign to any department
    - DEPT_MGR: Can only assign to their own department
    - USER: Cannot assign (403 error)
    
    Permission is enforced at router level.
    """
    return ComplaintService.assign_complaint(
        complaint_id=complaint_id,
        department=assign_data.department,
        db=db,
        user=current_user
    )