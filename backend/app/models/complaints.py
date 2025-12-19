from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)

    # Who filed the complaint
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # What kind of issue
    issue_type_id = Column(Integer, ForeignKey("issue_types.id"), nullable=False)

    # Core complaint data
    description = Column(String, nullable=False)
    address = Column(String, nullable=False)

    # Control fields
    status = Column(String, default="OPEN")
    urgency = Column(String, default="MEDIUM")

    created_at = Column(DateTime, default=datetime.utcnow)
