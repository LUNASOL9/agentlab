# agentlab 설치 가이드 (Windows / PowerShell)

LLM 에이전트 테스트베드(FastAPI + SQLAlchemy + Alembic 백엔드, React 19 + Vite 프런트엔드, PostgreSQL 18) 개발 환경을 이 PC(`C:\agentlab`) 기준으로 정리한 문서입니다.

- 작성일: 2026-11-14
- 대상 PC: Intel i5-14600KF / RAM 32GB / NVIDIA RTX 4060 Ti 8GB / Windows 11 Pro

## 1. 현재 설치 상태

| 항목 | 요구 버전 | 이 PC 상태 | 설치 방법 |
| --- | --- | --- | --- |
| Git for Windows | 최신 | 2.56.0 설치됨 | `winget install --id Git.Git -e --source winget` |
| Python | 3.12 이상 | 3.12.10 설치됨 | `winget install --id Python.Python.3.12 -e --source winget` |
| uv | 최신 | 0.13.8 설치됨 | `winget install --id astral-sh.uv -e --source winget` |
| Node.js | 22 이상 | 24.22.1 설치됨 | `winget install --id OpenJS.NodeJS.LTS -e --source winget --version 24.22.1` |
| **Docker Desktop** | 최신 | **미설치 — 직접 설치 필요 (2절)** | 2절 참고 |
| 백엔드 의존성 | `uv.lock` | `uv sync` 완료 (`backend\.venv`) | `uv sync` |
| 프런트엔드 의존성 | `package-lock.json` | `npm ci` 완료 | `npm.cmd ci` |
| VS Code 확장 | `.vscode/extensions.json` | 4개 모두 설치됨 | Python, Ruff, Oxc, Git Graph |

## 2. 직접 해야 할 것: Docker Desktop

PostgreSQL 18을 컨테이너로 띄우기 때문에 Docker Desktop이 필요합니다. 관리자 권한, WSL 2 설치, 재부팅, 약관 동의가 필요해서 자동으로 설치하지 않았습니다. 이 PC에는 WSL도 아직 설치되어 있지 않습니다.

1. **관리자 권한** PowerShell을 열고 WSL 2를 설치합니다.

   ```powershell
   wsl --install --no-distribution
   ```

2. PC를 **재부팅**합니다.
3. Docker Desktop을 설치합니다. 둘 중 하나를 고릅니다.
   - 관리자 PowerShell: `winget install --id Docker.DockerDesktop -e --source winget`
   - 또는 <https://www.docker.com/products/docker-desktop/> 에서 "Download for Windows – AMD64"를 받아 실행 (설치 옵션은 "Use WSL 2 instead of Hyper-V" 체크 유지)
4. 다시 로그인(또는 재부팅)한 뒤 시작 메뉴에서 Docker Desktop을 실행하고 서비스 약관에 동의합니다. 로그인은 건너뛰어도 됩니다.
5. 확인:

   ```powershell
   docker --version
   docker compose version
   ```

> BIOS에서 가상화(Intel VT-x)가 꺼져 있으면 Docker가 시작되지 않습니다. 작업 관리자 → 성능 → CPU의 "가상화: 사용"을 확인합니다.

## 3. 설치 확인

새 PowerShell 창에서:

```powershell
git --version
python --version
uv --version
node --version
npm.cmd --version
```

## 4. 실행

### DB (Docker Desktop 설치 후)

```powershell
cd C:\agentlab
docker compose up -d
docker compose ps
```

STATUS에 `(healthy)`가 보이면 준비된 것입니다. `compose.yaml`이 사용자/비밀번호/DB를 모두 `agentlab`으로 만들고, `docker/postgres-init/create-test-db.sql`이 테스트용 DB(`agentlab_test`)를 처음 한 번 만듭니다.

### 백엔드

```powershell
cd C:\agentlab\backend
uv sync
uv run alembic upgrade head
uv run fastapi dev app/main.py
```

- API: <http://localhost:8000>
- Swagger: <http://localhost:8000/docs>

### 프런트엔드

```powershell
cd C:\agentlab\frontend
npm.cmd ci
npm.cmd run dev
```

- 화면: <http://localhost:5173>

## 5. 환경 변수

`compose.yaml`을 그대로 쓰면 `.env`가 없어도 됩니다(기본값은 `backend/app/config.py`). 바꾸고 싶을 때만 `backend\.env.example`을 복사합니다.

```powershell
cd C:\agentlab\backend
Copy-Item .env.example .env
```

| 변수 | 기본값 |
| --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://agentlab:agentlab@127.0.0.1:5432/agentlab?connect_timeout=5` |
| `TEST_DATABASE_URL` | `postgresql+psycopg://agentlab:agentlab@127.0.0.1:5432/agentlab_test?connect_timeout=5` |

## 6. 테스트·검사·마이그레이션

```powershell
cd C:\agentlab
docker compose up -d

cd backend
uv run pytest
uv run ruff check .

cd ..\frontend
npm.cmd run lint
npm.cmd run build
```

마이그레이션 추가:

```powershell
cd C:\agentlab\backend
uv run alembic revision --autogenerate -m "<English description>"
uv run alembic upgrade head
```

이 PC에서 확인한 결과(2026-11-14): `uv run ruff check .` 통과, 프런트엔드 `npm run build` 성공. **`pytest`, `alembic upgrade head`, 서버 실행은 Docker(PostgreSQL)가 없어 아직 확인하지 못했습니다.** Docker Desktop 설치 후 4절과 6절을 순서대로 실행해 확인합니다.

## 7. Ollama (다음 단계 대비)

README의 계획에 LLM 프로바이더(Mock / Ollama / Claude / OpenAI)가 있지만 아직 구현 전이라 지금은 필요하지 않습니다. 이 PC에는 Ollama 0.40.16과 `qwen3:8b`(5.2GB, RTX 4060 Ti 8GB에서 100% GPU)가 이미 설치되어 있어, 구현 단계에서 `http://localhost:11434`로 바로 쓸 수 있습니다. Claude/OpenAI 프로바이더를 쓸 때는 각 서비스의 API 키를 직접 발급받아야 합니다.

## 8. 문제 해결

| 증상 | 확인할 것 |
| --- | --- |
| `uv`, `node`, `git`을 찾을 수 없음 | 터미널/VS Code를 완전히 종료하고 다시 실행 |
| `docker` 명령을 찾을 수 없음 | Docker Desktop 설치 후 다시 로그인 |
| `docker compose up`이 엔진 연결 오류 | Docker Desktop 앱이 실행 중인지 확인 |
| 백엔드가 DB 연결에서 5초 뒤 실패 | `docker compose ps`에서 `db`가 `(healthy)`인지 확인 |
| 5432 포트 충돌 | PC에 다른 PostgreSQL이 떠 있는지 확인 |
| conftest의 `AssertionError` | `.env`의 `TEST_DATABASE_URL`이 `_test`로 끝나는 DB인지 확인 |
| VS Code가 인터프리터를 못 찾음 | `uv sync` 후 `backend\.venv\Scripts\python.exe` 선택 |

더 자세한 단계별 설명은 `docs/guide/` 폴더의 문서를 참고합니다.
