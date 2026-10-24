# AgentLab

> LLM 에이전트를 실행하고, 기록하고, 비교·평가하는 테스트베드

현재 상태: **0단계 - 개발 환경 구성**

## 주요 기능 (계획)

- **에이전트 관리**: 시스템 프롬프트, 모델, 사용할 도구 조합을 저장하고 관리
- **도구 레지스트리**: Python 함수를 LLM이 호출할 수 있는 도구로 등록
- **실행 트레이스**: LLM과 도구 사이의 호출 과정을 단계별로 실시간 확인 (SSE)
- **평가(Eval)**: 같은 테스트 세트로 여러 에이전트·모델을 돌려 성공률, 지연, 비용 비교
- **프로바이더 추상화**: Mock / Ollama / Claude / OpenAI를 설정만으로 교체

## 기술 스택

| 영역 | 기술 |
|---|---|
| Frontend | React 19, TypeScript, Vite |
| Backend | Python 3.12, FastAPI, Pydantic |
| DB | SQLite → PostgreSQL (예정) |
| Tooling | uv, pytest, Ruff, Oxlint, Git / GitHub |

## 아키텍처

```text
[React + TS (Vite)]  ──REST / SSE──▶  [FastAPI]
                                         ├─ Agent Runner (LLM ↔ 도구 반복 루프)
                                         │    ├─ LLM Provider: Mock | Ollama | Claude | OpenAI
                                         │    └─ Tools: 계산기, SQL 조회, 웹검색 등
                                         └─ SQLAlchemy ──▶ [PostgreSQL]
```

## 로컬에서 실행하기

필요한 도구: Python 3.12+, [uv](https://docs.astral.sh/uv/), Node.js 22+

### 백엔드

```bash
cd backend
uv sync
uv run fastapi dev app/main.py
```

- API: http://localhost:8000
- API 문서(Swagger): http://localhost:8000/docs

### 프론트엔드

```bash
cd frontend
npm install
npm run dev
```

- 화면: http://localhost:5173

### 테스트

```bash
cd backend
uv run pytest
```

## 로드맵

- [x] 0. 개발 환경 + GitHub 레포
- [ ] 1. FastAPI 헬스체크 + 에이전트 CRUD (SQLite)
- [ ] 2. PostgreSQL + 마이그레이션(Alembic) + 테스트
- [ ] 3. React 화면: 에이전트 목록 / 생성
- [ ] 4. Mock LLM + 도구 + 에이전트 실행 루프
- [ ] 5. 실제 LLM 연결 + 실시간 트레이스 UI
- [ ] 6. 평가(Eval) 러너 + 대시보드
- [ ] 7. Docker Compose, GitHub Actions CI
