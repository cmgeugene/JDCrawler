# JDCrawler Frontend

JDCrawler의 프론트엔드 애플리케이션입니다. React 19와 Vite를 사용하여 빠르고 현대적인 사용자 경험을 제공합니다.

## 📦 Project Structure

```
src/
├── components/
│   ├── jobs/           # 공고 관련 컴포넌트 (목록, 카드, 상세 뷰)
│   ├── layout/         # 레이아웃 컴포넌트 (헤더, 사이드바)
│   └── ui/             # shadcn/ui 기반 공통 UI 컴포넌트
├── lib/
│   ├── api.ts          # Axios 인스턴스 및 API 호출 함수
│   └── utils.ts        # 유틸리티 함수 (cn 등)
├── pages/              # 라우트 페이지 (Dashboard, Jobs, Keywords 등)
├── queries/            # React Query 훅 (데이터 페칭 로직 분리)
└── types/              # TypeScript 타입 정의
```

## 🚀 Scripts

- `pnpm dev`: 개발 서버 실행 (HMR 지원)
- `pnpm build`: 프로덕션 빌드
- `pnpm preview`: 빌드된 결과물 미리보기
- `pnpm lint`: ESLint 코드 검사
- `pnpm test`: Vitest 단위 테스트 실행

## 🎨 UI & Styling

- **Tailwind CSS v4**: 유틸리티 퍼스트 스타일링
- **shadcn/ui**: 재사용 가능한 컴포넌트 라이브러리 (Radix UI 기반)
- **Lucide React**: 아이콘 라이브러리
- **Recharts**: 데이터 시각화 차트

## 🧩 State Management

- **React Query (@tanstack/react-query)**: 서버 상태 관리, 캐싱, 동기화
- **React Router DOM**: 클라이언트 사이드 라우팅

## 🔗 Environment Variables

루트의 `.env` 파일을 참고하거나, 필요한 경우 `.env.local`을 생성하여 설정을 덮어쓸 수 있습니다.

```env
VITE_API_URL="http://localhost:8000"  # 백엔드 API 주소
```