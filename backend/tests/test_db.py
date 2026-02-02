import pytest

from jdcrawler.db.client import DatabaseClient
from jdcrawler.models.job import JobCreate, JobSite


@pytest.fixture
def db_client(tmp_path):
    db_path = tmp_path / "test.db"
    client = DatabaseClient(f"sqlite:///{db_path}")
    client.create_tables()
    yield client
    client.close()


class TestDatabaseClient:
    def test_create_tables(self, db_client):
        assert db_client.engine is not None

    def test_create_job(self, db_client):
        job_data = JobCreate(
            title="Python Developer",
            company="Test Corp",
            url="https://saramin.co.kr/job/1",
            site=JobSite.SARAMIN,
            location="Seoul",
        )
        job = db_client.create_job(job_data)
        assert job.id is not None
        assert job.title == "Python Developer"
        assert job.is_bookmarked is False

    def test_get_jobs(self, db_client):
        job_data = JobCreate(
            title="Backend Engineer",
            company="Tech Inc",
            url="https://wanted.co.kr/job/2",
            site=JobSite.WANTED,
        )
        db_client.create_job(job_data)
        jobs = db_client.get_jobs()
        assert len(jobs) == 1
        assert jobs[0].title == "Backend Engineer"

    def test_get_job_by_id(self, db_client):
        job_data = JobCreate(
            title="Frontend Dev",
            company="Startup",
            url="https://jobkorea.co.kr/job/3",
            site=JobSite.JOBKOREA,
        )
        created = db_client.create_job(job_data)
        fetched = db_client.get_job(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    def test_get_job_not_found(self, db_client):
        job = db_client.get_job(999)
        assert job is None

    def test_toggle_bookmark(self, db_client):
        job_data = JobCreate(
            title="DevOps",
            company="Cloud Co",
            url="https://saramin.co.kr/job/4",
            site=JobSite.SARAMIN,
        )
        job = db_client.create_job(job_data)
        assert job.is_bookmarked is False

        updated = db_client.toggle_bookmark(job.id)
        assert updated.is_bookmarked is True

        updated2 = db_client.toggle_bookmark(job.id)
        assert updated2.is_bookmarked is False

    def test_duplicate_url_not_created(self, db_client):
        job_data = JobCreate(
            title="Engineer",
            company="Company",
            url="https://saramin.co.kr/job/same",
            site=JobSite.SARAMIN,
        )
        job1 = db_client.create_job(job_data)
        job2 = db_client.create_job(job_data)
        assert job1.id == job2.id
        jobs = db_client.get_jobs()
        assert len(jobs) == 1


class TestKeywordCRUD:
    def test_create_keyword(self, db_client):
        keyword = db_client.create_keyword("python")
        assert keyword.id is not None
        assert keyword.keyword == "python"
        assert keyword.is_active is True

    def test_get_keywords(self, db_client):
        db_client.create_keyword("react")
        db_client.create_keyword("typescript")
        keywords = db_client.get_keywords()
        assert len(keywords) == 2

    def test_delete_keyword(self, db_client):
        keyword = db_client.create_keyword("java")
        db_client.delete_keyword(keyword.id)
        keywords = db_client.get_keywords()
        assert len(keywords) == 0

    def test_duplicate_keyword_not_created(self, db_client):
        kw1 = db_client.create_keyword("python")
        kw2 = db_client.create_keyword("python")
        assert kw1.id == kw2.id
        keywords = db_client.get_keywords()
        assert len(keywords) == 1
