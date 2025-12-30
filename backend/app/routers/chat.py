# app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.chat import (
    ChatMessageRequest,
    ChatMessageResponse,
    ExtractedComplaintData
)

from app.services.ai_service import get_ai_service

from app.services.conversation_service import conversation_service
from app.services.complaint_service import ComplaintService
from app.models.users import User
from app.models.issue_types import IssueType
from app.schemas.complaint import ComplaintCreate
from app.deps import get_db, get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/message", response_model=ChatMessageResponse)
def send_chat_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_service = Depends(get_ai_service)
):
    """
    Conversational complaint submission.
    
    Flow:
    1. User sends natural language message
    2. AI extracts complaint info
    3. If unclear, ask clarification questions
    4. If clear, confirm and create complaint
    """
    
    # Get or create conversation
    if not request.conversation_id:
        conversation_id = conversation_service.create_conversation(current_user.id)
    else:
        conversation_id = request.conversation_id
        conversation = conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        if conversation["user_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Not your conversation")
    
    # Add user message to conversation
    conversation_service.add_message(conversation_id, "user", request.message)
    
    # Get conversation state
    conversation = conversation_service.get_conversation(conversation_id)
    
    # Extract complaint info using AI
    if not conversation["extracted_data"]:
        # First message - extract info
        extracted_data = ai_service.extract_complaint_info(request.message)
    else:
        # Follow-up message - update extraction
        extracted_data = ai_service.generate_clarification_response(
            original_message=conversation["messages"][0]["content"],
            extracted_info=conversation["extracted_data"],
            user_response=request.message
        )
    
    # Update conversation with extracted data
    conversation_service.update_extracted_data(conversation_id, extracted_data)
    
    # Check if we need clarification
    if extracted_data["needs_clarification"]:
        # Ask clarification questions
        bot_message = "I need some more information:\n\n"
        for i, question in enumerate(extracted_data["clarification_questions"], 1):
            bot_message += f"{i}. {question}\n"
        
        conversation_service.add_message(conversation_id, "assistant", bot_message)
        
        return ChatMessageResponse(
            conversation_id=conversation_id,
            bot_message=bot_message,
            extracted_data=ExtractedComplaintData(**extracted_data),
            ready_to_submit=False
        )
    
    # Check confidence level
    if extracted_data["confidence"] < 0.7:
        bot_message = f"""I'm not very confident about the details. Here's what I understood:

📍 Location: {extracted_data['address']}
📝 Issue: {extracted_data['description']}
🏷️ Category: {extracted_data['issue_type']}
⚠️ Urgency: {extracted_data['urgency']}

Is this correct? Reply 'yes' to submit or provide corrections."""
        
        conversation_service.add_message(conversation_id, "assistant", bot_message)
        
        return ChatMessageResponse(
            conversation_id=conversation_id,
            bot_message=bot_message,
            extracted_data=ExtractedComplaintData(**extracted_data),
            ready_to_submit=False
        )
    
    # High confidence - create complaint automatically
    
    # Map issue_type string to issue_type_id
    issue_type = db.query(IssueType).filter(
        IssueType.name.ilike(f"%{extracted_data['issue_type']}%")
    ).first()
    
    if not issue_type:
        # Default to "Other" if not found
        issue_type = db.query(IssueType).filter(
            IssueType.name == "Other"
        ).first()
    
    # Create complaint
    complaint_data = ComplaintCreate(
        user_id=current_user.id,
        issue_type_id=issue_type.id if issue_type else 1,
        description=extracted_data["description"],
        address=extracted_data["address"]
    )
    
    complaint = ComplaintService.create(complaint_data, db, current_user.id)
    
    # Delete conversation (cleanup)
    conversation_service.delete_conversation(conversation_id)
    
    bot_message = f"""✅ Complaint submitted successfully!

**Complaint ID:** #{complaint.id}
**Location:** {complaint.address}
**Category:** {issue_type.name if issue_type else 'Other'}
**Status:** {complaint.status}

You can track your complaint status anytime."""
    
    return ChatMessageResponse(
        conversation_id=conversation_id,
        bot_message=bot_message,
        extracted_data=ExtractedComplaintData(**extracted_data),
        ready_to_submit=True,
        complaint_id=complaint.id
    )