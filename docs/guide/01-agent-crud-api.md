# 1단계: 에이전트 CRUD API

**이번 단계 목표**

- FastAPI 프로젝트를 Spring처럼 계층(Controller → Service → Entity)으로 나눠 이해한다
- SQLAlchemy로 DB에 저장하고 조회한다
- 미리 써 둔 테스트를 통과시키는 방식으로 구현한다 (TDD 맛보기)
- Git 브랜치 → Pull Request → merge 흐름을 경험한다

예상 시간: 하루 1~2시간 기준 4~6일

---

## 0. 이번 단계의 Git 흐름

지금 `feat/agent-crud` 브랜치에 있어요. `git branch`로 확인해 보세요. `*`가 붙은 게 현재 브랜치예요.
직접 만들 때는 `git switch -c feat/agent-crud`처럼 하면 돼요.

**브랜치**는 main을 건드리지 않고 작업하는 별도의 작업 공간이에요.
작업이 끝나면 Pull Request(PR)로 main에 합쳐요.

```text
main             ●───────────────────────────────●  (merge)
                  \                             /
feat/agent-crud    ●────●────●────●────●────●──●
                  뼈대  과제1 과제2 과제3 과제4 과제5 README
```

## 1. 실습 ① 뼈대 코드 커밋하기

제가 만든 파일들을 VS Code에서 먼저 둘러본 다음, 그대로 커밋해요.

```powershell
git status
git add -A
git commit -m "feat: 에이전트 생성·조회 API 뼈대 추가"
```

## 2. 구조 이해하기: Spring과 비교

| 파일 | 하는 일 | Spring에서는 |
|---|---|---|
| `app/main.py` | 앱 생성, 라우터 등록 | `@SpringBootApplication` |
| `app/config.py` | 설정값 읽기 | `application.yml` + `@ConfigurationProperties` |
| `app/db.py` | DB 연결, 세션 만들기 | `DataSource` + `EntityManager` |
| `app/models/agent.py` | 테이블과 클래스 매핑 | `@Entity` |
| `app/schemas/agent.py` | 요청·응답 형태와 검증 | DTO + Bean Validation |
| `app/services/agent_service.py` | 비즈니스 로직 | `@Service` |
| `app/api/agents.py` | URL과 함수 연결 | `@RestController` |
| `app/api/deps.py` | 주입할 의존성 정의 | 생성자 주입 / `@Autowired` |
| `app/errors.py` | 예외를 HTTP 응답으로 변환 | `@ControllerAdvice` |
| `tests/conftest.py` | 테스트 공통 준비 | `@SpringBootTest` + `@TestConfiguration` |

### 요청 하나가 처리되는 과정

```text
POST /api/agents   {"name": "math-tutor"}
  │
  ▼  api/agents.py  create_agent()
  │     - JSON을 AgentCreate로 변환·검증해요 (실패하면 422)
  │     - session은 Depends(get_session)으로 주입돼요
  ▼  services/agent_service.py  create_agent()
  │     - Agent 엔티티 생성 → session.add() → session.commit()
  ▼  DB (backend/agentlab.db)
  │
  ◀  Agent 엔티티 → AgentRead DTO로 변환 → JSON 응답 (201 Created)
```

### 트랜잭션은?

Spring의 `@Transactional`처럼 자동으로 커밋되지 않아요. 서비스 함수에서 `session.commit()`을 **직접** 불러요.
요청이 끝나면 `get_session()`의 `with` 블록이 세션을 닫아요. 커밋하지 않은 변경은 버려져요.

## 3. 직접 실행해 보기

```powershell
cd backend
uv run fastapi dev app/main.py
```

### /docs 화면(Swagger UI)이란?

FastAPI가 자동으로 만들어 주는 **API 테스트 화면**이에요. Postman 같은 도구를 따로 깔지 않아도,
브라우저에서 버튼만 눌러서 API를 호출해 볼 수 있어요. springdoc의 `swagger-ui.html`과 같은 거예요.
**서버가 켜져 있을 때만** 열려요.

