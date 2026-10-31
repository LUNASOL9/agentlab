# 2단계 (전반): Alembic으로 DB 마이그레이션

**이번 단계 목표**

- 테이블을 `create_all` 대신 **마이그레이션**으로 만들고 바꾼다
- 모델을 고치면 마이그레이션 파일을 자동으로 만들고(autogenerate) DB에 적용한다
- 데이터가 이미 있는 테이블에 새 컬럼을 안전하게 추가한다
- 이번에도 브랜치 → PR → 리뷰 → merge

예상 시간: 하루 1~2시간 기준 3~4일

PostgreSQL(Docker)은 2단계 후반에 해요. Alembic은 지금 쓰는 SQLite로도 똑같이 연습할 수 있어요.

---

## 0. 왜 마이그레이션이 필요할까요?

1단계에서는 서버가 켜질 때 `create_all`로 테이블을 만들었어요. 그런데 `create_all`은 **없는 테이블만** 만들어요.
이미 있는 테이블에 컬럼을 추가해도 반영이 안 돼서, 1단계 가이드에서는 "agentlab.db를 지우고 다시 시작하세요"라고 했었죠.

연습용 DB는 지워도 되지만, 실제 서비스 DB는 데이터를 지울 수 없어요.
그래서 "DB를 어떻게 바꿨는지"를 파일로 차곡차곡 남기고, 순서대로 적용해요. 이게 **마이그레이션**이에요.

### Git과 비교하면 쉬워요

Git이 **코드**의 변경을 커밋으로 쌓아 두듯이, Alembic은 **DB 구조**의 변경을 마이그레이션 파일로 쌓아 둬요.

| 하는 일 | Git (코드의 변경 이력) | Alembic (DB 구조의 변경 이력) |
|---|---|---|
| 변경 하나를 기록한 것 | 커밋 | 마이그레이션 파일 (`alembic/versions/xxxx.py`) |
| 변경 기록 만들기 | `git commit` | `uv run alembic revision --autogenerate` |
| 이력 보기 | `git log --oneline` | `uv run alembic history` |
| 지금 어디까지 왔는지 | 맨 위 커밋 (`HEAD`) | `uv run alembic current` (책갈피) |
| 최신까지 맞추기 | `git pull` | `uv run alembic upgrade head` |
| 한 단계 되돌리기 | 이전 커밋 상태로 되돌리기 | `uv run alembic downgrade -1` |

다른 점이 하나 있어요. Git 커밋에는 내가 바꾼 코드가 들어가지만, Alembic은 **모델과 DB를 비교해서 바뀐 점을 찾아 기록을 대신 써 줘요** (`--autogenerate`).

### 모델, 마이그레이션 파일, DB의 관계

```text
 [모델]                          [마이그레이션 파일]                  [DB]
 app/models/agent.py   ──①──▶   alembic/versions/xxxx.py   ──②──▶   agentlab.db
 "테이블은 이렇게 생겨야 해"       "DB를 이렇게 바꿔라" (명령 목록)      실제 테이블
 (설계도)                         (공사 지시서)                        (건물)
```

- **①** `uv run alembic revision --autogenerate`: 모델과 지금 DB를 비교해서, 다른 점을 "바꿔라" 명령으로 적은 파일을 만들어요. (1-3에서 해요)
- **②** `uv run alembic upgrade head`: 그 파일에 적힌 명령을 DB에 실행해요. (1-4에서 해요)

마이그레이션 파일은 `backend/alembic/versions/` 폴더에 생겨요. **지금은 비어 있고, 1-3에서 첫 파일이 생겨요.**

②를 할 때 Alembic은 모델을 다시 보지 않고, **파일에 적힌 대로만** DB를 바꿔요.
그래서 모델을 고칠 때마다 ①로 새 파일을 만들어야 해요. 이걸 잊으면 1-1의 검사 테스트가 실패해서 알려줘요.

---

## 1. 제가 미리 해 둔 것

