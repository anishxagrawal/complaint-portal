# app/services/conversation_service.py
from typing import Dict, Optional
from datetime import datetime
import uuid

class ConversationService:
    """
    Manages conversation state for multi-turn chats.
    
    In production, use Redis. For now, use in-memory dict.
    """
    
    def __init__(self):
        # In-memory storage (replace with Redis later)
        self.conversations: Dict[str, Dict] = {}
    
    def create_conversation(self, user_id: int) -> str:
        """Create a new conversation and return its ID"""
        conversation_id = str(uuid.uuid4())
        
        self.conversations[conversation_id] = {
            "conversation_id": conversation_id,
            "user_id": user_id,
            "messages": [],
            "extracted_data": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Retrieve conversation state"""
        return self.conversations.get(conversation_id)
    
    def add_message(
        self, 
        conversation_id: str, 
        role: str, 
        content: str
    ):
        """Add a message to the conversation"""
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.conversations[conversation_id]["updated_at"] = datetime.utcnow().isoformat()
    
    def update_extracted_data(
        self, 
        conversation_id: str, 
        extracted_data: Dict
    ):
        """Update extracted complaint data"""
        if conversation_id in self.conversations:
            self.conversations[conversation_id]["extracted_data"] = extracted_data
            self.conversations[conversation_id]["updated_at"] = datetime.utcnow().isoformat()
    
    def delete_conversation(self, conversation_id: str):
        """Delete conversation after complaint is created"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]

# Create singleton
conversation_service = ConversationService()