```text
┌ AgentLab API ─────────────────────────────────────┐
│ agents                                             │
│ [POST] /api/agents              Create Agent       │ ← ① 줄을 클릭하면 펼쳐져요
│   Request body                     [Try it out]    │ ← ② 누르면 본문을 고칠 수 있어요
│   {                                                │
│     "name": "string",                              │ ← ③ "string"을 실제 값으로 바꿔요
│     ...                                            │
│   }                                                │
│   [              Execute              ]            │ ← ④ 누르면 서버로 전송돼요
│   Server response                                  │
│   Code 201   { "id": 1, "name": ... }              │ ← ⑤ 서버의 응답이에요
│ [GET]  /api/agents/{agent_id}   Get Agent          │
└────────────────────────────────────────────────────┘
```

### 따라 하기: 에이전트 만들기 (POST)

1. 브라우저 주소창에 http://localhost:8000/docs 를 입력해요.
2. 초록색 `POST /api/agents` 줄을 클릭해서 펼쳐요.
3. 오른쪽의 **Try it out** 버튼을 눌러요. 회색 예시 상자가 흰색 편집 상자로 바뀌어요.
4. 상자 안의 JSON을 고쳐요. 예를 들면:
   ```json
   {
     "name": "my-first-agent",
     "description": "처음 만든 에이전트",
     "model": "mock",
     "system_prompt": "You are a helpful assistant.",
     "temperature": 0.5
   }
   ```
5. 파란색 **Execute** 버튼을 눌러요.
6. 바로 아래 **Server response**에서 확인해요.
   - **Code 201**: Created, 즉 "새로 만들었어요"라는 뜻이에요.
   - 응답 본문에 보낸 값과 함께 DB가 붙여준 `id`, `created_at`이 들어 있어요.

### 따라 하기: 조회하기 (GET)

1. 파란색 `GET /api/agents/{agent_id}` 줄을 펼치고 **Try it out**을 눌러요.
2. `agent_id` 칸에 방금 받은 `id`를 넣고 **Execute**를 눌러요. **Code 200**과 저장된 내용이 와요.
3. 없는 id(예: 999)로도 해 보세요. **Code 404**와 `detail` 메시지가 와요.

### 일부러 틀려 보기

- `temperature`를 `1.5`로 바꿔서 POST → **422**. 응답의 `detail`에 어떤 필드가 왜 틀렸는지 나와요.
- 같은 `name`으로 두 번 POST → 지금은 **500**이에요. 과제 5에서 409로 고칠 거예요.

> 이 화면에서 하는 일은 테스트 코드의 `client.post("/api/agents", json=...)`와 똑같아요.
> 테스트는 이걸 자동으로, 매번 같은 방식으로 해 주는 거예요.

`backend/agentlab.db` 파일이 새로 생겨요. `.gitignore`에 있어서 커밋되지 않아요.
지우면 다음 실행 때 빈 DB로 다시 만들어져요.

## 4. Java 개발자를 위한 Python 문법 (이번 코드에 나온 것만)

| Python | Java | 메모 |
|---|---|---|
| `name: str` | `String name` | 타입이 이름 뒤에 와요 |
| `str \| None` | `@Nullable String` | `None`이 Java의 `null`이에요 |
| `def f(x: int) -> str:` | `String f(int x)` | 반환 타입은 `->` 뒤에 |
| `Agent(name="a")` | `new Agent("a")` | `new`가 없어요. 이름으로 인자를 넘길 수 있어요 |
| `class AgentCreate(AgentBase):` | `class AgentCreate extends AgentBase` | `pass`는 "내용 없음" 표시예요 |
| `f"id={agent_id}"` | `"id=" + agentId` | f-string |
| `with SessionLocal() as session:` | try-with-resources | 블록이 끝나면 자동으로 닫혀요 |
| `yield session` | (없음) | 값을 넘겨주고 멈췄다가, 요청이 끝나면 나머지(정리)를 실행해요 |
| `@router.get("/")` | `@GetMapping("/")` | 생김새는 어노테이션 같지만, 함수를 감싸는 함수(데코레이터)예요 |
| `Agent(**data.model_dump())` | 필드 하나하나 복사 | dict를 `키=값` 인자로 펼쳐서 넘겨요 |
| `[a.name for a in agents]` | `agents.stream().map(a -> a.name).toList()` | 리스트 컴프리헨션 |
| `try: ... except X as e:` | `try { } catch (X e) { }` | |
| `raise ConflictError("...") from e` | `throw new ConflictException("...", e)` | 원인 예외를 연결해요 |
| 들여쓰기 4칸 | `{ }` | 들여쓰기가 곧 블록이에요 |

---

## 5. 과제 (빈칸 채우기)

