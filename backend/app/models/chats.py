from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

class ChatConversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, unique=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    extracted_data = Column(JSON, nullable=True)
    status = Column(String, default="IN_PROGRESS")  
    # IN_PROGRESS | SUBMITTED | ABANDONED

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
