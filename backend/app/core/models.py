from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    meetings = relationship("Meeting", back_populates="owner")

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=True)
    original_filename = Column(String, nullable=True)
    status = Column(String, nullable=False, default="queued") # queued, running, done, failed
    stage = Column(String, nullable=True, default="validating")
    percent = Column(Integer, default=0)
    message = Column(String, nullable=True)
    error_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    duration_sec = Column(Float, nullable=True)
    summary = Column(Text, nullable=True)
    transcript_raw = Column(Text, nullable=True)
    transcript_refined = Column(Text, nullable=True)
    minutes_json = Column(Text, nullable=True)
    
    owner = relationship("User", back_populates="meetings")
