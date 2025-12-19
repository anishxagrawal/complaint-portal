from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ComplaintCreate(BaseModel):
    user_id: int
    issue_type_id: int
    description: str
    address: str

class ComplaintResponse(BaseModel):
    id: int
    user_id: int
    issue_type_id: int
    description: str
    address: str
    status: str
    urgency: str
    created_at: datetime
