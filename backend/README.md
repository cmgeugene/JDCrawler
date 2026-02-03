# JDCrawler Backend

JDCrawler의 백엔드 서비스입니다. FastAPI를 기반으로 구축되었으며, 채용 사이트 크롤링, 데이터 분석 및 REST API를 제공합니다.

## 🔧 Configuration (.env)

`backend/.env` 파일을 생성하여 다음 설정을 관리합니다.

```env
# Database
DATABASE_URL="sqlite:///./data/jobs.db"

# App Settings
HEADLESS=true           # 브라우저 헤드리스 모드 (False일 경우 브라우저 창이 보임)

# AI Settings (Zhipu AI)
ZHIPU_API_KEY="your-api-key"
RATE_LIMIT_DELAY="3.0"  # API 요청 간 딜레이 (초)
REQUESTS_PER_MINUTE="10"

# Logging
LOG_LEVEL="INFO"
```

## 🕷️ Crawlers

`jdcrawler/crawlers/` 디렉토리에 각 사이트별 크롤러가 구현되어 있습니다.

- **Jobkorea (`jobkorea.py`)**: 정적 파싱과 동적 로딩을 혼합하여 처리
- **Saramin (`saramin.py`)**: 네트워크 트래픽 분석을 통한 API 응답 활용 또는 HTML 파싱
- **Wanted (`wanted.py`)**: Next.js 기반 사이트 구조에 맞춰 데이터 추출

### Adding a New Crawler
1. `jdcrawler/crawlers/base.py`의 `BaseCrawler` 클래스를 상속받습니다.
2. `crawl()` 및 `extract_details()` 메서드를 구현합니다.
3. `jdcrawler/services/crawler.py`의 `crawlers` 딕셔너리에 등록합니다.

## 📡 API Endpoints

서버 실행 후 `http://localhost:8000/docs`에서 Swagger UI를 확인할 수 있습니다.

### Jobs
- `GET /api/jobs`: 채용 공고 목록 조회 (필터링, 페이지네이션)
- `GET /api/jobs/{job_id}`: 공고 상세 조회
- `GET /api/jobs/stats`: 공고 통계 데이터 조회

### Keywords
- `GET /api/keywords`: 등록된 검색 키워드 목록
- `POST /api/keywords`: 새 키워드 추가
- `PATCH /api/keywords/{keyword_id}`: 키워드 활성/비활성 토글

### Crawl
- `POST /api/crawl/trigger`: 즉시 크롤링 트리거
- `GET /api/crawl/status`: 현재 크롤링 상태 확인

## 🧪 Testing

```bash
# 전체 테스트 실행
pytest

# 특정 파일 테스트
pytest tests/test_saramin.py

# Lint & Format
ruff check .
ruff format .
```