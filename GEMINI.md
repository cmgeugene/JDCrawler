# JDCrawler

## Project Overview
JDCrawler is a full-stack application designed to aggregate job postings from major Korean job portals (Saramin, JobKorea, Wanted, etc.) and visualize them via a React-based dashboard. It uses a Python FastAPI backend with Playwright for crawling and a Modern React frontend.

## Architecture & Tech Stack

### Backend (`backend/`)
*   **Language:** Python 3.11+
*   **Framework:** FastAPI
*   **Crawler:** Playwright (dynamic), BeautifulSoup4 (static)
*   **Database:** SQLite (default) / PostgreSQL + SQLAlchemy
*   **Data Processing:** RapidFuzz (fuzzy matching for duplicates)
*   **Task Scheduling:** APScheduler
*   **Linting/Formatting:** Ruff
*   **Type Checking:** Pyright
*   **Testing:** Pytest

### Frontend (`frontend/`)
*   **Framework:** React 19
*   **Build Tool:** Vite
*   **Styling:** Tailwind CSS (v4), shadcn/ui principles
*   **State/Data Fetching:** React Query (@tanstack/react-query)
*   **Routing:** React Router DOM
*   **Visualization:** Recharts
*   **Testing:** Vitest

## Key Directories

*   **`backend/jdcrawler/`**: Main application logic.
    *   `api/`: FastAPI route handlers.
    *   `crawlers/`: Site-specific crawler implementations (base class in `base.py`).
    *   `models/`: Pydantic data models.
    *   `db/`: Database schemas and connection logic.
*   **`frontend/src/`**: React application source.
    *   `components/`: Reusable UI components.
    *   `pages/`: Route page components.
    *   `queries/`: React Query hooks.

## Development Workflow

### Backend Setup & Commands
Run these from the `backend/` directory:

1.  **Setup:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    playwright install chromium
    ```
2.  **Run Server:**
    ```bash
    # Via script (root)
    ./run_backend.sh
    # Manual
    uvicorn jdcrawler.main:app --reload
    ```
3.  **Quality Assurance:**
    ```bash
    ruff check .          # Lint
    ruff format .         # Format
    pyright               # Type check
    pytest                # Run tests
    ```

### Frontend Setup & Commands
Run these from the `frontend/` directory:

1.  **Setup:** `pnpm install`
2.  **Run Dev Server:** `pnpm dev`
3.  **Build:** `pnpm build`
4.  **Test:** `pnpm test`
5.  **Lint:** `pnpm lint`

## Coding Conventions & Guidelines (from `AGENTS.md`)

*   **Type Hints:** Mandatory for all functions and arguments.
*   **Imports:** Order: Standard Lib -> Third Party -> Local.
*   **Naming:**
    *   Files/Modules: `snake_case.py`
    *   Classes: `PascalCase`
    *   Functions/Variables: `snake_case`
*   **Crawling:**
    *   Respect `robots.txt` and rate limits.
    *   Use `data-*` attributes for selectors where possible.
    *   Handle dynamic content with Playwright.
*   **Testing:**
    *   Use HTML fixtures for crawler tests (no real HTTP requests in unit tests).
    *   Keep fixtures updated when site layouts change.

## References
*   See `AGENTS.md` for detailed agent instructions and crawler-specific guidelines.
*   See `backend/pyproject.toml` and `frontend/package.json` for full dependency lists.
