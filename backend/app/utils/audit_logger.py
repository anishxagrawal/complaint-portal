# app/utils/audit_logger.py
from datetime import datetime
from sqlalchemy.orm import Session
from typing import Optional
import logging

# Setup basic logger
logger = logging.getLogger(__name__)

class AuditLogger:
    """
    Audit logging utility to track user actions
    Foundation for Phase 3 - will be expanded later for database logging
    """
    
    @staticmethod
    def log_action(
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        details: Optional[str] = None
    ):
        """
        Log a user action
        
        Args:
            user_id: Who performed the action
            action: What they did (CREATE, READ, UPDATE, DELETE, ASSIGN)
            resource_type: What they acted on (COMPLAINT, USER, ISSUE_TYPE)
            resource_id: Specific resource ID (optional)
            details: Additional context (optional)
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details
        }
        
        # For now, just log to console
        # Later: Save to audit_logs table in database
        logger.info(f"AUDIT: {log_entry}")
        
        return log_entry

# Create singleton instance
audit_logger = AuditLogger()