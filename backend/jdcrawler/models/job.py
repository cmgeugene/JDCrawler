from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, HttpUrl


class JobSite(str, Enum):
    SARAMIN = "saramin"
    JOBKOREA = "jobkorea"
    WANTED = "wanted"


class JobBase(BaseModel):
    title: str
    company: str
    url: str
    site: JobSite
    location: str | None = None
    salary: str | None = None
    experience: str | None = None
    posted_at: datetime | None = None
    deadline: str | None = None


class JobCreate(JobBase):
    pass


class Job(JobBase):
    id: int
    is_bookmarked: bool = False
    created_at: datetime


class JobResponse(Job):
    pass
