from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.complaint import ComplaintCreate, ComplaintResponse
from app.models.complaints import Complaint
from app.models.users import User  # ✅ ADD THIS
from app.models.issue_types import IssueType  # ✅ ADD THIS
from app.deps import get_db

router = APIRouter(prefix="/complaints", tags=["Complaint"])

@router.post("/", response_model=ComplaintResponse, status_code=201)
def post_complaints(complaint_data: ComplaintCreate, db: Session = Depends(get_db)):
    
    # ✅ CHECK 1: User exists
    user = db.query(User).filter_by(id=complaint_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # ✅ CHECK 2: Issue type exists
    issue_type = db.query(IssueType).filter_by(id=complaint_data.issue_type_id).first()
    if not issue_type:
        raise HTTPException(status_code=404, detail="Issue type not found")
    
    # ✅ CHECK 3: Try-except for database errors
    try:
        new_complaint = Complaint(
            user_id=complaint_data.user_id,
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