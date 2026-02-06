import pytest
from fastapi.testclient import TestClient

from jdcrawler.db.client import DatabaseClient
from jdcrawler.main import app
from jdcrawler.models.job import JobCreate, JobSite


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseClient(f"sqlite:///{db_path}")
    db.create_tables()

    app.state.db = db
    yield TestClient(app)
    db.close()


@pytest.fixture
def client_with_jobs(client, tmp_path):
    db = client.app.state.db
    db.create_job(
        JobCreate(
            title="Python Developer",
            company="Company A",
            url="https://saramin.co.kr/job/1",
            site=JobSite.SARAMIN,
            location="Seoul",
        )
    )
    db.create_job(
        JobCreate(
            title="React Developer",
            company="Company B",
            url="https://wanted.co.kr/job/2",
            site=JobSite.WANTED,
            location="Busan",
        )
    )
    db.create_job(
        JobCreate(
            title="Python Backend",
            company="Company C",
            url="https://jobkorea.co.kr/job/3",
            site=JobSite.JOBKOREA,
        )
    )
    return client


class TestJobsListAPI:
    def test_get_jobs_empty(self, client):
        response = client.get("/api/jobs")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_jobs_returns_list(self, client_with_jobs):
        response = client_with_jobs.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_get_jobs_search_by_title(self, client_with_jobs):
        response = client_with_jobs.get("/api/jobs?q=python")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("python" in job["title"].lower() for job in data)

    def test_get_jobs_filter_by_site(self, client_with_jobs):
        response = client_with_jobs.get("/api/jobs?site=saramin")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["site"] == "saramin"

    def test_get_jobs_pagination(self, client_with_jobs):
        response = client_with_jobs.get("/api/jobs?limit=2&offset=0")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestJobDetailAPI:
    def test_get_job_by_id(self, client_with_jobs):
        response = client_with_jobs.get("/api/jobs/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "Python Developer"

    def test_get_job_not_found(self, client):
        response = client.get("/api/jobs/999")
        assert response.status_code == 404


class TestBookmarkAPI:
    def test_toggle_bookmark(self, client_with_jobs):
        response = client_with_jobs.patch("/api/jobs/1/bookmark")
        assert response.status_code == 200
        data = response.json()
        assert data["is_bookmarked"] is True

        response = client_with_jobs.patch("/api/jobs/1/bookmark")
        assert response.status_code == 200
        data = response.json()
        assert data["is_bookmarked"] is False

    def test_toggle_bookmark_not_found(self, client):
        response = client.patch("/api/jobs/999/bookmark")
        assert response.status_code == 404


class TestHiddenAPI:
    def test_toggle_hidden(self, client_with_jobs):
        # 1. Hide job 1
        response = client_with_jobs.patch("/api/jobs/1/hidden")
        assert response.status_code == 200
        data = response.json()
        assert data["is_hidden"] is True

        # 2. Check list - Job 1 should be gone
        response = client_with_jobs.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        ids = [j["id"] for j in data]
        assert 1 not in ids

        # 3. Unhide job 1
        response = client_with_jobs.patch("/api/jobs/1/hidden")
        assert response.status_code == 200
        data = response.json()
        assert data["is_hidden"] is False

        # 4. Check list - Job 1 should be back
        response = client_with_jobs.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_toggle_hidden_not_found(self, client):
        response = client.patch("/api/jobs/999/hidden")
        assert response.status_code == 404


class TestJobStatsAPI:
    def test_get_job_stats(self, client_with_jobs):
        response = client_with_jobs.get("/api/jobs/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["saramin"] == 1
        assert data["wanted"] == 1
        assert data["jobkorea"] == 1

    def test_get_job_stats_empty(self, client):
        response = client.get("/api/jobs/stats")
        assert response.status_code == 200
        assert response.json() == {}
