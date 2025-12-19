from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from datetime import datetime
from app.database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer ,primary_key=True ,nullable = False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=False)