- 브랜치 `feat/alembic-migrations`를 만들었어요. 지금 이 브랜치에 있어요 (`git branch`로 확인).
- `uv add alembic`으로 Alembic을 설치했어요.
- `uv run alembic init alembic`으로 기본 파일을 만들었어요.
- 설정 몇 가지, 빈칸 템플릿, 마이그레이션 검사 테스트를 넣었어요.

```text
backend/
├── alembic.ini                # Alembic 설정 (DB 주소, 로그 등)
├── alembic/
│   ├── env.py                 # Alembic이 실행될 때 읽는 파일. 앱 설정·모델과 연결해요 (빈칸 있음)
│   ├── script.py.mako         # 마이그레이션 파일을 만들 때 쓰는 틀
│   ├── README
│   └── versions/              # 마이그레이션 파일이 쌓이는 곳 (지금은 비어 있어요)
└── tests/test_migrations.py   # 마이그레이션이 모델과 맞는지 검사하는 테스트
```

**설정에서 바꾼 것**

- `alembic.ini`의 `sqlalchemy.url`을 비워 뒀어요. DB 주소는 `env.py`가 앱 설정(`app/config.py`)에서 가져와요.
  주소를 한 곳에서만 관리하려는 거예요.
- `pyproject.toml`
  - `extend-exclude = ["alembic/versions"]`: Alembic이 자동으로 만드는 파일은 ruff 검사에서 빼요.
  - `known-third-party = ["alembic"]`: `backend/alembic` 폴더 이름 때문에 ruff가 alembic 라이브러리를 우리 코드로 착각하지 않게 해요.

> **주의**: `alembic.ini`에는 **한글을 쓰지 마세요.** 한국어 Windows에서는 Alembic이 이 파일을 읽다가
> `UnicodeDecodeError`로 멈춰요. 제가 처음에 한글 주석을 넣었다가 직접 확인하고 영어로 바꿨어요.

**지금 상태**: `uv run pytest`를 돌리면 **2개 실패**(마이그레이션 테스트)가 정상이에요. 1-2와 1-3을 하면 통과해요.
`uv run ruff check .`도 `env.py`의 `target_metadata` 경고 2개가 나오는데, 1-2를 하면 사라져요.

**명령은 모두 `backend` 폴더에서** 실행해요.

```powershell
cd backend
```

### 빈칸 채우기 방법 (1단계와 같아요)

- `Ctrl+F`로 `[2단계 1-2]`처럼 번호가 붙은 안내 줄을 찾아요.
- 주석 풀기는 `Ctrl+/`, 줄 지우기는 `Ctrl+Shift+K`, 저장은 `Ctrl+S`예요.
- 막히면 단계 맨 아래 **정답 보기**를 눌러요.

---

## 전반: Alembic 연결하기

### 1-1. 마이그레이션 검사 테스트 이해하기 (빈칸 없음)

**파일**: `backend/tests/test_migrations.py`

파일을 열면 **모든 줄에 설명 주석**이 달려 있어요. 위에서부터 천천히 읽어 보세요.

#### 쉽게 말하면

이 테스트는 이런 순서로 일해요.

```text
① 빈 임시 DB를 하나 만들어요. (개발용 DB인 agentlab.db는 건드리지 않아요)
② 그 DB에 마이그레이션 파일들을 처음부터 끝까지 실행해요.   ← 터미널의 alembic upgrade head
③ 그렇게 만들어진 DB와 모델(app/models)을 비교해요.          ← 터미널의 alembic check
④ 둘이 다르면 실패해요. "모델은 바꿨는데 마이그레이션 파일을 안 만들었어요"라는 뜻이에요.
```

> **`upgrade head`가 뭐예요?**
> - DB 안에는 "마이그레이션 파일을 어디까지 실행했는지" 적어 두는 **책갈피**가 있어요 (`alembic_version` 테이블).
> - `upgrade`는 책갈피 다음부터, **아직 실행 안 한 파일을 순서대로** 실행해요.
> - `head`는 "가장 최신 파일까지"라는 뜻이에요.
> - 다 실행하면 책갈피를 최신 파일로 옮겨요. 그래서 두 번 실행해도 같은 파일이 또 실행되지는 않아요.
>
> 1-4에서 터미널로 직접 쳐 볼 거예요.

