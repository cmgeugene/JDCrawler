from unittest.mock import patch

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


class TestAnalysisAPI:
    def test_tech_stacks_empty(self, client):
        with patch("jdcrawler.api.analysis.get_db") as mock_get_db:
            mock_get_db.return_value.get_jobs.return_value = []
            response = client.get("/api/analysis/tech-stacks")
            assert response.status_code == 200
            data = response.json()
            assert data == {}

    def test_tech_stacks_endpoint_exists(self, client):
        response = client.get("/api/analysis/tech-stacks")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
