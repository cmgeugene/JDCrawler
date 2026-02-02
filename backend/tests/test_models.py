from datetime import date, datetime

import pytest
from pydantic import ValidationError

from jdcrawler.models.job import JobCreate, JobResponse, JobSite
from jdcrawler.models.keyword import Keyword, KeywordCreate


class TestJobModel:
    def test_job_create_valid(self):
        job = JobCreate(
            title="Python Developer",
            company="Test Company",
            url="https://saramin.co.kr/job/1",
            site=JobSite.SARAMIN,
        )
        assert job.title == "Python Developer"
        assert job.company == "Test Company"
        assert job.site == JobSite.SARAMIN

    def test_job_create_with_optional_fields(self):
        job = JobCreate(
            title="Backend Engineer",
            company="Tech Corp",
            url="https://wanted.co.kr/job/2",
            site=JobSite.WANTED,
            location="Seoul",
            salary="5000-7000만원",
            posted_at=date(2024, 1, 15),
        )
        assert job.location == "Seoul"
        assert job.salary == "5000-7000만원"
        assert job.posted_at == date(2024, 1, 15)

    def test_job_create_missing_required_field(self):
        with pytest.raises(ValidationError):
            JobCreate(
                title="Developer",
                company="Company",
            )

    def test_job_create_invalid_url(self):
        with pytest.raises(ValidationError):
            JobCreate(
                title="Developer",
                company="Company",
                url="not-a-url",
                site=JobSite.SARAMIN,
            )

    def test_job_response_has_id_and_timestamps(self):
        job = JobResponse(
            id=1,
            title="Developer",
            company="Company",
            url="https://example.com/job/1",
            site=JobSite.SARAMIN,
            is_bookmarked=False,
            created_at=datetime.now(),
        )
        assert job.id == 1
        assert job.is_bookmarked is False
        assert job.created_at is not None


class TestJobSite:
    def test_job_site_enum_values(self):
        assert JobSite.SARAMIN.value == "saramin"
        assert JobSite.JOBKOREA.value == "jobkorea"
        assert JobSite.WANTED.value == "wanted"


class TestKeywordModel:
    def test_keyword_create_valid(self):
        keyword = KeywordCreate(keyword="python")
        assert keyword.keyword == "python"

    def test_keyword_create_empty_string(self):
        with pytest.raises(ValidationError):
            KeywordCreate(keyword="")

    def test_keyword_create_whitespace_only(self):
        with pytest.raises(ValidationError):
            KeywordCreate(keyword="   ")

    def test_keyword_response_has_id_and_active(self):
        keyword = Keyword(
            id=1,
            keyword="react",
            is_active=True,
            created_at=datetime.now(),
        )
        assert keyword.id == 1
        assert keyword.is_active is True