두 번째 테스트는 ②까지 한 다음 맨 처음 상태로 되돌렸다가(downgrade) 다시 실행해요. **되돌리기도 잘 되는지** 확인하는 거예요.

쉽게 말해, **설계도(모델)대로 DB가 만들어지는지** 확인하는 테스트예요.

#### 새로 나온 것

| 코드 | 뜻 |
|---|---|
| `Path(__file__).resolve().parents[1]` | 이 파일에서 두 단계 위 폴더(backend)예요. Java로는 `Paths.get(...).getParent().getParent()`예요. |
| `경로 / "alembic.ini"` | 그 폴더 안의 파일이에요. `Path`에서 `/`는 나누기가 아니에요. |
| `tmp_path` | pytest가 테스트마다 만들어 주는 빈 임시 폴더예요. |
| `command.upgrade(config, "head")` | 마이그레이션 파일을 끝까지 실행해요. 터미널의 `uv run alembic upgrade head`와 같아요. |
| `command.check(config)` | 모델과 DB가 같은지 검사해요. 터미널의 `uv run alembic check`와 같아요. |
| `command.downgrade(config, "base")` | 맨 처음 상태(테이블이 하나도 없는 상태)까지 되돌려요. |

#### 직접 돌려 보기

```powershell
uv run pytest tests/test_migrations.py
```

지금은 **2개 모두 실패**해요. 출력에서 이 줄을 찾아보세요.

```text
E   NameError: name 'target_metadata' is not defined
```

`env.py`의 빈칸(1-2)을 아직 안 채워서, Alembic이 모델 정보(`target_metadata`)를 모르는 거예요.
1-2와 1-3을 끝내면 이 두 테스트가 통과해요. 그게 전반부의 목표예요.

### 1-2. env.py를 앱과 연결하기

**파일**: `backend/alembic/env.py`

`env.py`는 대부분 Alembic이 만들어 준 기본 코드예요. 줄마다 설명 주석을 달아 뒀으니 한 번 읽어 보세요. 외울 필요는 없어요.

**할 일**

1. 위쪽 `[2단계 1-2]` 아래 4줄의 주석을 풀어요.
2. 가운데 `[2단계 1-2]` 블록 8줄의 주석을 풀고, 빈칸 2개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `config.set_main_option("sqlalchemy.url", ____)` | 앱이 쓰는 DB 주소예요. `app/config.py`의 `settings` 안에 있어요. |
| `target_metadata = ____` | 모든 모델(테이블) 정보를 모아 둔 곳이에요. 모델의 부모 클래스 `Base`(`app/db.py`)가 `metadata`라는 이름으로 갖고 있어요. |

**이 코드가 하는 일**

- `if not config.get_main_option(...)`: 테스트처럼 DB 주소를 따로 넣어 준 경우에는 그 주소를 쓰고, 아니면 앱 설정의 주소를 써요.
- `Base.metadata`: autogenerate는 이걸 실제 DB와 비교해서 "무엇이 달라졌는지" 찾아요.
- `from app import models` 줄이 꼭 있어야 해요. 모델을 import하지 않으면 `Base.metadata`가 비어 있어서 "테이블이 하나도 없다"고 생각해요.

**확인**: `uv run pytest` → 실패가 **1개**로 줄어요. 남은 실패 메시지는 이래요.

```text
AutogenerateDiffsDetected: New upgrade operations detected: [('add_table', Table('agents', ...
```

"모델에는 agents 테이블이 있는데, 마이그레이션에는 없어요"라는 뜻이에요. 1-3에서 해결해요.

<details>
<summary>정답 보기</summary>

위쪽 import 부분:

```python
# 모델을 import해야 Base에 테이블이 등록돼요.
from app import models  # noqa: F401
from app.config import settings
from app.db import Base
```

가운데 빈칸 부분:

```python
# DB 주소가 따로 정해지지 않았으면(테스트가 아닐 때) 앱 설정(.env)의 주소를 써요.
# get_main_option: alembic.ini에서 값을 읽어요. 비어 있으면 빈 문자열이 와요.
if not config.get_main_option("sqlalchemy.url"):
    # set_main_option: 설정 값을 넣어요. 여기서는 DB 주소를 넣어요.
    config.set_main_option("sqlalchemy.url", settings.database_url)

# autogenerate가 DB와 비교할 "모델 쪽 테이블 정보"예요.
target_metadata = Base.metadata
```

</details>

### 1-3. 첫 마이그레이션 자동으로 만들기

autogenerate는 **모델과 지금 DB를 비교**해요. 그런데 지금 개발용 DB(`agentlab.db`)에는 1단계 `create_all`이 만든 테이블이 이미 있어요.
그대로 비교하면 "달라진 게 없다"고 나와서 빈 파일이 만들어져요. 그래서 깨끗한 DB에서 시작할 거예요.

**할 일**

1. 서버가 켜져 있으면 `Ctrl+C`로 꺼요. 켜져 있으면 DB 파일이 잠겨서 지워지지 않아요.
2. 개발용 DB를 지워요. 1단계 연습 데이터라 지워도 괜찮아요.
   ```powershell
   Remove-Item agentlab.db
   ```
3. 마이그레이션 파일을 자동으로 만들어요.
   ```powershell
   uv run alembic revision --autogenerate -m "create agents table"
   ```
   `Detected added table 'agents'`가 보이고, `alembic/versions/`에 파일이 하나 생겨요.
   `-m` 뒤의 메시지는 파일 이름이 되니까 **영어**로 짧게 써요.
4. 생긴 파일을 열어서 읽어 보세요. `upgrade()`와 `downgrade()`가 각각 무엇을 하는지 찾아보세요.

<details>
<summary>정답 보기 (파일 내용 예시)</summary>

파일 이름 앞의 `072678c112e5` 같은 번호(Revision ID)는 만들 때마다 달라요.
아래 코드의 한국어 주석은 이해를 돕기 위해 제가 붙인 거예요. 실제로 생기는 파일에는 없어요.

```python
# upgrade head를 할 때 실행되는 부분이에요.
def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    # "agents 테이블을 만들어라" (SQL의 CREATE TABLE agents)
    op.create_table('agents',
    # ↓ 컬럼 하나하나예요. 모델의 필드와 한 줄씩 짝이 맞아요.
    sa.Column('id', sa.Integer(), nullable=False),                    # 정수, 비면 안 돼요
    sa.Column('name', sa.String(length=100), nullable=False),         # 최대 100글자, 비면 안 돼요
    sa.Column('description', sa.String(length=500), nullable=True),   # 최대 500글자, 비어도 돼요
    sa.Column('model', sa.String(length=100), nullable=False),
    sa.Column('system_prompt', sa.Text(), nullable=False),            # 길이 제한 없는 글자
    sa.Column('temperature', sa.Double(), nullable=False),            # 소수
    # 값을 안 넣으면 DB가 현재 시각(CURRENT_TIMESTAMP)을 넣어요.
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.PrimaryKeyConstraint('id'),   # id가 기본키(PK)
    sa.UniqueConstraint('name')      # name은 중복 금지(UNIQUE)
    )
    # ### end Alembic commands ###


# downgrade(되돌리기)를 할 때 실행되는 부분이에요. upgrade와 정반대 일을 해요.
def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    # "agents 테이블을 지워라" (SQL의 DROP TABLE agents)
    op.drop_table('agents')
    # ### end Alembic commands ###
```

**모델의 어느 줄이 어디로 갔나요?**

| 모델 (`app/models/agent.py`) | 마이그레이션 파일 |
|---|---|
| `id: Mapped[int] = mapped_column(primary_key=True)` | `sa.Column('id', sa.Integer(), ...)` + `PrimaryKeyConstraint('id')` |
| `name: Mapped[str] = mapped_column(String(100), unique=True)` | `sa.Column('name', sa.String(length=100), nullable=False)` + `UniqueConstraint('name')` |
| `description: Mapped[str \| None] = mapped_column(String(500))` | `sa.Column('description', sa.String(length=500), nullable=True)` |
| `temperature: Mapped[float]` | `sa.Column('temperature', sa.Double(), nullable=False)` |
| `created_at: ... server_default=func.now()` | `server_default=sa.text('(CURRENT_TIMESTAMP)')` |

`Mapped[str]`처럼 `| None`이 없으면 `nullable=False`(비면 안 됨), `Mapped[str | None]`처럼 있으면 `nullable=True`(비어도 됨)가 돼요.

</details>

> **데이터를 지울 수 없는 DB라면?** 이미 테이블이 있는 운영 DB에 Alembic을 처음 도입할 때는
> `alembic stamp head`를 써요. 실제로 아무것도 바꾸지 않고 "이 DB는 이미 최신 마이그레이션까지 적용됐다"고 기록만 해요.
> 이번엔 연습 DB라 지우고 새로 만들었어요.

### 1-4. 마이그레이션 적용하기

```powershell
uv run alembic upgrade head
```

- `head`는 "가장 최신 마이그레이션까지"라는 뜻이에요.
- `Running upgrade  -> 072678c112e5, create agents table` 같은 줄이 나오면 성공이에요.
- `agentlab.db`가 새로 생기고, 그 안에 `agents` 테이블과 `alembic_version` 테이블이 생겨요.

어디까지 적용됐는지 확인하는 명령이에요.

```powershell
uv run alembic current
```

```powershell
uv run alembic history
```

- `current`: 이 DB가 지금 어디까지 적용됐는지 보여줘요. `072678c112e5 (head)`처럼 나와요.
- `history`: 마이그레이션 목록을 보여줘요.

### 1-5. main.py에서 create_all 지우기

이제 테이블은 Alembic이 만들어요. 서버가 켜질 때 `create_all`을 부를 필요가 없어요.

**파일**: `backend/app/main.py`

**지울 것**

1. `from collections.abc import AsyncIterator`
2. `from contextlib import asynccontextmanager`
3. `# models를 import해야...` 주석과 `from app import models  # noqa: F401`
4. `from app.db import Base, engine`
5. `lifespan` 함수 전체 (위의 주석 2줄과 `@asynccontextmanager` 포함)
6. `FastAPI(...)` 괄호 안의 `, lifespan=lifespan`

> 서버가 켜질 때 자동으로 마이그레이션하게 만들 수도 있어요. 하지만 여기서는 `alembic upgrade head`를 직접 실행하는 방식을 써요.
> 서버를 켜는 것만으로 DB 구조가 바뀌는 일을 막을 수 있어서 많이 쓰는 방식이에요.

<details>
<summary>정답 보기 (바뀐 후 main.py 전체)</summary>

```python
from fastapi import FastAPI

from app.api import agents, health
from app.errors import register_error_handlers

# Spring Boot의 @SpringBootApplication처럼 애플리케이션의 진입점이에요.
# 테이블은 이제 Alembic이 만들어요 (uv run alembic upgrade head).
app = FastAPI(title="AgentLab API", version="0.1.0")
register_error_handlers(app)
app.include_router(agents.router)
app.include_router(health.router)


# @GetMapping("/")과 같아요. 반환한 dict는 자동으로 JSON 응답이 돼요.
@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, LUNA!"}
```

</details>

**확인**

1. `uv run pytest` → **26 passed** (마이그레이션 테스트 2개 포함)
2. `uv run alembic check` → `No new upgrade operations detected.` (모델과 DB가 같다는 뜻이에요)
3. 서버를 켜고(`uv run fastapi dev app/main.py`) /docs에서 **에이전트를 2개 만들어 두세요.** 후반에 "이미 있던 데이터"로 써요.

> 테스트(`conftest.py`)는 여전히 `create_all`로 메모리 DB를 만들어요. 그게 훨씬 빠르기 때문이에요.
> 마이그레이션이 모델과 맞는지는 `test_migrations.py`가 따로 검사하니까 괜찮아요.

**커밋**: `feat: Alembic 마이그레이션 도입`

---

## 후반: 컬럼 추가해 보기 (max_steps)

**목표**: 에이전트에 `max_steps`를 추가해요. LLM과 도구 사이를 최대 몇 번 오갈지 정하는 값이에요(기본 5, 1~20).
4단계 실행 루프에서 무한 반복을 막는 데 쓸 거예요.

