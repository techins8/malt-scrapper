from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, JSON, DateTime, Enum as SQLAlchemyEnum
from sqlalchemy.sql import func
from app.core.database import Base


class ProfileStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    ERROR = "error"
    CANCELLED = "cancelled"
    SCRAPPED = "scrapped"
    NOT_FOUND = "not_found"


class MaltProfile(Base):
    __tablename__ = "malt_profiles"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(String, unique=True, index=True)
    fullname = Column(String, index=True)
    title = Column(String)
    experience_years = Column(Float)
    daily_rate = Column(Float)
    image_url = Column(String)
    profile_url = Column(String)
    locations = Column(JSON)  # List of locations
    skills = Column(JSON)  # List of skills with levels
    languages = Column(JSON)  # List of languages with levels
    availability = Column(String)
    missions_count = Column(Integer)
    description = Column(String)
    education = Column(JSON)  # List of education entries
    experience = Column(JSON)  # List of work experiences
    certifications = Column(JSON)  # List of certifications
    status = Column(SQLAlchemyEnum(ProfileStatus), default=ProfileStatus.TODO, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    class Config:
        orm_mode = True
