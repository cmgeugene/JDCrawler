# JDCrawler

한국 채용 사이트 크롤링 및 대시보드 프로젝트

## Overview

사람인, 잡코리아, 원티드에서 채용공고를 수집하고 React 대시보드에서 조회/분석하는 풀스택 애플리케이션.

## Tech Stack

- **Backend**: Python 3.11+, FastAPI, Playwright, SQLAlchemy, RapidFuzz
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, shadcn/ui
- **Database**: SQLite

## Project Structure

```
JDCrawler/
├── backend/
│   ├── jdcrawler/
│   │   ├── api/          # FastAPI endpoints
│   │   ├── crawlers/     # Site-specific crawlers
│   │   ├── db/           # Database models & client
│   │   ├── models/       # Pydantic schemas
│   │   └── utils/        # Utilities (rate limiter, retry)
│   └── tests/
├── frontend/
│   └── src/
└── README.md
```

## Quick Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
playwright install chromium

# Run API server
uvicorn jdcrawler.main:app --reload
```

### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## Development

```bash
# Backend
cd backend
ruff check .          # Lint
ruff format .         # Format
pyright               # Type check
pytest                # Test

# Frontend
cd frontend
pnpm lint             # Lint
pnpm build            # Build
```

## License

MIT