실무에서 가장 흔한 마이그레이션이 "데이터가 이미 있는 테이블에 컬럼 추가"예요. 순서는 이래요.

```text
모델 고치기 → (테스트가 "마이그레이션 없음"을 알려줌) → 마이그레이션 자동 생성 → DB에 적용 → 스키마 → 테스트
```

### 2-1. 모델에 컬럼 추가하기

**파일**: `backend/app/models/agent.py`

**할 일**: `[2단계 2-1]` 블록 3줄의 주석을 풀고, 빈칸 1개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `server_default=____` | DB가 채울 기본값 5예요. **SQL에 그대로 들어가는 글자**라서 숫자가 아니라 문자열로 써요 (따옴표 포함). |

**왜 `server_default`인가요?**
1-5에서 만든 에이전트 2개에는 `max_steps` 값이 없어요. 그런데 NOT NULL 컬럼이라 값이 꼭 있어야 해요.
`server_default`는 DB에 "값이 없으면 5"라고 알려 줘서, **이미 있던 행에도 5가 채워져요.**
Python 쪽 기본값(`default=`)은 앞으로 새로 만드는 행에만 적용돼서 이 문제를 못 풀어요.

<details>
<summary>정답 보기</summary>

```python
    temperature: Mapped[float]
    # LLM과 도구 사이를 최대 몇 번 오갈지예요 (무한 반복 방지).
    # server_default는 DB가 채우는 기본값이라, 이미 있던 행에도 이 값이 들어가요.
    max_steps: Mapped[int] = mapped_column(server_default="5")
```

</details>

### 2-2. 실패 확인하기 (빨강)

1. `uv run pytest` → **1개 실패**. 메시지는 이래요.
   ```text
   AutogenerateDiffsDetected: New upgrade operations detected: [('add_column', None, 'agents', Column('max_steps', ...
   ```
   "모델에는 max_steps가 있는데 마이그레이션에는 없어요"라는 뜻이에요. 1-1의 검사 테스트가 빠뜨린 걸 잡아 준 거예요.
2. 서버가 켜져 있다면 /docs에서 목록 조회(`GET /api/agents`)를 해 보세요. **500**이 나요.
   모델은 `max_steps`를 읽으려는데 DB에는 아직 그 컬럼이 없어서예요.

### 2-3. 마이그레이션 만들고 적용하기

```powershell
uv run alembic revision --autogenerate -m "add max_steps to agents"
```

```powershell
uv run alembic upgrade head
```

새로 생긴 파일을 열어 보세요.

<details>
<summary>정답 보기 (파일 내용 예시)</summary>

```python
def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('agents', schema=None) as batch_op:
        batch_op.add_column(sa.Column('max_steps', sa.Integer(), server_default='5', nullable=False))

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('agents', schema=None) as batch_op:
        batch_op.drop_column('max_steps')

    # ### end Alembic commands ###
```

- `upgrade()`: 컬럼을 추가해요 (`ALTER TABLE ... ADD COLUMN`).
- `downgrade()`: 컬럼을 지워요.
- `batch_alter_table`은 `env.py`의 `render_as_batch=True` 때문에 생겨요. SQLite가 컬럼 변경을 바로 못 해서 쓰는 방식이에요.

</details>

**확인**

1. `uv run pytest` → **26 passed**
2. `uv run alembic history` → 마이그레이션이 2개 보여요.
3. /docs에서 `GET /api/agents` → 다시 200이에요. 아직 응답에 `max_steps`가 안 보이는데, 2-4에서 스키마에 추가하면 보여요.

### 2-4. 스키마에 추가하기

**파일**: `backend/app/schemas/agent.py`

**할 일**

