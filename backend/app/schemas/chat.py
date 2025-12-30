# app/schemas/chat.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class ChatMessageRequest(BaseModel):
    """User sends a message in the chat"""
    message: str = Field(
        ...,
        min_length=5,
        max_length=1000,
        examples=["There's a pothole on MG Road near the mall"]
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="ID for multi-turn conversations. Leave empty for new conversation."
    )

class ExtractedComplaintData(BaseModel):
    """AI-extracted complaint information"""
    description: str
    address: str
    issue_type: str
    urgency: str
    confidence: float
    needs_clarification: bool
    clarification_questions: List[str] = []

class ChatMessageResponse(BaseModel):
    """Response from chat endpoint"""
    conversation_id: str
    bot_message: str
    extracted_data: Optional[ExtractedComplaintData] = None
    ready_to_submit: bool = Field(
        default=False,
        description="True when complaint is ready to be saved"
    )
    complaint_id: Optional[int] = Field(
        default=None,
        description="Set after complaint is successfully created"
    )

class ConversationState(BaseModel):
    """Track conversation state (stored in memory/cache)"""
    conversation_id: str
    user_id: int
    messages: List[Dict] = []
    extracted_data: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime