# app/routers/complaints.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from math import ceil

from app.schemas.complaint import(
    ComplaintCreate, 
    ComplaintResponse,
    PaginatedComplaintResponse,  # ✅ NEW: For paginated list
    PaginationMetadata           # ✅ NEW: For pagination info
)
from app.services.complaint_service import ComplaintService  # ✅ IMPORT
from app.deps import get_db, get_current_user # Function we created
from app.models.users import User            # So we can type-hint current_user

router = APIRouter(prefix="/complaints", tags=["Complaint"])

@router.post("/", response_model=ComplaintResponse, status_code=201)
def post_complaints(
    complaint_data: ComplaintCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ✅ Pass both arguments + current_user.id
    return ComplaintService.create(complaint_data, db, current_user.id)

@router.get("/search", response_model=PaginatedComplaintResponse)
def search_complaint(
    q: str,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    complaints, total_count = ComplaintService.search(
        db=db,
        user_id=current_user.id,
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

@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ComplaintService.get_by_id(complaint_id, db, current_user.id)

"""
@router.get("/", response_model=List[ComplaintResponse])
def list_complaints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ComplaintService.list_all(db, current_user.id)
"""

@router.put("/{complaint_id}", response_model=ComplaintResponse)
def update_complaint(
    complaint_id: int,
    complaint_data: ComplaintCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing complaint"""
    return ComplaintService.update(complaint_id, complaint_data, db, current_user.id)


@router.delete("/{complaint_id}")
def delete_complaint(
    complaint_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a complaint"""
    return ComplaintService.delete(complaint_id, db, current_user.id)

# ============================================
# 🆕 UPDATED ENDPOINT (Added sorting, filter and pagination)
# ============================================

@router.get("/", response_model=PaginatedComplaintResponse)
def list_complaints(
    # 🆕 FILTER PARAMETERS (Optional - can be None)
    status: Optional[str] = None,
    urgency: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,   

    # 🆕 SORTING PARAMETER (Default: newest first)
    sort: str = "-created_at",

    # 🆕 PAGINATION PARAMETERS
    page: int = 1,
    page_size: int = 20,

    # EXISTING PARAMETERS
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    complaints, total_count = ComplaintService.list_all(
        db=db,
        user_id=current_user.id,    # Only user's complaints
        status=status,              # Filter by status (if provided)
        urgency=urgency,            # Filter by urgency (if provided)
        from_date=from_date,        # Filter by start date (if provided)
        to_date=to_date,            # Filter by end date (if provided)
        sort=sort,                  # Sort order
        page=page,                  # Which page
        page_size=page_size         # Items per page
    )

    total_pages = ceil(total_count / page_size) if total_count > 0 else 1

    has_next = page < total_pages

    has_prev = page > 1

    return PaginatedComplaintResponse(
        data=complaints,

        # The pagination metadata
        pagination=PaginationMetadata(
            page=page,                  # Current page number
            page_size=page_size,        # Items per page
            total=total_count,          # Total items across all pages
            pages=total_pages,          # Total number of pages
            has_next=has_next,          # Can go to next page?
            has_prev=has_prev           # Can go to previous page?
        )
    )
