# app/routers/complaints.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.complaint import ComplaintCreate, ComplaintResponse
from app.services.complaint_service import ComplaintService  # ✅ IMPORT
from app.deps import get_db

from app.deps import get_current_user        # Function we created
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

@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(
    complaint_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ComplaintService.get_by_id(complaint_id, db, current_user.id)

@router.get("/", response_model=List[ComplaintResponse])
def list_complaints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return ComplaintService.list_all(db, current_user.id)

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


