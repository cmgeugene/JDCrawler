import pytest


@pytest.fixture
def sample_job_data():
    return {
        "title": "Python Developer",
        "company": "Test Company",
        "location": "Seoul",
        "url": "https://example.com/job/1",
    }
