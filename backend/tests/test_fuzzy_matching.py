import pytest
from jdcrawler.db.client import DatabaseClient
from jdcrawler.models.job import JobCreate, JobSite

@pytest.fixture
def db_client(tmp_path):
    db_path = tmp_path / "test_fuzzy.db"
    db = DatabaseClient(f"sqlite:///{db_path}")
    db.create_tables()
    yield db
    db.close()

def test_fuzzy_duplicate_detection(db_client):
    # 1. Create initial job
    job1_data = JobCreate(
        title="Python Backend Developer",
        company="Tech Corp",
        url="http://example.com/1",
        site=JobSite.WANTED,
        location="Seoul",
        salary="5000",
    )
    job1 = db_client.create_job(job1_data)
    assert job1.id is not None

    # 2. Create duplicate job (similar title, same company)
    # "Backend Python Developer" is very similar to "Python Backend Developer"
    job2_data = JobCreate(
        title="Backend Developer (Python)", 
        company="Tech Corp",
        url="http://example.com/2", # Different URL
        site=JobSite.JOBKOREA,      # Different site
        location="Seoul",
    )
    job2 = db_client.create_job(job2_data)

    # Should be detected as duplicate and return job1
    assert job2.id == job1.id
    assert job2.title == job1.title # Should return the existing job's title

    # 3. Create non-duplicate job (same company, different title)
    job3_data = JobCreate(
        title="Frontend Developer",
        company="Tech Corp",
        url="http://example.com/3",
        site=JobSite.WANTED,
    )
    job3 = db_client.create_job(job3_data)

    # Should be a new job
    assert job3.id != job1.id

    # Verify total count
    jobs = db_client.get_jobs(limit=100)
    assert len(jobs) == 2 # job1 and job3 only
