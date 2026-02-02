# JDCrawler - 채용공고 크롤링 자동화 프로젝트

## Context

### Original Request
AX 포지션 지원용 포트폴리오 프로젝트. 한국 채용 사이트(사람인, 잡코리아, 원티드)에서 채용공고를 크롤링하고, 대시보드에서 조회/분석하는 풀스택 애플리케이션. 실사용 겸용.

### Interview Summary
**Key Discussions**:
- 언어: Python 3.11+ (AX 포지션에 적합)
- 크롤러: Playwright (동적 렌더링 필수)
- 백엔드: FastAPI (REST API)
- 프론트엔드: React + Vite + TypeScript + Tailwind + shadcn/ui
- DB: SQLite (로컬 전용)
- 테스트: TDD with pytest
- 구조: 모노레포 (/backend, /frontend)

**Research Findings**:
- 채용 사이트들은 마크업이 자주 변경됨 → 셀렉터 분리 설계 필요
- 대부분 JavaScript 렌더링 → Playwright 필수
- Rate limiting 필수 (법적 준수)

---

## Work Objectives

### Core Objective
한국 채용 사이트 3곳(사람인, 잡코리아, 원티드)에서 채용공고를 크롤링하고, React 대시보드에서 조회/분석/북마크할 수 있는 풀스택 애플리케이션 구축.

### Concrete Deliverables
- `/backend`: FastAPI 서버 + Playwright 크롤러
- `/frontend`: React 대시보드
- SQLite 데이터베이스
- pytest 테스트 스위트

### Definition of Done
- [ ] 3개 사이트 크롤링 동작 확인
- [ ] 대시보드에서 공고 목록 조회/검색/필터링 가능
- [ ] 북마크 기능 동작
- [ ] 키워드 분석 차트 표시
- [ ] 새 공고 뱃지 표시
- [ ] `pytest` 전체 통과
- [ ] `ruff check .` 에러 없음

### Must Have
- 채용공고 목록 (검색, 필터링, 정렬)
- 사이트별 수집 현황 차트
- 키워드/기술 스택 분석
- 새 공고 알림 (대시보드 뱃지)
- 관심 공고 북마크
- 공고 상세 보기
- 수동 크롤링 버튼
- 자동 스케줄링 (하루 1~2회)
- 대시보드에서 검색 키워드 설정

### Must NOT Have (Guardrails)
- ❌ 로그인/회원가입 구현
- ❌ 실제 배포 설정 (Docker, CI/CD 등)
- ❌ LLM API 연동 (확장 가능하게 설계만)
- ❌ 지원 현황 관리 기능
- ❌ 과도한 크롤링 (rate limit 반드시 준수)
- ❌ 불필요한 추상화/과도한 패턴

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: NO (신규 프로젝트)
- **User wants tests**: YES (TDD)
- **Framework**: pytest

### TDD Workflow
각 TODO는 RED-GREEN-REFACTOR 패턴:
1. **RED**: 실패하는 테스트 먼저 작성
2. **GREEN**: 테스트 통과하는 최소 구현
3. **REFACTOR**: 코드 정리 (테스트 유지)

---

## Task Flow

```
Phase 1: 프로젝트 설정
  [1] → [2] → [3]

Phase 2: 백엔드 코어
  [4] → [5] → [6] → [7] → [8]

Phase 3: 크롤러
  [9] → [10] → [11] → [12]

Phase 4: 프론트엔드
  [13] → [14] → [15] → [16] → [17] → [18]

Phase 5: 통합
  [19] → [20] → [21]
```

## Parallelization

| Group | Tasks | Reason |
|-------|-------|--------|
| A | 10, 11, 12 | 각 사이트 크롤러 독립 |
| B | 15, 16, 17 | 각 대시보드 페이지 독립 |

---

## TODOs

### Phase 1: 프로젝트 설정

- [x] 1. 모노레포 초기 구조 설정

  **What to do**:
  - `git init` 실행
  - 루트에 `pyproject.toml` 생성 (프로젝트 메타데이터)
  - `/backend` 폴더 생성 + Python 패키지 구조
  - `/frontend` 폴더 생성 + Vite React 프로젝트
  - `.gitignore` 설정 (Python, Node, .env 등)
  - `.env.example` 생성 (DATABASE_URL, HEADLESS 등)
  - `README.md` 기본 작성

  **Must NOT do**:
  - Docker 설정
  - CI/CD 설정
  - 실제 `.env` 파일 커밋

  **Parallelizable**: NO (최초 설정)

  **References**:
  - `AGENTS.md` - 프로젝트 구조 참고

  **Acceptance Criteria**:
  - [ ] `git status` 동작 (레포 초기화 확인)
  - [ ] `/backend/jdcrawler/__init__.py` 존재
  - [ ] `/frontend/package.json` 존재
  - [ ] `.env.example` 존재
  - [ ] `python -c "import jdcrawler"` 성공 (backend 폴더에서)
  - [ ] `cd frontend && pnpm dev` 실행 가능

  **Commit**: YES
  - Message: `chore: 모노레포 초기 구조 설정`
  - Files: `pyproject.toml`, `backend/`, `frontend/`, `.gitignore`, `README.md`

---

- [x] 2. Backend 개발 환경 설정

  **What to do**:
  - `backend/pyproject.toml` 생성 (의존성: fastapi, uvicorn, playwright, sqlalchemy, pydantic, pytest, ruff, pyright)
  - Ruff 설정 (`ruff.toml`)
  - pyright 설정 (`pyrightconfig.json`)
  - pytest 설정 (`pyproject.toml`에 포함)
  - `backend/jdcrawler/` 패키지 구조 생성
  - `playwright install chromium` 실행

  **Must NOT do**:
  - 실제 코드 구현 (설정만)

  **Parallelizable**: NO (1번 이후)

  **References**:
  - `AGENTS.md` - Tech Stack, Commands 섹션

  **Acceptance Criteria**:
  - [ ] `cd backend && pip install -e ".[dev]"` 성공
  - [ ] `playwright install chromium` 성공
  - [ ] `ruff check .` 실행 가능
  - [ ] `pyright` 실행 가능
  - [ ] `pytest` 실행 가능 (테스트 0개)

  **Commit**: YES
  - Message: `chore(backend): 개발 환경 설정`
  - Files: `backend/pyproject.toml`, `backend/ruff.toml`, `backend/pyrightconfig.json`

---

- [x] 3. Frontend 개발 환경 설정

  **What to do**:
  - Vite + React + TypeScript 프로젝트 초기화
  - Tailwind CSS 설정
  - shadcn/ui 설정
  - ESLint + Prettier 설정
  - 기본 App.tsx 정리

  **Must NOT do**:
  - 실제 컴포넌트 구현

  **Parallelizable**: NO (1번 이후)

  **References**:
  - Vite 공식 문서
  - shadcn/ui 설치 가이드

  **Acceptance Criteria**:
  - [ ] `cd frontend && pnpm install` 성공
  - [ ] `pnpm dev` → 브라우저에서 기본 페이지 표시
  - [ ] `pnpm lint` 에러 없음
  - [ ] Tailwind 클래스 동작 확인

  **Commit**: YES
  - Message: `chore(frontend): 개발 환경 설정`
  - Files: `frontend/`

---

### Phase 2: 백엔드 코어

- [x] 4. Pydantic 모델 정의 (Job, Keyword)

  **What to do**:
  - TDD: 먼저 모델 테스트 작성
  - `Job` 모델: title, company, location, salary, url, site, posted_at, created_at, is_bookmarked
  - `Keyword` 모델: id, keyword, is_active, created_at
  - `JobCreate`, `JobResponse` 등 API용 스키마

  **Must NOT do**:
  - DB 연동 (별도 태스크)

  **Parallelizable**: NO (2번 이후)

  **References**:
  - `AGENTS.md` - Pydantic Models 섹션

  **Acceptance Criteria**:
  - [ ] `tests/test_models.py` 존재
  - [ ] `pytest tests/test_models.py` 통과
  - [ ] Job 모델 필드 타입 검증 동작

  **Commit**: YES
  - Message: `feat(backend): Job, Keyword Pydantic 모델 정의`
  - Files: `backend/jdcrawler/models/`, `backend/tests/test_models.py`

---

- [x] 5. SQLAlchemy 스키마 및 DB 클라이언트

  **What to do**:
  - TDD: DB 연결 테스트 먼저 작성
  - SQLAlchemy 모델 (jobs, keywords 테이블)
  - SQLite 연결 클라이언트
  - 기본 CRUD 함수 (create_job, get_jobs, etc.)

  **Must NOT do**:
  - Alembic 마이그레이션 (초기에는 create_all 사용)

  **Parallelizable**: NO (4번 이후)

  **References**:
  - `AGENTS.md` - Project Structure (db/ 폴더)

  **Acceptance Criteria**:
  - [ ] `tests/test_db.py` 존재
  - [ ] `pytest tests/test_db.py` 통과
  - [ ] Job 생성/조회/삭제 동작
  - [ ] SQLite 파일 생성 확인

  **Commit**: YES
  - Message: `feat(backend): SQLAlchemy 스키마 및 DB 클라이언트`
  - Files: `backend/jdcrawler/db/`, `backend/tests/test_db.py`

---

- [x] 6. FastAPI 기본 설정 및 Health Check

  **What to do**:
  - TDD: API 테스트 먼저 작성 (TestClient)
  - FastAPI 앱 생성 (`main.py`)
  - CORS 설정 (localhost)
  - Health check 엔드포인트 (`GET /health`)

  **Must NOT do**:
  - 인증/인가

  **Parallelizable**: NO (5번 이후)

  **References**:
  - FastAPI 공식 문서 - Testing

  **Acceptance Criteria**:
  - [ ] `tests/test_api.py` 존재
  - [ ] `pytest tests/test_api.py` 통과
  - [ ] `GET /health` → `{"status": "ok"}`
  - [ ] CORS 헤더 확인

  **Commit**: YES
  - Message: `feat(backend): FastAPI 기본 설정 및 Health Check`
  - Files: `backend/jdcrawler/main.py`, `backend/tests/test_api.py`

---

- [x] 7. Jobs API 엔드포인트

  **What to do**:
  - TDD: 각 엔드포인트 테스트 먼저
  - `GET /api/jobs` - 목록 조회 (검색, 필터링, 정렬, 페이지네이션)
  - `GET /api/jobs/{id}` - 상세 조회
  - `PATCH /api/jobs/{id}/bookmark` - 북마크 토글
  - `GET /api/jobs/stats` - 사이트별 통계

  **Must NOT do**:
  - Job 생성/삭제 API (크롤러가 직접 DB 접근)

  **Parallelizable**: NO (6번 이후)

  **References**:
  - FastAPI 공식 문서 - Path Parameters, Query Parameters

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_jobs_api.py` 통과
  - [ ] 검색 쿼리 동작 (`?q=python`)
  - [ ] 사이트 필터 동작 (`?site=saramin`)
  - [ ] 정렬 동작 (`?sort=posted_at`)
  - [ ] 북마크 토글 동작

  **Commit**: YES
  - Message: `feat(backend): Jobs API 엔드포인트`
  - Files: `backend/jdcrawler/api/jobs.py`, `backend/tests/test_jobs_api.py`

---

- [x] 8. Keywords API 및 새 공고 알림

  **What to do**:
  - TDD: 테스트 먼저
  - `GET /api/keywords` - 키워드 목록
  - `POST /api/keywords` - 키워드 추가
  - `DELETE /api/keywords/{id}` - 키워드 삭제
  - `GET /api/notifications/new-jobs-count` - 마지막 확인 이후 새 공고 수
  - `POST /api/notifications/mark-read` - 확인 처리

  **Must NOT do**:
  - 이메일/슬랙 알림

  **Parallelizable**: NO (7번 이후)

  **References**:
  - Draft 문서 - 알림 섹션

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_keywords_api.py` 통과
  - [ ] 키워드 CRUD 동작
  - [ ] 새 공고 카운트 정확히 반환

  **Commit**: YES
  - Message: `feat(backend): Keywords API 및 새 공고 알림`
  - Files: `backend/jdcrawler/api/keywords.py`, `backend/tests/test_keywords_api.py`

---

### Phase 3: 크롤러

- [x] 9. 크롤러 베이스 클래스 및 유틸리티

  **What to do**:
  - TDD: 유틸리티 테스트 먼저
  - `BaseCrawler` 추상 클래스 (async)
  - Rate limiter 유틸리티
  - Retry 유틸리티 (exponential backoff)
  - Playwright 브라우저 관리

  **Must NOT do**:
  - 실제 사이트 크롤링

  **Parallelizable**: NO (5번 이후)

  **References**:
  - `AGENTS.md` - Crawler Guidelines

  **Acceptance Criteria**:
  - [ ] `pytest tests/test_crawler_utils.py` 통과
  - [ ] Rate limiter 딜레이 동작
  - [ ] Retry 로직 동작

  **Commit**: YES
  - Message: `feat(backend): 크롤러 베이스 클래스 및 유틸리티`
  - Files: `backend/jdcrawler/crawlers/base.py`, `backend/jdcrawler/utils/`

---

- [x] 10. 사람인 크롤러

  **What to do**:
  - TDD: HTML fixture로 파서 테스트 먼저
  - 사람인 검색 결과 페이지 크롤링
  - 채용공고 파싱 (title, company, location, salary, url, posted_at)
  - 셀렉터 분리 (변경 대응 용이하게)

  **Must NOT do**:
  - 상세 페이지 크롤링 (목록만)
  - 로그인 필요 콘텐츠

  **Parallelizable**: YES (10, 11, 12 병렬 가능)

  **References**:
  - `AGENTS.md` - Selectors, Rate Limiting

  **Acceptance Criteria**:
  - [ ] `tests/fixtures/saramin.html` 존재
  - [ ] `pytest tests/test_saramin.py` 통과
  - [ ] 파싱 결과에 필수 필드 존재

  **Commit**: YES
  - Message: `feat(backend): 사람인 크롤러`
  - Files: `backend/jdcrawler/crawlers/saramin.py`, `backend/tests/test_saramin.py`, `backend/tests/fixtures/saramin.html`

---

- [x] 11. 잡코리아 크롤러

  **What to do**:
  - TDD: HTML fixture로 파서 테스트 먼저
  - 잡코리아 검색 결과 페이지 크롤링
  - 채용공고 파싱
  - 셀렉터 분리

  **Must NOT do**:
  - 상세 페이지 크롤링

  **Parallelizable**: YES (10, 11, 12 병렬 가능)

  **References**:
  - 사람인 크롤러 패턴 참고

  **Acceptance Criteria**:
  - [ ] `tests/fixtures/jobkorea.html` 존재
  - [ ] `pytest tests/test_jobkorea.py` 통과

  **Commit**: YES
  - Message: `feat(backend): 잡코리아 크롤러`
  - Files: `backend/jdcrawler/crawlers/jobkorea.py`, `backend/tests/test_jobkorea.py`, `backend/tests/fixtures/jobkorea.html`

---

- [x] 12. 원티드 크롤러

  **What to do**:
  - TDD: HTML fixture로 파서 테스트 먼저
  - 원티드 검색 결과 페이지 크롤링
  - 채용공고 파싱
  - 셀렉터 분리

  **Must NOT do**:
  - 상세 페이지 크롤링

  **Parallelizable**: YES (10, 11, 12 병렬 가능)

  **References**:
  - 사람인 크롤러 패턴 참고

  **Acceptance Criteria**:
  - [ ] `tests/fixtures/wanted.html` 존재
  - [ ] `pytest tests/test_wanted.py` 통과

  **Commit**: YES
  - Message: `feat(backend): 원티드 크롤러`
  - Files: `backend/jdcrawler/crawlers/wanted.py`, `backend/tests/test_wanted.py`, `backend/tests/fixtures/wanted.html`

---

### Phase 4: 프론트엔드

- [x] 13. API 클라이언트 및 타입 정의

  **What to do**:
  - TypeScript 타입 정의 (Job, Keyword, etc.)
  - Fetch 기반 API 클라이언트
  - React Query 설정 (캐싱, 상태 관리)

  **Must NOT do**:
  - 컴포넌트 구현

  **Parallelizable**: NO (3번 이후)

  **References**:
  - Backend Pydantic 모델과 타입 일치

  **Acceptance Criteria**:
  - [ ] `frontend/src/lib/api.ts` 존재
  - [ ] `frontend/src/types/index.ts` 존재
  - [ ] TypeScript 컴파일 에러 없음

  **Commit**: YES
  - Message: `feat(frontend): API 클라이언트 및 타입 정의`
  - Files: `frontend/src/lib/`, `frontend/src/types/`

---

- [x] 14. 레이아웃 및 네비게이션

  **What to do**:
  - 기본 레이아웃 컴포넌트 (Header, Sidebar, Main)
  - React Router 설정
  - 네비게이션 메뉴 (대시보드, 공고 목록, 키워드 설정)
  - 새 공고 뱃지 표시

  **Must NOT do**:
  - 페이지 내용 구현

  **Parallelizable**: NO (13번 이후)

  **References**:
  - shadcn/ui 컴포넌트

  **Acceptance Criteria**:
  - [ ] 3개 라우트 네비게이션 동작
  - [ ] 새 공고 뱃지 표시 (API 연동)
  - [ ] 반응형 레이아웃

  **Commit**: YES
  - Message: `feat(frontend): 레이아웃 및 네비게이션`
  - Files: `frontend/src/components/layout/`, `frontend/src/App.tsx`

---

- [x] 15. 대시보드 페이지 (통계/차트)

  **What to do**:
  - 사이트별 수집 현황 차트 (Recharts)
  - 최근 수집 공고 요약
  - 키워드별 공고 수 차트

  **Must NOT do**:
  - 상세 분석 기능

  **Parallelizable**: YES (15, 16, 17 병렬 가능)

  **References**:
  - Recharts 공식 문서

  **Acceptance Criteria**:
  - [ ] 사이트별 파이/바 차트 표시
  - [ ] 데이터 로딩 상태 표시
  - [ ] 빈 데이터 처리

  **Commit**: YES
  - Message: `feat(frontend): 대시보드 페이지`
  - Files: `frontend/src/pages/Dashboard.tsx`

---

- [x] 16. 채용공고 목록 페이지

  **What to do**:
  - 공고 테이블 (shadcn/ui DataTable)
  - 검색 입력
  - 사이트/날짜 필터
  - 정렬 (최신순, 회사명 등)
  - 페이지네이션
  - 북마크 버튼
  - 수동 크롤링 버튼

  **Must NOT do**:
  - 인라인 편집

  **Parallelizable**: YES (15, 16, 17 병렬 가능)

  **References**:
  - shadcn/ui DataTable

  **Acceptance Criteria**:
  - [ ] 검색 동작
  - [ ] 필터 동작
  - [ ] 북마크 토글 동작
  - [ ] 크롤링 버튼 → API 호출

  **Commit**: YES
  - Message: `feat(frontend): 채용공고 목록 페이지`
  - Files: `frontend/src/pages/Jobs.tsx`, `frontend/src/components/jobs/`

---

- [x] 17. 키워드 설정 페이지

  **What to do**:
  - 키워드 목록 표시
  - 키워드 추가 폼
  - 키워드 삭제 버튼
  - 활성/비활성 토글

  **Must NOT do**:
  - 복잡한 키워드 조합 로직

  **Parallelizable**: YES (15, 16, 17 병렬 가능)

  **References**:
  - shadcn/ui Form, Input, Button

  **Acceptance Criteria**:
  - [ ] 키워드 추가 동작
  - [ ] 키워드 삭제 동작
  - [ ] 목록 실시간 갱신

  **Commit**: YES
  - Message: `feat(frontend): 키워드 설정 페이지`
  - Files: `frontend/src/pages/Keywords.tsx`

---

- [x] 18. 공고 상세 모달/페이지

  **What to do**:
  - 공고 상세 정보 표시
  - 원문 링크 버튼
  - 북마크 버튼
  - 키워드 하이라이팅 (선택)

  **Must NOT do**:
  - 공고 원문 임베딩 (링크만)

  **Parallelizable**: NO (16번 이후)

  **References**:
  - shadcn/ui Dialog

  **Acceptance Criteria**:
  - [ ] 상세 정보 표시
  - [ ] 원문 링크 새 탭 열기
  - [ ] 북마크 토글 동작

  **Commit**: YES
  - Message: `feat(frontend): 공고 상세 모달`
  - Files: `frontend/src/components/jobs/JobDetail.tsx`

