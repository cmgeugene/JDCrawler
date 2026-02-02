from datetime import datetime

from rapidfuzz import fuzz
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from jdcrawler.db.schema import Base, JobTable, KeywordTable
from jdcrawler.models.job import Job, JobCreate
from jdcrawler.models.keyword import Keyword


class DatabaseClient:
    def __init__(self, database_url: str = "sqlite:///./data/jobs.db"):
        self.engine = create_engine(database_url, echo=False)
        self._session: Session | None = None

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def close(self):
        if self._session:
            self._session.close()
        self.engine.dispose()

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = Session(self.engine)
        return self._session

    def create_job(self, job_data: JobCreate) -> Job:
        # 1. Exact URL match
        existing = self.session.execute(
            select(JobTable).where(JobTable.url == str(job_data.url))
        ).scalar_one_or_none()

        if existing:
            return self._job_table_to_model(existing)

        # 2. Fuzzy matching: Check same company & similar title
        # Fetch jobs from the same company
        company_jobs = self.session.execute(
            select(JobTable).where(JobTable.company == job_data.company)
        ).scalars().all()

        for c_job in company_jobs:
            # token_set_ratio is better for partial matches and reordering
            similarity = fuzz.token_set_ratio(job_data.title, c_job.title)
            if similarity >= 85:
                print(f"Skipping duplicate job (similarity {similarity}%): '{job_data.title}' == '{c_job.title}'")
                return self._job_table_to_model(c_job)

        job = JobTable(
            title=job_data.title,
            company=job_data.company,
            url=str(job_data.url),
            site=job_data.site,
            location=job_data.location,
            salary=job_data.salary,
            posted_at=job_data.posted_at,
            is_bookmarked=False,
            created_at=datetime.now(),
        )
        self.session.add(job)
        self.session.commit()
        self.session.refresh(job)
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
        results = self.session.execute(query).scalars().all()
        return [self._job_table_to_model(j) for j in results]

    def get_job(self, job_id: int) -> Job | None:
        job = self.session.get(JobTable, job_id)
        if job:
            return self._job_table_to_model(job)
        return None

    def toggle_bookmark(self, job_id: int) -> Job:
        job = self.session.get(JobTable, job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        job.is_bookmarked = not job.is_bookmarked
        self.session.commit()
        self.session.refresh(job)
        return self._job_table_to_model(job)

    def get_job_stats(self) -> dict[str, int]:
        jobs = self.session.execute(select(JobTable)).scalars().all()
        stats: dict[str, int] = {}
        for job in jobs:
            site = job.site.value if hasattr(job.site, "value") else str(job.site)
            stats[site] = stats.get(site, 0) + 1
        return stats

    def create_keyword(self, keyword: str) -> Keyword:
        existing = self.session.execute(
            select(KeywordTable).where(KeywordTable.keyword == keyword)
        ).scalar_one_or_none()

        if existing:
            return self._keyword_table_to_model(existing)

        kw = KeywordTable(
            keyword=keyword,
            is_active=True,
            created_at=datetime.now(),
        )
        self.session.add(kw)
        self.session.commit()
        self.session.refresh(kw)
        return self._keyword_table_to_model(kw)

    def get_keywords(self, only_active: bool = False) -> list[Keyword]:
        query = select(KeywordTable)
        if only_active:
            query = query.where(KeywordTable.is_active == True)
        results = self.session.execute(query).scalars().all()
        return [self._keyword_table_to_model(k) for k in results]

    def delete_keyword(self, keyword_id: int) -> None:
        kw = self.session.get(KeywordTable, keyword_id)
        if kw:
            self.session.delete(kw)
            self.session.commit()

    def _job_table_to_model(self, job: JobTable) -> Job:
        return Job(
            id=job.id,
            title=job.title,
            company=job.company,
            url=job.url,
            site=job.site,
            location=job.location,
            salary=job.salary,
            posted_at=job.posted_at.date() if job.posted_at else None,
            is_bookmarked=job.is_bookmarked,
            created_at=job.created_at,
        )

    def _keyword_table_to_model(self, kw: KeywordTable) -> Keyword:
        return Keyword(
            id=kw.id,
            keyword=kw.keyword,
            is_active=kw.is_active,
            created_at=kw.created_at,
        )
