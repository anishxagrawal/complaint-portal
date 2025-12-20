from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.schemas.issue_type import IssueTypeCreate, IssueTypeResponse
from app.models.issue_types import IssueType
from app.models.departments import Department  # ✅ ADD THIS
from app.deps import get_db

router = APIRouter(prefix="/issue-types", tags=["Issue Types"])

@router.post("/", response_model=IssueTypeResponse, status_code=201)
def create_issue_type(issue_type: IssueTypeCreate, db: Session = Depends(get_db)):
    # ✅ Check if department exists
    dept = db.query(Department).filter_by(id=issue_type.department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    
    try:
        new_issue_type = IssueType(name=issue_type.name, department_id=issue_type.department_id)
        db.add(new_issue_type)
        db.commit()
        db.refresh(new_issue_type)
        return new_issue_type
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create issue type")

@router.get("/", response_model=List[IssueTypeResponse])
def list_issue_types(db: Session = Depends(get_db)):
    return db.query(IssueType).all()

@router.get("/{issue_id}", response_model=IssueTypeResponse)
def get_issue_type(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(IssueType).filter_by(id=issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue type not found")
    return issue