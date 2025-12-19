from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.complaint import ComplaintCreate, ComplaintResponse
from app.models.complaints import Complaint
from app.deps import get_db

router = APIRouter(prefix="/complaints", tags=["Complaint"])

@router.post("/", response_model=ComplaintResponse)
def post_complaints(user: ComplaintCreate, db: Session = Depends(get_db)):

    new_complaint = Complaint(
        user_id=user.user_id,
        issue_type_id=user.issue_type_id,
        description=user.description,
        address=user.address
    )

    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
    
    return new_complaint