import pytest
from fastapi.testclient import TestClient

from jdcrawler.db.client import DatabaseClient
from jdcrawler.main import app


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test.db"
    db = DatabaseClient(f"sqlite:///{db_path}")
    db.create_tables()
    app.state.db = db
    yield TestClient(app)
    db.close()


class TestE2E:
    def test_all_endpoints_available(self, client):
        health = client.get("/health")
        assert health.status_code == 200

        crawl_status = client.get("/api/crawl/status")
        assert crawl_status.status_code == 200

        jobs = client.get("/api/jobs")
        assert jobs.status_code == 200

        stats = client.get("/api/jobs/stats")
        assert stats.status_code == 200

        keywords = client.get("/api/keywords")
        assert keywords.status_code == 200

        analysis = client.get("/api/analysis/tech-stacks")
        assert analysis.status_code == 200
