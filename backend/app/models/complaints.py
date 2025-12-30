# app/models/complaints.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Complaint(Base):
    """
    Complaint model with workflow support.
    
    Workflow statuses:
    - pending: Just submitted
    - assigned: Assigned to officer
    - in_progress: Being worked on
    - resolved: Fixed, awaiting confirmation
    - closed: Confirmed resolved
    - rejected: Invalid complaint
    """
    __tablename__ = "complaints"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # ==========================================
    # CORE COMPLAINT DATA
    # ==========================================
    
    # Who filed the complaint
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)  # Alias for clarity

    # What kind of issue
    issue_type_id = Column(Integer, ForeignKey("issue_types.id"), nullable=False)

    # Complaint details
    description = Column(String, nullable=False)
    address = Column(String, nullable=False)

    # ==========================================
    # WORKFLOW FIELDS (NEW)
    # ==========================================
    
    # Current status
    status = Column(String, default="pending", nullable=False, index=True)
    
    # Assignment tracking
    department = Column(String, nullable=True)  # Department name
    assigned_to = Column(
        Integer, 
        ForeignKey("users.id"), 
        nullable=True
    )  # Assigned officer ID
    assigned_at = Column(DateTime, nullable=True)  # When assigned
    
    # Priority/urgency
    urgency = Column(String, default="medium", nullable=False)  # low, medium, high, critical
    
    # Resolution tracking
    resolved_at = Column(DateTime, nullable=True)  # When marked resolved
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who resolved
    resolution_notes = Column(String, nullable=True)  # Resolution details
    
    # Closure tracking
    closed_at = Column(DateTime, nullable=True)  # When closed
    closed_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who closed
    
    # ==========================================
    # TIMESTAMPS
    # ==========================================
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # ==========================================
    # RELATIONSHIPS (Optional - for ORM queries)
    # ==========================================
    
    # Uncomment if you want to use relationships
    # submitter = relationship("User", foreign_keys=[submitted_by])
    # assignee = relationship("User", foreign_keys=[assigned_to])
    # issue_type = relationship("IssueType")
    # status_history = relationship("ComplaintStatusHistory", back_populates="complaint")