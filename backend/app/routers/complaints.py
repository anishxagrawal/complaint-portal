# app/routers/complaints.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.complaint import ComplaintCreate, ComplaintResponse
from app.services.complaint_service import ComplaintService  # ✅ IMPORT
from app.deps import get_db

router = APIRouter(prefix="/complaints", tags=["Complaint"])

@router.post("/", response_model=ComplaintResponse, status_code=201)
def post_complaints(complaint_data: ComplaintCreate, db: Session = Depends(get_db)):
    # ✅ Pass both arguments
    return ComplaintService.create(complaint_data, db)

@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    return ComplaintService.get_by_id(complaint_id, db)

@router.get("/", response_model=List[ComplaintResponse])
def list_complaints(db: Session = Depends(get_db)):
    return ComplaintService.list_all(db)