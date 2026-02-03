import json
from datetime import datetime

from rapidfuzz import fuzz
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from jdcrawler.db.schema import Base, UserBase, JobTable, KeywordTable, ProfileTable, NotificationTable
from jdcrawler.models.job import Job, JobCreate
from jdcrawler.models.keyword import Keyword
from jdcrawler.models.profile import UserProfile, UserProfileUpdate


class DatabaseClient:
    def __init__(
        self, 
        jobs_db_url: str = "sqlite:///./data/jobs.db",
        user_db_url: str = "sqlite:///./data/user.db"
    ):
        self.jobs_engine = create_engine(jobs_db_url, echo=False)
        self.user_engine = create_engine(user_db_url, echo=False)
        self._jobs_session: Session | None = None
        self._user_session: Session | None = None

    def create_tables(self):
        Base.metadata.create_all(self.jobs_engine)
        UserBase.metadata.create_all(self.user_engine)

    def close(self):
        if self._jobs_session:
            self._jobs_session.close()
        if self._user_session:
            self._user_session.close()
        self.jobs_engine.dispose()
        self.user_engine.dispose()

    @property
    def jobs_session(self) -> Session:
        if self._jobs_session is None:
            self._jobs_session = Session(self.jobs_engine)
        return self._jobs_session

    @property
    def user_session(self) -> Session:
        if self._user_session is None:
            self._user_session = Session(self.user_engine)
        return self._user_session

    def create_job(self, job_data: JobCreate) -> Job:
        # 1. Exact URL match
        existing = self.jobs_session.execute(
            select(JobTable).where(JobTable.url == str(job_data.url))
        ).scalar_one_or_none()

        if existing:
            return self._job_table_to_model(existing)

        # 2. Fuzzy matching: Check similar company & similar title
        # Fetch recent jobs to compare (last 500 for performance)
        recent_jobs = self.jobs_session.execute(
            select(JobTable).order_by(JobTable.created_at.desc()).limit(500)
        ).scalars().all()

        for r_job in recent_jobs:
            # 2a. Compare Company Name (Handle minor variations like (주), corp, etc.)
            company_sim = fuzz.token_set_ratio(job_data.company, r_job.company)
            
            # 2b. Compare Title
            title_sim = fuzz.token_set_ratio(job_data.title, r_job.title)
            
            # If both company and title are very similar, consider it a duplicate
            # Company must be at least 90% similar OR exactly match
            # Title must be at least 85% similar
            if company_sim >= 90 and title_sim >= 85:
                print(f"Skipping duplicate job (Company: {company_sim}%, Title: {title_sim}%): '{job_data.company} - {job_data.title}'")
                return self._job_table_to_model(r_job)

        job = JobTable(
            title=job_data.title,
            company=job_data.company,
            url=str(job_data.url),
            site=job_data.site,
            location=job_data.location,
            salary=job_data.salary,
            experience=job_data.experience,
            posted_at=job_data.posted_at,
            deadline=job_data.deadline,
            is_bookmarked=False,
            created_at=datetime.now(),
            description=job_data.description,
            description_image_url=job_data.description_image_url,
            ai_score=job_data.ai_score,
            ai_summary=job_data.ai_summary,
            ai_status=job_data.ai_status,
        )
        self.jobs_session.add(job)
        self.jobs_session.commit()
        self.jobs_session.refresh(job)
        return self._job_table_to_model(job)

    def get_jobs(
        self,
        search: str | None = None,
        site: str | None = None,
        bookmarked: bool | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Job]:
        query = select(JobTable)

        if search:
            query = query.where(
                JobTable.title.ilike(f"%{search}%")
                | JobTable.company.ilike(f"%{search}%")
            )
        if site:
            query = query.where(JobTable.site == site)
        if bookmarked is not None:
            query = query.where(JobTable.is_bookmarked == bookmarked)

        query = query.order_by(JobTable.created_at.desc()).limit(limit).offset(offset)
        results = self.jobs_session.execute(query).scalars().all()
        return [self._job_table_to_model(j) for j in results]

    def get_job(self, job_id: int) -> Job | None:
        job = self.jobs_session.get(JobTable, job_id)
        if job:
            return self._job_table_to_model(job)
        return None

    def toggle_bookmark(self, job_id: int) -> Job:
        job = self.jobs_session.get(JobTable, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        job.is_bookmarked = not job.is_bookmarked
        self.jobs_session.commit()
        self.jobs_session.refresh(job)
        return self._job_table_to_model(job)

    def get_job_stats(self) -> dict[str, int]:
        jobs = self.jobs_session.execute(select(JobTable)).scalars().all()
        stats: dict[str, int] = {}
        for job in jobs:
            site = job.site.value if hasattr(job.site, "value") else str(job.site)
            stats[site] = stats.get(site, 0) + 1
        return stats

    def create_keyword(self, keyword: str) -> Keyword:
        existing = self.user_session.execute(
            select(KeywordTable).where(KeywordTable.keyword == keyword)
        ).scalar_one_or_none()

        if existing:
            return self._keyword_table_to_model(existing)

        kw = KeywordTable(
            keyword=keyword,
            is_active=True,
            created_at=datetime.now(),
        )
        self.user_session.add(kw)
        self.user_session.commit()
        self.user_session.refresh(kw)
        return self._keyword_table_to_model(kw)

    def get_keywords(self, only_active: bool = False) -> list[Keyword]:
        query = select(KeywordTable)
        if only_active:
            query = query.where(KeywordTable.is_active == True)
        results = self.user_session.execute(query).scalars().all()
        return [self._keyword_table_to_model(k) for k in results]

    def delete_keyword(self, keyword_id: int) -> None:
        kw = self.user_session.get(KeywordTable, keyword_id)
        if kw:
            self.user_session.delete(kw)
            self.user_session.commit()

    def get_profile(self) -> UserProfile:
        profile = self.user_session.execute(select(ProfileTable)).scalar_one_or_none()
        if not profile:
            # Create a default profile if none exists
            profile = ProfileTable(
                tech_stack="[]",
                experience_years=0,
                interest_keywords="[]",
                exclude_keywords="[]"
            )
            self.user_session.add(profile)
            self.user_session.commit()
            self.user_session.refresh(profile)
        
        return UserProfile(
            tech_stack=json.loads(profile.tech_stack),
            experience_years=profile.experience_years,
            interest_keywords=json.loads(profile.interest_keywords),
            exclude_keywords=json.loads(profile.exclude_keywords),
            updated_at=profile.updated_at
        )

    def update_profile(self, data: UserProfileUpdate) -> UserProfile:
        profile = self.user_session.execute(select(ProfileTable)).scalar_one_or_none()
        if not profile:
            profile = ProfileTable()
            self.user_session.add(profile)
        
        # Convert Pydantic objects to dicts for JSON serialization
        tech_stack_data = [skill.model_dump() for skill in data.tech_stack]
        
        profile.tech_stack = json.dumps(tech_stack_data)
        profile.experience_years = data.experience_years
        profile.interest_keywords = json.dumps(data.interest_keywords)
        profile.exclude_keywords = json.dumps(data.exclude_keywords)
        profile.updated_at = datetime.now()
        
        self.user_session.commit()
        self.user_session.refresh(profile)
        return self.get_profile()

    def get_new_jobs_count(self) -> int:
        notification = self.user_session.execute(select(NotificationTable)).scalar_one_or_none()
        if not notification:
            notification = NotificationTable(last_checked_at=datetime(1970, 1, 1))
            self.user_session.add(notification)
            self.user_session.commit()
            self.user_session.refresh(notification)

        count = (
            self.jobs_session.query(JobTable)
            .filter(JobTable.created_at > notification.last_checked_at)
            .count()
        )
        return count

    def mark_read(self) -> None:
        notification = self.user_session.execute(select(NotificationTable)).scalar_one_or_none()
        if not notification:
            notification = NotificationTable(last_checked_at=datetime.now())
            self.user_session.add(notification)
        else:
            notification.last_checked_at = datetime.now()
        self.user_session.commit()

    def _job_table_to_model(self, job: JobTable) -> Job:
        return Job(
            id=job.id,
            title=job.title,
            company=job.company,
            url=job.url,
            site=job.site,
            location=job.location,
            salary=job.salary,
            experience=job.experience,
            posted_at=job.posted_at.date() if job.posted_at else None,
            deadline=job.deadline,
            is_bookmarked=job.is_bookmarked,
            created_at=job.created_at,
            description=job.description,
            description_image_url=job.description_image_url,
            ai_score=job.ai_score,
            ai_summary=job.ai_summary,
            ai_status=job.ai_status,
        )

    def _keyword_table_to_model(self, kw: KeywordTable) -> Keyword:
        return Keyword(
            id=kw.id,
            keyword=kw.keyword,
            is_active=kw.is_active,
            created_at=kw.created_at,
        )