1. `AgentBase` 안의 `[2단계 2-4]` 아래 1줄의 주석을 풀고, 빈칸 3개를 채워요.
2. `AgentUpdate` 안의 `[2단계 2-4]` 아래 1줄의 주석을 풀어요 (빈칸 없음).
3. `reject_null` 위의 `[2단계 2-4]`: 바로 아래 `@field_validator(...)` 줄을 **지우고**, 그 밑의 주석 줄을 풀어서 빈칸 1개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `default=____` | 기본값 5예요. 이번엔 Python 값이라 **숫자 그대로** 써요 (2-1과 달라요). |
| `ge=____` | 최솟값 1이에요. |
| `le=____` | 최댓값 20이에요. |
| `@field_validator(..., ____)` | null을 막을 필드를 하나 더 넣어요. 필드 이름을 문자열로 써요. |

> 2-1의 `server_default="5"`는 DB에 들어가는 SQL 글자라 문자열이고,
> 여기 `default=5`는 Python 값이라 숫자예요. 같은 5라도 쓰는 곳에 따라 모양이 달라요.

**확인**

1. `uv run pytest` → **26 passed**
2. /docs에서 `GET /api/agents` → 1-5에서 만든 에이전트에도 `"max_steps": 5`가 보여요. `server_default` 덕분이에요.

<details>
<summary>정답 보기</summary>

```python
class AgentBase(BaseModel):
    ...
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)
    max_steps: int = Field(default=5, ge=1, le=20)


class AgentUpdate(BaseModel):
    ...
    temperature: float | None = Field(default=None, ge=0.0, le=1.0)
    max_steps: int | None = Field(default=None, ge=1, le=20)

    # 안 보내는 건 괜찮지만, DB에서 NOT NULL인 필드에 null을 보내면 422로 막아요.
    # 이 필드들에 값이 들어오면 아래 함수로 한 번 더 검사해요.
    @field_validator("name", "model", "system_prompt", "temperature", "max_steps")
    @classmethod
    def reject_null(cls, value: object) -> object:
        ...
```

</details>

### 2-5. 테스트 추가하기

**파일**: `backend/tests/test_agents.py` (맨 아래)

**할 일**: `[2단계 2-5]` 블록 22줄의 주석을 풀고, 빈칸 3개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| 첫 번째 `["max_steps"] == ____` | 안 보냈을 때의 기본값이에요. |
| `status_code == ____` | 범위 밖의 값(0, 21)을 보냈을 때의 검증 실패 코드예요. |
| 세 번째 `["max_steps"] == ____` | PATCH로 보낸 값이에요. |

`for max_steps in [0, 21]:`는 Java의 `for (int maxSteps : List.of(0, 21))`와 같아요. 같은 검사를 값만 바꿔서 두 번 해요.

**확인**

1. `uv run pytest` → **29 passed**
2. `uv run ruff check .` → `All checks passed!`

<details>
<summary>정답 보기</summary>

```python
def test_create_agent_uses_default_max_steps(client: TestClient) -> None:
    response = client.post("/api/agents", json={"name": "steps"})

    assert response.status_code == 201
    assert response.json()["max_steps"] == 5


def test_create_agent_rejects_out_of_range_max_steps(client: TestClient) -> None:
    for max_steps in [0, 21]:  # Java의 for (int maxSteps : List.of(0, 21))
        # {**AGENT, ...}: AGENT 내용을 그대로 복사하고 max_steps만 바꾼 새 dict예요.
        response = client.post("/api/agents", json={**AGENT, "max_steps": max_steps})

        assert response.status_code == 422


def test_update_agent_changes_max_steps(client: TestClient) -> None:
    agent = create(client, "beta")

    response = client.patch(f"/api/agents/{agent['id']}", json={"max_steps": 10})

    assert response.status_code == 200
    assert response.json()["max_steps"] == 10
```

</details>

**커밋**: `feat: 에이전트 최대 스텝 수(max_steps) 추가`

### 2-6. (선택) 되돌리기 체험

```powershell
uv run alembic downgrade -1
```

`-1`은 "한 단계 뒤로"예요. `max_steps` 컬럼이 사라지고, 이 상태로 목록을 조회하면 2-2처럼 500이 나요.

```powershell
uv run alembic upgrade head
```

컬럼이 다시 생겨요. 그런데 downgrade 전에 PATCH로 `max_steps`를 10으로 바꿔 둔 에이전트가 있었다면,
다시 올렸을 때는 **5**로 돌아와 있어요. 컬럼을 지웠다가 새로 만들었기 때문이에요.