### 시작하기 전에: 빈칸 채우기 사용법

코드 파일 안에 `[과제 2-1]`처럼 번호가 붙은 **주석 블록**이 미리 들어 있어요. 단계마다 이렇게 하면 돼요.

1. **주석 풀기**: `[과제 …]` 안내 줄 **아래**에 있는 `#` 줄들을 마우스로 선택하고 `Ctrl+/`를 눌러요.
   줄 앞의 `# `가 한꺼번에 지워져요. 안내 줄(`# [과제 2-1] ...`)은 선택하지 말고, 다 끝나면 지워도 돼요.
2. **빈칸 채우기**: `____`(밑줄 4개)를 알맞은 코드로 바꿔요.
3. **저장**: `Ctrl+S`. 저장할 때 import 줄이 자동으로 정리돼요. 위치가 옮겨지거나 한 줄로 합쳐지는데, 정상이에요.
4. **확인**: 단계마다 적힌 방법으로 확인해요.
5. **막히면**: 단계 맨 아래 **정답 보기**를 눌러요. 정답을 보고 따라 쳐도 괜찮아요. 대신 설명은 꼭 읽어 보세요.

예를 들면 이렇게 바뀌어요.

```python
# [과제 2-1] 주석을 풀고 ____를 채워요.
# def list_agents(session: Session, offset: int, limit: int) -> list[Agent]:
#     stmt = select(____).order_by(____).offset(offset).limit(limit)
#     return list(session.scalars(stmt))
```

↓ 안내 줄 아래 3줄을 선택하고 `Ctrl+/`

```python
# [과제 2-1] 주석을 풀고 ____를 채워요.
def list_agents(session: Session, offset: int, limit: int) -> list[Agent]:
    stmt = select(____).order_by(____).offset(offset).limit(limit)
    return list(session.scalars(stmt))
```

↓ `____`를 채우면 끝이에요.

> **들여쓰기 주의**: Python은 들여쓰기(앞쪽 칸 수)가 곧 문법이에요.
> `Ctrl+/`로 풀면 칸 수가 그대로 유지되니, `#`를 손으로 지우는 것보다 안전해요.

> import 자동 정리는 VS Code의 **Ruff 확장**이 해 줘요. 설치가 안 돼 있으면 저장 후
> `uv run ruff check . --fix`를 실행하면 똑같이 정리돼요.

---

### 과제 1: 헬스체크 API (완료)

`GET /api/health`로 서버 상태를 확인하는 API예요. 이미 끝냈어요.

<details>
<summary>정답 보기</summary>

`backend/app/api/health.py` (기본):

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
```

보너스(DB 확인)까지 하면 함수가 이렇게 바뀌어요. 이때는 테스트의 기대값도
`{"status": "ok", "database": "ok"}`로 바꿔야 해요.

```python
from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import SessionDep

router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def health_check(session: SessionDep) -> dict[str, str]:
    session.execute(text("SELECT 1"))  # 에러 없이 실행되면 DB가 살아 있는 거예요.
    return {"status": "ok", "database": "ok"}
```

</details>

---

### 과제 2: 목록 조회

**목표**: `GET /api/agents`로 에이전트 목록을 받아요.
SQL로 치면 `SELECT * FROM agents ORDER BY id LIMIT 20 OFFSET 0`이에요.

#### 2-1. 서비스: DB에서 목록 꺼내기

**파일**: `backend/app/services/agent_service.py`

**할 일**

1. 위쪽 `[과제 2-1]` 아래 import 1줄의 주석을 풀어요.
2. 아래쪽 `[과제 2-1]` 블록 3줄의 주석을 풀어요.
3. 빈칸 2개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `select(____)` | 어떤 엔티티를 조회할지예요. JPQL `SELECT a FROM Agent a`에서 `Agent` 자리예요. |
| `.order_by(____)` | 무엇으로 정렬할지예요. "Agent의 id 컬럼"은 `클래스이름.컬럼이름`으로 써요. |

**이 코드가 하는 일**

- `select(...).order_by(...).offset(...).limit(...)`: 쿼리를 **만들기만** 해요. 아직 실행 전이에요.
  Querydsl처럼 메서드를 이어 붙여요.
- `session.scalars(stmt)`: 쿼리를 실행해서 엔티티를 꺼내요. `list(...)`로 감싸서 리스트로 만들어요.

**확인**: 저장했을 때 빨간 물결 밑줄이 없으면 돼요. 화면 확인은 다음 단계에서 해요.

<details>
<summary>정답 보기</summary>

```python
def list_agents(session: Session, offset: int, limit: int) -> list[Agent]:
    stmt = select(Agent).order_by(Agent.id).offset(offset).limit(limit)
    return list(session.scalars(stmt))
```

</details>

#### 2-2. 라우터: 주소와 연결하기

**파일**: `backend/app/api/agents.py`

**할 일**

1. 아래쪽 `[과제 2-2]` 블록 4줄의 주석을 풀어요.
2. 빈칸 1개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `agent_service.____(...)` | 2-1에서 만든 서비스 함수 이름이에요. |

**이 코드가 하는 일**

- `offset: int = 0, limit: int = 20`: 함수 인자에 기본값을 주면 **쿼리 파라미터**가 돼요.
  `@RequestParam(defaultValue = "0")`과 같아요. `/api/agents?offset=1&limit=2`처럼 받아요.
- `[AgentRead.model_validate(agent) for agent in agents]`: 엔티티 목록을 DTO 목록으로 바꿔요.
  Java로 쓰면 `agents.stream().map(AgentRead::from).toList()`예요.
- `-> list[AgentRead]`: `List<AgentRead>`를 돌려준다는 뜻이에요.

**확인**

1. 브라우저에서 http://localhost:8000/api/agents → 지금까지 만든 에이전트 목록이 보여요.
2. http://localhost:8000/api/agents?limit=1 → 1개만 보여요.
3. `tests/test_agents_todo.py`에서 `test_list_agents`, `test_list_agents_with_pagination`
   바로 위의 `@pytest.mark.skip(...)` 줄 2개를 지워요.
4. `uv run pytest` → 통과

<details>
<summary>정답 보기</summary>

```python
@router.get("")
def list_agents(session: SessionDep, offset: int = 0, limit: int = 20) -> list[AgentRead]:
    agents = agent_service.list_agents(session, offset, limit)
    return [AgentRead.model_validate(agent) for agent in agents]
