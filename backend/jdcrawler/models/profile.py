from datetime import datetime
from pydantic import BaseModel, Field
from typing import List

class TechSkill(BaseModel):
    name: str
    level: str  # e.g., "Beginner", "Intermediate", "Advanced"
    description: str | None = None  # e.g., "Can distinguish functions and variables"

class UserProfile(BaseModel):
    tech_stack: List[TechSkill] = Field(default_factory=list)
    experience_years: int = 0
    interest_keywords: List[str] = Field(default_factory=list)
    exclude_keywords: List[str] = Field(default_factory=list)
    updated_at: datetime | None = None

class UserProfileUpdate(BaseModel):
    tech_stack: List[TechSkill]
    experience_years: int
    interest_keywords: List[str]
    exclude_keywords: List[str]