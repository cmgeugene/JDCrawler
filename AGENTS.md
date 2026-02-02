# AGENTS.md - JDCrawler

한국 채용 사이트(사람인, 잡코리아, 원티드, 로켓펀치, 점핏) 크롤링 프로젝트.

## Tech Stack

- **Runtime**: Python 3.11+
- **Crawler**: Playwright (동적), BeautifulSoup4 (정적)
- **Database**: SQLite / PostgreSQL + SQLAlchemy
- **Data**: pandas, pydantic, rapidfuzz
- **Testing**: pytest
- **Linting**: Ruff (formatter + linter)
- **Type Check**: pyright

## Duplicate Detection Strategy

We use `rapidfuzz` to detect duplicate jobs across different platforms or slightly different titles.

1.  **Exact Match**: First, check for exact URL match.
2.  **Fuzzy Match**:
    *   Filter jobs by **exact company name**.
    *   Calculate `token_set_ratio` similarity between titles.
    *   If similarity >= **85%**, consider it a duplicate and skip saving.

## Commands

```bash
# 환경 설정
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
playwright install chromium

# 개발
python -m jdcrawler          # Run crawler
python -m jdcrawler saramin  # 사람인 only

# Linting and Formatting
ruff check .                 # Lint check
ruff check --fix .           # Lint auto-fix
ruff format .                # Format code

# Type Check
pyright                      # Type check all

# Testing
pytest                       # Run all tests
pytest tests/test_saramin.py # Run single file
pytest -k "test_parse"       # Run by test name
pytest -v                    # Verbose output

# Database
alembic upgrade head         # Run migrations
alembic revision --autogenerate -m "msg"  # Generate migration
```

## Project Structure

```
jdcrawler/
├── __init__.py
├── __main__.py           # Entry point
├── crawlers/
│   ├── __init__.py
│   ├── base.py           # Abstract base class
│   ├── saramin.py
│   ├── jobkorea.py
│   └── wanted.py
├── models/
│   ├── __init__.py
│   └── job.py            # Pydantic models
├── db/
│   ├── __init__.py
│   ├── schema.py         # SQLAlchemy models
│   └── client.py
└── utils/
    ├── __init__.py
    ├── rate_limiter.py
    └── retry.py

tests/
├── conftest.py           # pytest fixtures
├── fixtures/             # HTML fixtures
├── test_saramin.py
└── test_parser.py
```

## Code Style

### Imports (순서)
```python
# 1. Standard library
import asyncio
from pathlib import Path

# 2. Third-party
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd

# 3. Local
from jdcrawler.models import Job
from jdcrawler.utils import rate_limit
```

### Naming
- Files/Modules: `snake_case.py`
- Classes: `PascalCase`
- Functions/Variables: `snake_case`
- Constants: `SCREAMING_SNAKE_CASE`

### Type Hints (필수)
```python
async def fetch_job(job_id: str) -> Job | None:
    """Fetch a single job by ID."""
    ...

def parse_jobs(html: str) -> list[Job]:
    """Parse job listings from HTML."""
    ...
```

### Pydantic Models
```python
from pydantic import BaseModel, HttpUrl

class Job(BaseModel):
    title: str
    company: str
    location: str | None = None
    salary: str | None = None
    url: HttpUrl
    posted_at: date | None = None
```

### Error Handling
```python
class CrawlerError(Exception):
    def __init__(self, message: str, site: str, cause: Exception | None = None):
        super().__init__(message)
        self.site = site
        self.cause = cause

# NEVER: bare except, pass in except block
```

## Crawler Guidelines

### Rate Limiting (CRITICAL)
```python
RATE_LIMIT = {"requests_per_minute": 10, "delay_sec": 3.0}

async def respectful_request():
    await asyncio.sleep(RATE_LIMIT["delay_sec"] + random.uniform(0, 2))
```

### Selectors
```python
# Prefer: data-* > semantic > CSS classes
SELECTORS = {
    "job_card": "[data-job-card]",     # Best
    "job_title": "h2.job-title",       # OK
    "company": ".info > span",         # Avoid (fragile)
}
```

### Async Pattern
```python
async def crawl_all(urls: list[str]) -> list[Job]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        results = await asyncio.gather(*[fetch(url) for url in urls])
        await browser.close()
    return results
```

## Testing

```python
# tests/test_saramin.py
import pytest
from pathlib import Path

@pytest.fixture
def saramin_html():
    return Path("tests/fixtures/saramin.html").read_text()

def test_parse_job_listing(saramin_html):
    jobs = parse_jobs(saramin_html)
    assert len(jobs) > 0
    assert jobs[0].title
    assert jobs[0].company
```
- Use HTML fixtures, never real HTTP in unit tests
- Update fixtures when sites change

## Environment

```bash
# .env
DATABASE_URL="sqlite:///./data/jobs.db"
HEADLESS="true"
LOG_LEVEL="INFO"
```

## Git Commits

```
feat: 새 크롤러 추가
fix: 셀렉터 업데이트
test: 파서 테스트 추가
```

## AI Agent Notes

1. **사이트 변경 주의**: 채용 사이트 마크업 자주 변경됨
2. **법적 준수**: robots.txt 준수, 과도한 요청 금지
3. **동적 렌더링**: 대부분 Playwright 필요
4. **중복 처리**: URL/ID 기반 중복 체크 필수
5. **확장 계획**: pandas 분석, LLM 연동 고려
