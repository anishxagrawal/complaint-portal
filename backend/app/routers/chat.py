# app/routers/chat.py
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

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
from app.core.logging import get_logger
from app.core.exceptions import NotFoundError, ForbiddenError

# ==========================================
# Setup
# ==========================================

router = APIRouter(prefix="/chat", tags=["Chat"])
logger = get_logger(__name__)
limiter = Limiter(key_func=get_remote_address)

# ==========================================
# SEND CHAT MESSAGE (Rate Limited: 20 per minute)
# ==========================================

@router.post("/message", response_model=ChatMessageResponse)
@limiter.limit("20/minute")  # ✅ NEW: Rate limit (AI API costs money!)
async def send_chat_message(
    http_request: Request,  # ✅ NEW: For rate limiting
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    ai_service = Depends(get_ai_service)
):
    """
    Conversational complaint submission using AI.
    
    **Rate Limit:** 20 messages per minute per IP
    
    Flow:
    1. User sends natural language message
    2. AI extracts complaint info
    3. If unclear, ask clarification questions
    4. If clear, confirm and create complaint
    
    Args:
        http_request: FastAPI request (for rate limiting)
        request: Chat message from user
        current_user: Authenticated user
        db: Database session
        ai_service: AI service for extraction
        
    Returns:
        ChatMessageResponse with bot's reply and extracted data
        
    Errors:
        404: Conversation not found
        403: Not your conversation
        429: Too many requests (rate limit)
        500: AI extraction failed
    """
    
    try:
        # ==========================================
        # 1. Get or Create Conversation
        # ==========================================
        
        if not request.conversation_id:
            conversation_id = conversation_service.create_conversation(current_user.id)
            logger.info(f"Created new conversation: {conversation_id} for user {current_user.id}")
        else:
            conversation_id = request.conversation_id
            conversation = conversation_service.get_conversation(conversation_id)
            
            if not conversation:
                logger.warning(f"Conversation not found: {conversation_id}")
                raise NotFoundError(f"Conversation {conversation_id} not found")
            
            if conversation["user_id"] != current_user.id:
                logger.warning(
                    f"User {current_user.id} tried to access "
                    f"conversation {conversation_id} owned by {conversation['user_id']}"
                )
                raise ForbiddenError("Not your conversation")
        
        # ==========================================
        # 2. Add User Message
        # ==========================================
        
        conversation_service.add_message(conversation_id, "user", request.message)
        logger.debug(f"Added user message to conversation {conversation_id}")
        
        # Get conversation state
        conversation = conversation_service.get_conversation(conversation_id)
        
        # ==========================================
        # 3. Extract/Update Complaint Info with AI
        # ==========================================
        
        try:
            if not conversation["extracted_data"]:
                # First message - extract info
                logger.info(f"Extracting complaint info from first message")
                extracted_data = ai_service.extract_complaint_info(request.message)
            else:
                # Follow-up message - update extraction
                logger.info(f"Updating extraction with follow-up message")
                extracted_data = ai_service.generate_clarification_response(
                    original_message=conversation["messages"][0]["content"],
                    extracted_info=conversation["extracted_data"],
                    user_response=request.message
                )
        except Exception as e:
            logger.error(f"❌ AI extraction failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"AI extraction failed: {str(e)}"
            )
        
        # Update conversation with extracted data
        conversation_service.update_extracted_data(conversation_id, extracted_data)
        
        # ==========================================
        # 4. Check if Clarification Needed
        # ==========================================
        
        if extracted_data["needs_clarification"]:
            bot_message = "I need some more information:\n\n"
            for i, question in enumerate(extracted_data["clarification_questions"], 1):
                bot_message += f"{i}. {question}\n"
            
            conversation_service.add_message(conversation_id, "assistant", bot_message)
            logger.info(f"Requesting clarification for conversation {conversation_id}")
            
            return ChatMessageResponse(
                conversation_id=conversation_id,
                bot_message=bot_message,
                extracted_data=ExtractedComplaintData(**extracted_data),
                ready_to_submit=False
            )
        
        # ==========================================
        # 5. Check Confidence Level
        # ==========================================
        
        if extracted_data["confidence"] < 0.7:
            bot_message = f"""I'm not very confident about the details. Here's what I understood:

📍 Location: {extracted_data['address']}
📝 Issue: {extracted_data['description']}
🏷️ Category: {extracted_data['issue_type']}
⚠️ Urgency: {extracted_data['urgency']}

Is this correct? Reply 'yes' to submit or provide corrections."""
            
            conversation_service.add_message(conversation_id, "assistant", bot_message)
            logger.info(f"Low confidence ({extracted_data['confidence']}) - asking for confirmation")
            
            return ChatMessageResponse(
                conversation_id=conversation_id,
                bot_message=bot_message,
                extracted_data=ExtractedComplaintData(**extracted_data),
                ready_to_submit=False
            )
        
        # ==========================================
        # 6. High Confidence - Create Complaint
        # ==========================================
        
        logger.info(f"High confidence ({extracted_data['confidence']}) - creating complaint")
        
        # Map issue_type string to issue_type_id
        issue_type = db.query(IssueType).filter(
            IssueType.name.ilike(f"%{extracted_data['issue_type']}%")
        ).first()
        
        if not issue_type:
            # Default to "Other" if not found
            issue_type = db.query(IssueType).filter(
                IssueType.name == "Other"
            ).first()
            logger.warning(f"Issue type '{extracted_data['issue_type']}' not found, using 'Other'")
        
        # Create complaint
        try:
            complaint_data = ComplaintCreate(
                user_id=current_user.id,
                issue_type_id=issue_type.id if issue_type else 1,
                description=extracted_data["description"],
                address=extracted_data["address"]
            )
            
            complaint = ComplaintService.create(complaint_data, db, current_user.id)
            logger.info(f"✅ Complaint #{complaint.id} created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create complaint: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="Failed to create complaint"
            )
        
        # Delete conversation (cleanup)
        conversation_service.delete_conversation(conversation_id)
        logger.info(f"Conversation {conversation_id} deleted after complaint creation")
        
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
    
    except (NotFoundError, ForbiddenError):
        # Re-raise custom exceptions (handled by error handler)
        raise
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        # Catch any other unexpected errors
        logger.error(f"❌ Unexpected error in chat: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )