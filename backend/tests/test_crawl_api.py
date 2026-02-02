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


class TestCrawlAPI:
    def test_crawl_status_endpoint_exists(self, client):
        response = client.get("/api/crawl/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "last_crawl" in data

    def test_invalid_site_returns_error(self, client):
        response = client.post(
            "/api/crawl", json={"site": "invalid", "keyword": "python"}
        )
        assert response.status_code == 422

    def test_missing_keyword_returns_error(self, client):
        response = client.post("/api/crawl", json={"site": "saramin"})
        assert response.status_code == 422
