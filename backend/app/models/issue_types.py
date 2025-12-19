from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from app.database import Base


class IssueType(Base):
    __tablename__ = "issue_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    is_active = Column(Boolean, default=True)