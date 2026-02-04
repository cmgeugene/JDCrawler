# JDCrawler (Job Description Crawler)

한국 주요 채용 사이트(Jobkorea, Saramin, Wanted)의 채용 공고를 수집하고, AI를 활용하여 사용자 맞춤형으로 분석해주는 통합 대시보드 애플리케이션입니다.

## 🚀 Key Features

### 1. Multi-Site Crawling
- **지원 사이트**: 잡코리아, 사람인, 원티드
- **스마트 수집**: Playwright를 활용한 동적 페이지 크롤링 및 로봇 탐지 우회
- **중복 제거**: RapidFuzz를 이용한 유사 공고 필터링 및 통합

### 2. AI-Powered Analysis
- **자동 분석**: 수집된 공고를 AI가 자동으로 분석하여 요약 및 평가
- **맞춤형 점수**: 사용자 프로필(기술 스택, 제외 키워드 등) 기반 적합도 점수 산출
- **스킬 매칭**: 공고 내 요구 스킬과 사용자 보유 스킬 매칭 시각화

### 3. Modern Dashboard
- **통합 뷰**: 모든 사이트의 공고를 한곳에서 검색 및 필터링
- **데이터 시각화**: 일별 수집 현황, 사이트별 분포, 포지션 분석 차트 제공
- **키워드 관리**: 수집 대상 키워드 및 활성/비활성 상태 관리

## 🛠 Tech Stack

### Backend
- **Framework**: Python 3.11+, FastAPI
- **Crawling**: Playwright, BeautifulSoup4
- **Database**: SQLite (SQLAlchemy + Pydantic)
- **Task Queue**: APScheduler (Periodic Crawling)
- **AI/ML**: RapidFuzz (Duplicate Detection)

### Frontend
- **Framework**: React 19, Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4, shadcn/ui
- **State Management**: React Query (@tanstack/react-query)
- **Visualization**: Recharts

## 🏁 Quick Start

### Prerequisites
- Python 3.11 or higher
- Node.js 18 or higher
- pnpm (recommended) or npm

### 1. Clone Repository
```bash
git clone https://github.com/cmgeugene/JDCrawler.git
cd JDCrawler
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"
playwright install chromium

# Environment Setup
cp .env.example .env
# Edit .env with your API keys (ZHIPU_API_KEY etc.)

# Run Server
./run_backend.sh
# Or manually: uvicorn jdcrawler.main:app --reload
```

### 4. Docker Deployment (Recommended for Production)

도커를 이용하면 복잡한 설치 과정 없이 백엔드와 프론트엔드를 한 번에 실행할 수 있습니다.

```bash
# 1. 환경 변수 설정
cp .env.example .env
# .env 파일을 열어 ZHIPU_API_KEY 등을 실제 키로 수정하세요.

# 2. 서비스 실행
docker-compose up -d --build
```
실행 후 브라우저에서 `http://localhost`에 접속하세요.

## 📁 Project Structure

```
JDCrawler/
├── backend/
│   ├── jdcrawler/
│   │   ├── api/          # FastAPI endpoints (jobs, crawl, keywords, etc.)
│   │   ├── crawlers/     # Site-specific crawler implementations
│   │   ├── db/           # Database schema, client, and migrations
│   │   ├── models/       # Pydantic data models for API & internal use
│   │   ├── services/     # Business logic (crawler orchestration, AI analysis)
│   │   └── utils/        # Shared utilities (rate limiting, retries)
│   └── tests/            # Unit, integration, and E2E tests
├── frontend/
│   ├── src/
│   │   ├── components/   # UI components (jobs, layout, common ui)
│   │   ├── lib/          # API client (Axios) and utility functions
│   │   ├── pages/        # Main route pages (Dashboard, Jobs, etc.)
│   │   ├── queries/      # React Query hooks for data fetching
│   │   └── types/        # TypeScript interfaces and types
│   └── ...
└── ...
```

## 📝 License

This project is licensed under the MIT License.