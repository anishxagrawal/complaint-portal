from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DepartmentCreate(BaseModel):
    name: str

class DepartmentResponse(BaseModel):
    id: int
    name: str
    is_active: bool