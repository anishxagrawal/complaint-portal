from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    # Who filed the complaint
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Issue type
    issue_type_id = Column(Integer, ForeignKey("issue_types.id"), nullable=False)

    # Complaint details
    description = Column(String, nullable=False)
    address = Column(String, nullable=False)

    # Workflow / assignment
    status = Column(String, default="pending", nullable=False)
    department = Column(String, nullable=True)

    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_at = Column(DateTime, nullable=True)

    urgency = Column(String, default="medium", nullable=False)

    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolution_notes = Column(String, nullable=True)

    closed_at = Column(DateTime, nullable=True)
    closed_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # ✅ ORM relationships (THIS FIXES 500 ERRORS)
    issue_type = relationship(
        "IssueType",
        back_populates="complaints"
    )

    user = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="complaints"
    )

    submitter = relationship(
        "User",
        foreign_keys=[submitted_by]
    )