```

</details>

#### 2-3. 검증 추가: 이상한 값 막기

지금은 `limit=1000000`도 그대로 받아서, 서버가 한 번에 너무 많이 읽을 수 있어요.
`limit`은 1~100, `offset`은 0 이상만 받도록 막아요.

**파일**: `backend/app/api/agents.py`

**할 일**

1. 위쪽 `[과제 2-3]` 아래 import 2줄의 주석을 풀어요.
2. 2-2에서 푼 `def list_agents(...)` **한 줄**을 지우고, 그 자리에 아래 코드를 넣어요. 빈칸은 2개예요.

```python
def list_agents(
    session: SessionDep,
    offset: Annotated[int, Query(ge=____)] = 0,
    limit: Annotated[int, Query(ge=1, le=____)] = 20,
) -> list[AgentRead]:
```

| 빈칸 | 힌트 |
|---|---|
| `ge=____` | ge는 greater or equal, 즉 "이상"이에요. offset의 최솟값을 넣어요. |
| `le=____` | le는 less or equal, 즉 "이하"예요. limit의 최댓값을 넣어요. |

**이 코드가 하는 일**: `Annotated[int, Query(ge=0)]`은 "int이고, 쿼리 파라미터이고, 0 이상"이라는 뜻이에요.
Spring의 `@RequestParam @Min(0) int offset`과 같아요.

**확인**

1. http://localhost:8000/api/agents?limit=1000 → 422와 함께 `detail`에 이유가 나와요.
2. `test_list_agents_rejects_too_large_limit` 위의 skip 줄을 지우고 `uv run pytest` → 통과

<details>
<summary>정답 보기</summary>

```python
@router.get("")
def list_agents(
    session: SessionDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[AgentRead]:
    agents = agent_service.list_agents(session, offset, limit)
    return [AgentRead.model_validate(agent) for agent in agents]
```

파일 맨 위 import는 저장 후 이렇게 정리돼요.

```python
from typing import Annotated

from fastapi import APIRouter, Query, status
```

</details>

**커밋**: `feat: 에이전트 목록 조회 API 추가`

---

### 과제 3: 부분 수정 (PATCH)

**목표**: `PATCH /api/agents/1`에 `{"name": "new-name"}`을 보내면 이름만 바뀌고 나머지는 그대로예요.

#### 3-1. 서비스: 보낸 필드만 바꾸기

**파일**: `backend/app/services/agent_service.py`

**할 일**

1. 위쪽 `[과제 3-1]` 아래 import 1줄의 주석을 풀어요.
2. 아래쪽 `[과제 3-1]` 블록 8줄의 주석을 풀어요.
3. 빈칸 2개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `agent = ____(session, agent_id)` | 같은 파일에 이미 있는, id로 하나를 찾는 함수예요. 없는 id면 알아서 404를 내줘요. |
| `session.____()` | 바꾼 내용을 DB에 확정하는 메서드예요. `create_agent`에서도 썼어요. |

**이 코드가 하는 일**

- `data.model_dump(exclude_unset=True)`: 요청 JSON에 **실제로 들어온** 필드만 dict로 꺼내요.
  `{"name": "after"}`만 보냈으면 `{"name": "after"}`만 나와요.
- `for field, value in changes.items():`: dict의 키와 값을 하나씩 꺼내요.
  Java의 `for (var e : map.entrySet())`와 같아요.
- `setattr(agent, field, value)`: `field`가 `"name"`이면 `agent.name = value`와 같아요.
- JPA의 변경 감지(dirty checking)처럼, 엔티티 값만 바꾸고 `commit()`하면 UPDATE가 실행돼요.

<details>
<summary>정답 보기</summary>

```python
def update_agent(session: Session, agent_id: int, data: AgentUpdate) -> Agent:
    agent = get_agent(session, agent_id)
    changes = data.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(agent, field, value)
    session.commit()
    session.refresh(agent)
    return agent
```

</details>

#### 3-2. 라우터: PATCH 주소 연결하기

**파일**: `backend/app/api/agents.py`

**할 일**

1. 위쪽 `[과제 3-2]` 아래 import 1줄의 주석을 풀어요.
2. 아래쪽 `[과제 3-2]` 블록 4줄의 주석을 풀어요.
3. 빈칸 2개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `@router.____(...)` | HTTP 메서드 이름을 소문자로 써요. 부분 수정은 어떤 메서드였죠? |
| `data: ____` | 요청 본문으로 받을 DTO예요. `schemas/agent.py`에 수정용으로 만들어 둔 클래스 이름이에요. |

**확인**

1. http://localhost:8000/docs 를 새로고침하면 `PATCH`가 생겨요.
2. **Try it out** → `agent_id`에 있는 id를 넣고, 본문을 `{"name": "renamed"}`로 바꿔서 **Execute** → 200
3. 과제 3 테스트 2개의 skip 줄을 지우고 `uv run pytest` → 통과

<details>
<summary>정답 보기</summary>

```python
@router.patch("/{agent_id}")
def update_agent(agent_id: int, data: AgentUpdate, session: SessionDep) -> AgentRead:
    agent = agent_service.update_agent(session, agent_id, data)
    return AgentRead.model_validate(agent)
```

</details>

**커밋**: `feat: 에이전트 수정 API 추가`

---

### 과제 4: 삭제

**목표**: `DELETE /api/agents/1` → 204 No Content. 성공했지만 돌려줄 본문은 없다는 뜻이에요.

#### 4-1. 서비스: 삭제하기

**파일**: `backend/app/services/agent_service.py`

**할 일**: 아래쪽 `[과제 4-1]` 블록 4줄의 주석을 풀고, 빈칸 1개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `session.____(agent)` | 엔티티를 삭제하는 메서드예요. JPA의 `em.remove(agent)`에 해당하고, 영어로 "삭제"예요. |

<details>
<summary>정답 보기</summary>

```python
def delete_agent(session: Session, agent_id: int) -> None:
    agent = get_agent(session, agent_id)
    session.delete(agent)
    session.commit()
```

</details>

#### 4-2. 라우터: DELETE 주소 연결하기

**파일**: `backend/app/api/agents.py`

**할 일**: 아래쪽 `[과제 4-2]` 블록 3줄의 주석을 풀고, 빈칸 2개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `status.____` | "204 No Content"를 뜻하는 상수예요. 위에 있는 `status.HTTP_201_CREATED`와 같은 모양이에요. |
| `agent_service.____(...)` | 4-1에서 만든 함수 이름이에요. |

**이 코드가 하는 일**: 돌려줄 본문이 없으니 반환 타입이 `-> None`이에요. Java의 `void`예요.

**확인**

1. /docs에서 `DELETE` → 있는 id로 **Execute** → 204
2. 같은 id로 `GET` → 404
3. 과제 4 테스트 2개의 skip 줄을 지우고 `uv run pytest` → 통과

<details>
<summary>정답 보기</summary>

```python
@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: int, session: SessionDep) -> None:
    agent_service.delete_agent(session, agent_id)
