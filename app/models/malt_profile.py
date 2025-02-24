from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    JSON,
    DateTime,
    Enum as SQLAlchemyEnum,
)
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

    id: str = Column(
        String, primary_key=True, index=True, server_default=func.gen_random_uuid()
    )
    profile_id: str = Column(String, unique=True, index=True)
    fullname: Optional[str] = Column(String, index=True)
    title: Optional[str] = Column(String)
    experience_years: Optional[str] = Column(String)
    categories: Optional[List[dict]] = Column(JSON)  # List of categories
    daily_rate: Optional[str] = Column(String)
    image_url: Optional[str] = Column(String)
    profile_url: Optional[str] = Column(String)
    location: str = Column(String)  # location
    work_locations: Optional[List[dict]] = Column(JSON)  # List of work locations
    top_skills: Optional[List[dict]] = Column(JSON)  # List of top skills
    skills: Optional[List[dict]] = Column(JSON)  # List of skills with levels
    response_rate: Optional[str] = Column(String)
    languages: Optional[List[dict]] = Column(JSON)  # List of languages with levels
    availability: Optional[str] = Column(String)
    missions_count: Optional[int] = Column(Integer)
    description: Optional[str] = Column(String)
    education: Optional[List[dict]] = Column(JSON)  # List of education entries
    expertise_domains: Optional[List[dict]] = Column(JSON)  # List of expertise domains
    experience: Optional[List[dict]] = Column(JSON)  # List of work experiences
    certifications: Optional[List[dict]] = Column(JSON)  # List of certifications
    status: ProfileStatus = Column(
        SQLAlchemyEnum(ProfileStatus), default=ProfileStatus.TODO, nullable=False
    )

    last_scraped_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    class Config:
        orm_mode = True