> downgrade는 **데이터도 같이 지워요.** 그래서 운영 DB에서는 아주 조심해서 써요.

---

## 3. README 업데이트

`README.md`를 이렇게 바꿔요.

1. 5번째 줄: `현재 상태: **2단계 진행 중** (Alembic 완료, PostgreSQL 예정)`
2. "로컬에서 실행하기 → 백엔드"의 명령을 이렇게 바꿔요. 서버를 켜기 전에 마이그레이션을 적용하는 줄이 추가됐어요.

   ```bash
   cd backend
   uv sync
   uv run alembic upgrade head
   uv run fastapi dev app/main.py
   ```

3. "테스트" 아래에 새 섹션을 추가해요.

   ````markdown
   ### DB 마이그레이션

   모델(`app/models`)을 바꾼 뒤에는 마이그레이션을 만들고 적용해요.

   ```bash
   cd backend
   uv run alembic revision --autogenerate -m "변경 내용을 영어로"
   uv run alembic upgrade head
   ```
   ````

**커밋**: `docs: README에 마이그레이션 실행 방법 추가`

---

## 4. PR 만들고 merge하기

1단계와 같아요. 이번엔 main에 템플릿이 있어서, PR 본문 칸에 **양식이 자동으로 채워져 나와요.**

1. `git push -u origin feat/alembic-migrations`
2. GitHub에서 PR을 만들어요. 제목은 `feat: Alembic 마이그레이션 도입 (2단계 전반)`이에요.
3. **merge하기 전에 저에게 리뷰를 요청하세요.**
4. 리뷰 반영 → **Create a merge commit** → 로컬 정리 (`git switch main`, `git pull`, `git branch -d feat/alembic-migrations`)

---

## 5. 자주 만나는 에러

| 증상 | 원인 | 해결 |
|---|---|---|
| `UnicodeDecodeError: 'cp949' codec can't decode ...` | `alembic.ini`에 한글이 들어갔어요 | `alembic.ini`에서 한글을 지워요 |
| `NameError: name 'target_metadata' is not defined` | `env.py`의 1-2 주석을 아직 안 풀었어요 | 1-2를 해요 |
| `Could not parse SQLAlchemy URL from string ''` | `env.py`에서 DB 주소를 넣는 부분(1-2)이 빠졌어요 | 1-2의 첫 번째 빈칸을 확인해요 |
| 만들어진 마이그레이션의 `upgrade()`가 `pass`뿐이에요 | 지금 DB가 이미 모델과 같아요 (예: 1-3에서 개발용 DB를 안 지웠어요) | `alembic/versions/`의 그 파일을 지우고, 개발용 DB를 지운 다음 다시 만들어요 |
| `table agents already exists` | `create_all`로 만든 테이블이 있는 DB에 upgrade했어요 | 개발용 DB를 지우고 다시 `upgrade head` |
| `agentlab.db`가 지워지지 않아요 (다른 프로세스가 사용 중) | 서버가 켜져 있어서 파일이 잠겼어요 | 서버를 `Ctrl+C`로 끄고 다시 지워요 |
| 목록 조회가 500이에요 | 모델은 바뀌었는데 DB에 적용을 안 했어요 | `uv run alembic upgrade head` |
| `Can't locate revision identified by '...'` | 마이그레이션 파일을 지웠는데 DB에는 기록이 남아 있어요 | 개발용 DB를 지우고 `upgrade head` |

## 6. 완료 체크리스트

- [ ] `uv run pytest` → 29 passed
- [ ] `uv run ruff check .` → All checks passed!
- [ ] `uv run alembic check` → No new upgrade operations detected.
- [ ] `uv run alembic history` → 마이그레이션 2개
- [ ] `[2단계` 안내 줄을 모두 지웠고, 그다음 `____`가 남아 있지 않아요 (`Ctrl+Shift+F`로 검색)
- [ ] 커밋 3개 정도 (Alembic 도입, max_steps, README)
- [ ] PR → 리뷰 → merge
