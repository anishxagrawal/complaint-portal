from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.schemas.issue_type import IssueTypeCreate, IssueTypeResponse
from app.models.issue_types import IssueType
from app.deps import get_db

router = APIRouter(
    prefix="/issue-types",
    tags=["Issue Types"]
)

@router.post("/", response_model=IssueTypeResponse)
def create_issue_type(
    issue_type: IssueTypeCreate,
    db: Session = Depends(get_db)
):
    new_issue_type = IssueType(
        name=issue_type.name,
        department_id=issue_type.department_id
    )

    db.add(new_issue_type)
    db.commit()
    db.refresh(new_issue_type)

    return new_issue_type


@router.get("/", response_model=List[IssueTypeResponse])
def list_issue_types(db: Session = Depends(get_db)):
    return db.query(IssueType).all()
