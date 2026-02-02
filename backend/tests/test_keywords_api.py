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


class TestKeywordsAPI:
    def test_get_keywords_empty(self, client):
        response = client.get("/api/keywords")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_keyword(self, client):
        response = client.post("/api/keywords", json={"keyword": "python"})
        assert response.status_code == 201
        data = response.json()
        assert data["keyword"] == "python"
        assert data["is_active"] is True
        assert "id" in data

    def test_create_keyword_empty_string(self, client):
        response = client.post("/api/keywords", json={"keyword": ""})
        assert response.status_code == 422

    def test_get_keywords_returns_list(self, client):
        client.post("/api/keywords", json={"keyword": "python"})
        client.post("/api/keywords", json={"keyword": "react"})
        response = client.get("/api/keywords")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_delete_keyword(self, client):
        create_response = client.post("/api/keywords", json={"keyword": "java"})
        keyword_id = create_response.json()["id"]

        response = client.delete(f"/api/keywords/{keyword_id}")
        assert response.status_code == 204

        get_response = client.get("/api/keywords")
        assert len(get_response.json()) == 0

    def test_delete_keyword_not_found(self, client):
        response = client.delete("/api/keywords/999")
        assert response.status_code == 404


class TestNotificationsAPI:
    def test_get_new_jobs_count_empty(self, client):
        response = client.get("/api/notifications/new-jobs-count")
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_get_new_jobs_count_with_jobs(self, client):
        db = client.app.state.db
        db.create_job(
            JobCreate(
                title="Python Dev",
                company="Company",
                url="https://saramin.co.kr/job/1",
                site=JobSite.SARAMIN,
            )
        )
        response = client.get("/api/notifications/new-jobs-count")
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_mark_read_resets_count(self, client):
        db = client.app.state.db
        db.create_job(
            JobCreate(
                title="Python Dev",
                company="Company",
                url="https://saramin.co.kr/job/1",
                site=JobSite.SARAMIN,
            )
        )

        count_response = client.get("/api/notifications/new-jobs-count")
        assert count_response.json()["count"] == 1

        mark_response = client.post("/api/notifications/mark-read")
        assert mark_response.status_code == 200

        count_after = client.get("/api/notifications/new-jobs-count")
        assert count_after.json()["count"] == 0
