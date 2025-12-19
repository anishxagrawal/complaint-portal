from pydantic import BaseModel

class IssueTypeCreate(BaseModel):
    name: str
    department_id: int

class IssueTypeResponse(BaseModel):
    id: int
    name: str
    department_id: int
    is_active: bool
