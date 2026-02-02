from datetime import datetime

from pydantic import BaseModel, field_validator


class KeywordCreate(BaseModel):
    keyword: str

    @field_validator("keyword")
    @classmethod
    def keyword_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("keyword cannot be empty")
        return v.strip()


class Keyword(KeywordCreate):
    id: int
    is_active: bool = True
    created_at: datetime
