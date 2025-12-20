# app/routers/issue_types.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.issue_type import IssueTypeCreate, IssueTypeResponse
from app.services.issue_type_service import IssueTypeService
from app.deps import get_db

router = APIRouter(
    prefix="/issue-types",
    tags=["Issue Types"]
)

@router.post("/", response_model=IssueTypeResponse, status_code=201)
def create(
    issue_type: IssueTypeCreate,
    db: Session = Depends(get_db)
):
    return IssueTypeService.create(issue_type, db)

@router.get("/", response_model=List[IssueTypeResponse])
def list_issue_types(db: Session = Depends(get_db)):
    return IssueTypeService.list_all(db)

@router.get("/{issue_id}", response_model=IssueTypeResponse)
def get_issue_type(issue_id: int, db: Session = Depends(get_db)):
    return IssueTypeService.get_by_id(issue_id, db)