```

</details>

#### 4-3. 정리하기

skip 줄을 모두 지우면 `test_agents_todo.py` 맨 위의 `import pytest`를 쓰는 곳이 없어져요.
`uv run ruff check .`를 실행하면 이 줄을 지적해요. `uv run ruff check . --fix`로 자동으로 지울 수 있어요.

**커밋**: `feat: 에이전트 삭제 API 추가`

---

### 과제 5: 이름 중복이면 409 (테스트 먼저 쓰기)

지금 같은 이름으로 두 번 만들면 **500 Internal Server Error**가 나요.
DB의 UNIQUE 제약을 어겨서 예외가 났는데, 아무도 처리하지 않았기 때문이에요.
사용자에게는 "이미 있는 이름이에요"라는 뜻의 **409 Conflict**를 주는 게 맞아요.

이번에는 **테스트를 먼저** 쓰고, 실패하는 걸 확인한 다음 고쳐요. 이런 방식을 TDD라고 해요.

#### 5-1. 테스트 먼저 쓰기

**파일**: `backend/tests/test_agents.py` (맨 아래)

**할 일**: `[과제 5-1]` 블록 7줄의 주석을 풀고, 빈칸 2개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `json=____` | 첫 번째와 똑같은 내용을 보내야 해요. 파일 맨 위에 정의된 변수예요. |
| `== ____` | "이미 있어요"를 뜻하는 상태 코드예요. |

<details>
<summary>정답 보기</summary>

```python
def test_create_agent_duplicate_name(client: TestClient) -> None:
    first = client.post("/api/agents", json=AGENT)
    assert first.status_code == 201

    second = client.post("/api/agents", json=AGENT)

    assert second.status_code == 409
```

</details>

#### 5-2. 실패하는 걸 확인하기 (빨강)

`uv run pytest`를 실행하면 방금 쓴 테스트가 **실패**해요. 출력에서 `E`로 시작하는 이런 줄을 찾아보세요.

```text
E   sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: agents.name
```

이렇게 읽으면 돼요.

- `IntegrityError`라는 예외가 났어요. **이 이름을 기억해 두세요.** 5-3에서 이 예외를 잡을 거예요.
- 이유는 `UNIQUE constraint failed: agents.name`, 즉 agents 테이블 name 컬럼의 중복 금지 규칙을 어겼다는 거예요.

> 테스트에서는 서버 안에서 난 예외가 그대로 보여요. 브라우저(/docs)에서 같은 일을 하면 500으로 보여요.

#### 5-3. 고치기 (초록)

**파일**: `backend/app/services/agent_service.py`

**할 일**

1. 위쪽 `[과제 5-3]` 아래 import 2줄의 주석을 풀어요.
2. `create_agent` 함수 안에서 `[과제 5-3]` 안내 줄 **바로 위의 `session.commit()` 한 줄을 지워요.**
3. 안내 줄 아래 블록 5줄의 주석을 풀고, 빈칸 3개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `except ____ as e:` | 5-2에서 본 예외 이름이에요. |
| `session.____()` | `commit`의 반대예요. 실패한 작업을 되돌려요. |
| `raise ____(...)` | 409 응답으로 바꿔주는 우리 예외 클래스예요. `app/errors.py`에 있어요. |

**이 코드가 하는 일**

- `try:` / `except X as e:`는 Java의 `try { } catch (X e) { }`예요.
- `raise ConflictError(...) from e`는 `throw new ConflictException(msg, e)`처럼 원인 예외를 연결해서 던져요.
- `ConflictError`를 던지면 `errors.py`의 핸들러(`@ControllerAdvice` 역할)가 409 JSON 응답으로 바꿔줘요.

<details>
<summary>정답 보기</summary>

```python
def create_agent(session: Session, data: AgentCreate) -> Agent:
    agent = Agent(**data.model_dump())
    session.add(agent)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        raise ConflictError(f"Agent name already exists: {data.name}") from e
    session.refresh(agent)
    return agent
