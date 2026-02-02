from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from jdcrawler.models.job import JobSite


class Base(DeclarativeBase):
    pass


class JobTable(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), unique=True, nullable=False)
    site: Mapped[str] = mapped_column(Enum(JobSite), nullable=False)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    salary: Mapped[str | None] = mapped_column(String(200), nullable=True)
    experience: Mapped[str | None] = mapped_column(String(100), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    deadline: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_bookmarked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class KeywordTable(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    keyword: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class NotificationTable(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_checked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
