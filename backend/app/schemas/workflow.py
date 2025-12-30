# app/schemas/workflow.py
"""
Workflow-related Pydantic schemas for request/response validation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class StatusChangeRequest(BaseModel):
    """Request to change complaint status"""
    new_status: str = Field(
        ...,
        description="New status to set",
        examples=["assigned", "in_progress", "resolved", "closed", "rejected"]
    )
    comment: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional comment about the status change"
    )
    reason: Optional[str] = Field(
        None,
        max_length=500,
        description="Reason for status change (required for rejections)"
    )


class AssignOfficerRequest(BaseModel):
    """Request to assign complaint to an officer"""
    officer_id: int = Field(
        ...,
        description="ID of officer to assign complaint to",
        gt=0
    )


class StatusHistoryResponse(BaseModel):
    """Single status history entry"""
    id: int
    complaint_id: int
    old_status: Optional[str]
    new_status: str
    changed_by: int
    changed_at: datetime
    comment: Optional[str]
    reason: Optional[str]
    assigned_to: Optional[int]
    
    class Config:
        from_attributes = True


class StatusHistoryListResponse(BaseModel):
    """List of status history entries"""
    count: int
    data: List[StatusHistoryResponse]


class WorkQueueResponse(BaseModel):
    """Officer's work queue"""
    count: int
    pending_count: int
    assigned_count: int
    in_progress_count: int
    complaints: List[dict]  # Will use existing ComplaintResponse


class AllowedTransitionsResponse(BaseModel):
    """Available status transitions for current user"""
    current_status: str
    allowed_transitions: List[str]
    message: str