```

파일 맨 위 import는 저장 후 이렇게 정리돼요.

```python
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.models import Agent
from app.schemas.agent import AgentCreate, AgentUpdate
```

</details>

#### 5-4. 통과 확인하기

1. `uv run pytest` → 전부 통과, skipped 0개
2. /docs에서 같은 이름으로 두 번 POST → 두 번째는 409와 `{"detail": "Agent name already exists: ..."}`

**커밋**: `feat: 에이전트 이름 중복 시 409 반환`

---

### 생각해 볼 질문 (리뷰 때 같이 이야기해요)

- PUT과 PATCH는 어떻게 다를까요?
- PATCH에 `{"name": null}`을 보내면 어떻게 될까요?
- 저장하기 전에 SELECT로 같은 이름이 있는지 먼저 확인하는 방식과 비교하면 어떤 차이가 있을까요?
  (힌트: 요청 두 개가 동시에 들어오면?)

---

## 6. 실습 ② PR 만들고 merge하기

1. README 로드맵의 1단계를 `[x]`로 바꾸고 커밋해요: `docs: 1단계 완료 표시`
2. 브랜치를 GitHub에 올려요.
   ```powershell
   git push -u origin feat/agent-crud
   ```
3. GitHub 저장소 페이지에 뜨는 **Compare & pull request** 버튼을 눌러요.
   base는 `main`, compare는 `feat/agent-crud`인지 확인하세요.
4. 제목은 `feat: 에이전트 CRUD API (1단계)`예요. 본문은 템플릿이 자동으로 채워지니 빈칸을 작성해요.
5. **Files changed** 탭에서 직접 한 번 훑어보세요 (셀프 리뷰). 디버그용 print, 오타, 필요 없는 변경이 없는지 확인해요.
6. **merge하기 전에 저에게 알려주세요.** 실무 코드 리뷰처럼 리뷰해 드릴게요.
   고칠 게 있으면 같은 브랜치에 커밋하고 push하면 PR에 자동으로 반영돼요.
7. 리뷰가 끝나면 **Merge pull request** → **Create a merge commit**을 눌러요.
8. 로컬을 정리해요.
   ```powershell
   git switch main
   git pull
   git branch -d feat/agent-crud
   git log --oneline --graph
   ```
   Git Graph로 보면 브랜치가 갈라졌다가 합쳐진 모양이 보여요.

## 7. 자주 만나는 에러

| 증상 | 원인 | 해결 |
|---|---|---|
| `NameError: name '____' is not defined` | 빈칸(`____`)을 아직 안 채웠어요 | `Ctrl+F`로 `____`를 검색해서 남은 빈칸을 채워요 |
| `IndentationError` / `unexpected indent` | 들여쓰기 칸 수가 맞지 않아요 | 위아래 줄과 칸을 맞춰요. 주석은 `Ctrl+/`로 풀면 안전해요 |
| 저장했더니 import 줄 위치가 바뀌었어요 | 저장할 때 import 자동 정리가 동작했어요 | 정상이에요 |
| `ModuleNotFoundError: No module named 'app'` | `backend` 폴더 밖에서 실행했어요 | `cd backend` 후 다시 실행 |
| 422 Unprocessable Entity | 요청 본문이 스키마와 맞지 않아요 | 응답의 `detail`에 어떤 필드가 왜 틀렸는지 나와요 |
| 405 Method Not Allowed | 경로는 있는데 그 HTTP 메서드용 함수가 없어요 | 데코레이터(`@router.patch` 등) 확인 |
| 모델에 컬럼을 추가했는데 반영이 안 돼요 | `create_all`은 **없는 테이블만** 만들어요 | `agentlab.db`를 지우고 재시작 (2단계에서 Alembic으로 해결해요) |
| `database is locked` | 다른 프로그램이 DB 파일을 열고 있어요 | 그 프로그램을 닫아요 |

## 8. 완료 체크리스트

- [ ] 과제 1~5 구현, `uv run pytest` 전부 통과 (skipped 0개)
- [ ] `uv run ruff check .` 통과
- [ ] /docs에서 생성 → 목록 → 수정 → 삭제를 직접 해 봤다
- [ ] 과제마다 커밋했다 (뼈대 포함 8개 정도)
- [ ] PR을 만들고 리뷰를 받은 뒤 merge했다
- [ ] 로컬 main이 최신이고, 작업 브랜치는 지웠다