---

### Phase 5: 통합

- [x] 19. 크롤링 실행 API 및 스케줄러

  **What to do**:
  - `POST /api/crawl` - 수동 크롤링 실행
  - `GET /api/crawl/status` - 크롤링 상태 조회
  - APScheduler 또는 간단한 cron 설정
  - 중복 체크 로직 (URL 기반)

  **Must NOT do**:
  - 복잡한 큐 시스템

  **Parallelizable**: NO (12번 이후)

  **References**:
  - APScheduler 문서

  **Acceptance Criteria**:
  - [ ] 수동 크롤링 API 동작
  - [ ] 중복 공고 필터링
  - [ ] 스케줄러 설정 가능

  **Commit**: YES
  - Message: `feat(backend): 크롤링 실행 API 및 스케줄러`
  - Files: `backend/jdcrawler/api/crawl.py`, `backend/jdcrawler/scheduler.py`

---

- [x] 20. 키워드 분석 API

  **What to do**:
  - `GET /api/analysis/tech-stacks` - 기술 스택 빈도 분석
  - 공고 제목/설명에서 키워드 추출
  - 간단한 정규식 기반 분석

  **Must NOT do**:
  - LLM 기반 분석 (나중에 확장)
  - NLP 라이브러리 사용

  **Parallelizable**: NO (7번 이후)

  **References**:
  - Draft - LLM 확장 가능하게 설계

  **Acceptance Criteria**:
  - [ ] 기술 스택 빈도 반환 (Python: 50, React: 30 등)
  - [ ] 빈 데이터 처리

  **Commit**: YES
  - Message: `feat(backend): 키워드 분석 API`
  - Files: `backend/jdcrawler/api/analysis.py`, `backend/tests/test_analysis.py`

---

- [x] 21. End-to-End 테스트 및 문서화

  **What to do**:
  - E2E 테스트 (실제 크롤링 → DB → API → 확인)
  - README.md 완성 (설치, 실행, 사용법)
  - API 문서 자동 생성 확인 (FastAPI /docs)

  **Must NOT do**:
  - 배포 문서

  **Parallelizable**: NO (모든 기능 완료 후)

  **References**:
  - 전체 프로젝트

  **Acceptance Criteria**:
  - [ ] E2E 테스트 통과
  - [ ] README에 Quick Start 포함
  - [ ] `/docs`에서 API 문서 확인

  **Commit**: YES
  - Message: `docs: README 및 E2E 테스트 완성`
  - Files: `README.md`, `backend/tests/test_e2e.py`

---

## Commit Strategy

| After Task | Message | Files |
|------------|---------|-------|
| 1 | `chore: 모노레포 초기 구조 설정` | 루트 설정 파일 |
| 2 | `chore(backend): 개발 환경 설정` | backend 설정 |
| 3 | `chore(frontend): 개발 환경 설정` | frontend 설정 |
| 4-8 | `feat(backend): ...` | 백엔드 기능 |
| 9-12 | `feat(backend): ...` | 크롤러 |
| 13-18 | `feat(frontend): ...` | 프론트엔드 |
| 19-21 | `feat/docs: ...` | 통합/문서 |

---

## Success Criteria

### Verification Commands
```bash
# Backend
cd backend
pip install -e ".[dev]"
ruff check .
pyright
pytest

# Frontend
cd frontend
pnpm install
pnpm lint
pnpm build

# E2E
cd backend
python -m jdcrawler  # 크롤링 실행
pytest tests/test_e2e.py
```

### Final Checklist
- [ ] 3개 사이트 크롤링 동작
- [ ] 대시보드 모든 페이지 동작
- [ ] 북마크/검색/필터 동작
- [ ] 새 공고 뱃지 동작
- [ ] 전체 테스트 통과
- [ ] 린트 에러 없음
- [ ] README 완성
