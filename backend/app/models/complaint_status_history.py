# app/models/complaint_status_history.py
"""
Complaint Status History Model

Tracks all status changes for audit trail and timeline view.
Every time a complaint status changes, a record is created here.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class ComplaintStatusHistory(Base):
    """
    Records every status change for a complaint.
    
    Use cases:
    - Audit trail (who changed what when)
    - Timeline view for citizens
    - Performance metrics (time in each status)
    - Accountability tracking
    """
    
    __tablename__ = "complaint_status_history"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # ==========================================
    # FOREIGN KEYS
    # ==========================================
    
    complaint_id = Column(
        Integer,
        ForeignKey("complaints.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    changed_by = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )
    
    # ==========================================
    # STATUS TRACKING
    # ==========================================
    
    old_status = Column(String, nullable=True)  # NULL for first entry (creation)
    new_status = Column(String, nullable=False)
    
    # ==========================================
    # ADDITIONAL CONTEXT
    # ==========================================
    
    comment = Column(Text, nullable=True)  # Optional comment from officer
    reason = Column(String, nullable=True)  # For rejections, reopening, etc.
    
    # Assignment changes (track who it was assigned to)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # ==========================================
    # TIMESTAMP
    # ==========================================
    
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # ==========================================
    # RELATIONSHIPS (Optional)
    # ==========================================
    
    # Uncomment if you want to use relationships
    # complaint = relationship("Complaint", back_populates="status_history")
    # changer = relationship("User", foreign_keys=[changed_by])
    # assignee = relationship("User", foreign_keys=[assigned_to])