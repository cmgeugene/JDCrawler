from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, HttpUrl


class JobSite(str, Enum):
    SARAMIN = "saramin"
    JOBKOREA = "jobkorea"
    WANTED = "wanted"


class JobCreate(BaseModel):
    title: str
    company: str
    url: HttpUrl
    site: JobSite
    location: str | None = None
    salary: str | None = None
    posted_at: date | None = None


class Job(JobCreate):
    id: int
    is_bookmarked: bool = False
    created_at: datetime


class JobResponse(Job):
    pass
