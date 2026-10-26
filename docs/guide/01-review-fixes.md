# 1단계 리뷰 반영: 버그 2개 고치기

리뷰에서 찾은 버그 2개를 고쳐요. 둘 다 **수정(PATCH) API**에서 500 에러가 나는 문제예요.

> 500은 "서버가 잘못했어요"라는 뜻이에요. 사용자가 잘못된 요청을 보냈다면 400번대 코드를 줘야 해요.
> 500이 난다는 건 서버 코드에 구멍이 있다는 신호라서, merge 전에 고치는 게 좋아요.

| 버그 | 지금 | 고친 후 |
|---|---|---|
| 리뷰 1: 이미 있는 이름으로 수정 | 500 | **409** Conflict |
| 리뷰 2: 꼭 있어야 하는 필드에 null을 보냄 | 500 | **422** Unprocessable Entity |

이번에도 순서는 **테스트 먼저 → 실패 확인(빨강) → 고치기 → 통과 확인(초록)**이에요.

## 시작하기 전에

- 빈칸 채우기 방법은 [1단계 가이드](01-agent-crud-api.md) 5번의 "시작하기 전에"와 같아요.
  주석 풀기(`Ctrl+/`) → `____` 채우기 → 저장(`Ctrl+S`)
- 코드 파일에서 `[리뷰 1-1]`처럼 번호가 붙은 안내 줄을 찾으면 돼요. `Ctrl+F`로 `[리뷰`를 검색하면 빨라요.
- 이번엔 **줄 지우기**도 있어요. 지울 줄에 커서를 두고 `Ctrl+Shift+K`를 누르면 한 줄이 통째로 지워져요.
  여러 줄은 마우스로 선택한 다음 누르면 돼요.
- 테스트는 터미널에서 `cd backend` 후 `uv run pytest`로 돌려요.

---

## 리뷰 1: 이미 있는 이름으로 바꾸면 500 → 409

### 무엇이 문제인가요?

`alpha`, `beta` 두 에이전트가 있을 때 `beta`의 이름을 `alpha`로 바꾸면(PATCH) 500 에러가 나요.

과제 5에서 `create_agent`에는 `try/except`를 넣었지만, `update_agent`의 `session.commit()`은 그대로예요.
그래서 이름이 겹칠 때 나는 예외(`IntegrityError`)를 아무도 처리하지 않아요.

### 어떻게 고치나요?

같은 `try/except`를 두 번 쓰는 대신, **함수 하나로 뽑아서** 두 곳에서 같이 써요.
Java에서 중복 코드를 private 메서드로 빼는 것과 같아요.

```text
지금                                     고친 후

create_agent ── try/except               create_agent ──┐
update_agent ── commit() (보호 없음)                     ├──▶ _commit_or_conflict
                                         update_agent ──┘     (try/except는 여기 한 곳)
```

### 1-1. 테스트 먼저 쓰기

**파일**: `backend/tests/test_agents.py` (맨 아래)

**할 일**: `[리뷰 1-1]` 블록 7줄의 주석을 풀고, 빈칸 2개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `json={"name": ____}` | `beta`의 이름을 무엇으로 바꿔야 "중복"이 될까요? 문자열이라 따옴표(`"`)도 같이 써요. |
| `== ____` | "이미 있어요"를 뜻하는 상태 코드예요. 과제 5와 같아요. |

**확인**: `uv run pytest` → 방금 쓴 테스트가 **실패**해요. 출력에서 이 줄을 찾아보세요.

```text
E   sqlalchemy.exc.IntegrityError: (sqlite3.IntegrityError) UNIQUE constraint failed: agents.name
```

과제 5-2에서 본 것과 같은 예외예요. 이번엔 만들 때가 아니라 **수정할 때** 나는 거예요.

<details>
<summary>정답 보기</summary>

```python
def test_update_agent_duplicate_name(client: TestClient) -> None:
    create(client, "alpha")
    beta = create(client, "beta")

    response = client.patch(f"/api/agents/{beta['id']}", json={"name": "alpha"})

    assert response.status_code == 409
```

</details>

### 1-2. 공통 함수 만들기

**파일**: `backend/app/services/agent_service.py` (맨 아래)

**할 일**: `[리뷰 1-2]` 블록 8줄의 주석을 풀고, 빈칸 3개를 채워요.

블록 맨 위 두 줄은 `# # ...`처럼 `#`가 두 개예요. 주석을 풀어도 `# `가 하나 남아서 설명 주석이 돼요. 정상이에요.

| 빈칸 | 힌트 |
|---|---|
| `except ____ as e:` | 1-1에서 본 예외 이름이에요. |
| `session.____()` | `commit`의 반대예요. 실패한 작업을 되돌려요. |
| `{____}` | 어떤 이름이 겹쳤는지 메시지에 넣어요. 이 함수가 받는 매개변수의 **이름**이에요. `name: str`에서 앞의 `name`이 변수 이름이고 뒤의 `str`은 타입이에요 (Java의 `String name`). |

**이 코드가 하는 일**

- `_commit_or_conflict`는 저장(commit)을 시도하고, 이름이 겹쳐서 실패하면 되돌린 다음 `ConflictError`(409)를 던져요.
- 이름 앞의 `_`는 "이 파일 안에서만 쓰는 함수"라는 Python의 약속이에요.
  Java의 `private`처럼 강제로 막지는 않지만, 다른 파일에서 쓰지 말라는 표시예요.
- 파일 맨 아래에 있어도 괜찮아요. Python은 함수를 **부르는 순간** 이름을 찾기 때문에, 위에 있는 함수에서 불러도 돼요.

**확인**: 아직 아무도 이 함수를 부르지 않아서, 테스트 결과는 1-1과 같아요(1개 실패).

<details>
<summary>정답 보기</summary>

```python
# create_agent와 update_agent가 같이 써요. 이름이 겹쳐 저장에 실패하면 409로 바꿔요.
# 이름 앞의 _는 "이 파일 안에서만 쓰는 함수"라는 약속이에요 (Java의 private).
def _commit_or_conflict(session: Session, name: str) -> None:
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()  # 실패한 작업을 되돌려요.
        raise ConflictError(f"Agent name already exists: {name}") from e
```

</details>

### 1-3. create_agent에서 공통 함수 쓰기

**파일**: `backend/app/services/agent_service.py`의 `create_agent` 함수

**할 일**

1. `[리뷰 1-3]` 안내 줄 아래 주석 1줄을 풀고, 빈칸 1개를 채워요.
2. 그 밑의 `try:`부터 `raise ...`까지 **5줄을 지워요.** 이제 공통 함수가 같은 일을 해 줘요.

| 빈칸 | 힌트 |
|---|---|
| `_commit_or_conflict(session, ____)` | 새로 만들 에이전트의 이름이에요. `create_agent`가 받은 `data` 안에 들어 있어요. |

```text
    session.add(agent)

    _commit_or_conflict(session, ____)       ← 주석을 푼 줄 (빈칸 채우기)
    try:                                     ┐
        session.commit()                     │
    except IntegrityError as e:              │  이 5줄을 지워요
        session.rollback()  # ...            │
        raise ConflictError(...) from e      ┘
    session.refresh(agent)
```

**확인**: `uv run pytest` → 여전히 **1개 실패**(1-1 테스트)예요.
그런데 과제 5의 `test_create_agent_duplicate_name`은 **계속 통과**해요.

> 코드 구조를 바꿨는데 기존 테스트가 그대로 통과한다는 건 "동작은 그대로"라는 증거예요.
> 이렇게 동작은 두고 구조만 바꾸는 걸 **리팩터링**이라고 해요. 테스트를 미리 써 두면 안심하고 고칠 수 있어요.

<details>
<summary>정답 보기</summary>

```python
def create_agent(session: Session, data: AgentCreate) -> Agent:
    agent = Agent(**data.model_dump())
    session.add(agent)

    _commit_or_conflict(session, data.name)
    session.refresh(agent)  # DB가 채운 id, created_at 등을 다시 읽어와요.
    return agent
```

`data.name` 대신 `agent.name`을 써도 정답이에요. 바로 위에서 `data`의 값을 `agent`에 복사했으니 둘은 같은 값이에요.
`update_agent`(1-4)와 모양이 똑같아지는 장점도 있어요.

</details>

### 1-4. update_agent에서 공통 함수 쓰기

**파일**: `backend/app/services/agent_service.py`의 `update_agent` 함수

**할 일**

1. `[리뷰 1-4]` 안내 줄 아래 주석 1줄을 풀고, 빈칸 1개를 채워요.
2. 그 밑의 `session.commit()  # PA의 ...` **1줄을 지워요.**
   린트 경고가 났던 그 긴 줄이라, 지우면 경고도 같이 사라져요.

| 빈칸 | 힌트 |
|---|---|
| `_commit_or_conflict(session, ____)` | 바꾸려는 새 이름이에요. 바로 위 `for` 문에서 `agent`의 값이 이미 바뀌었으니, `agent` 안에 있어요. |

**확인**

1. `uv run pytest` → **17 passed**
2. `uv run ruff check .` → `All checks passed!`

<details>
<summary>정답 보기</summary>

```python
def update_agent(session: Session, agent_id: int, data: AgentUpdate) -> Agent:
    agent = get_agent(session, agent_id)  # 없는 id면 여기서 NotFoundError가 나요.
    changes = data.model_dump(exclude_unset=True)  # 요청에 들어온 필드만 꺼내요.
    for field, value in changes.items():
        setattr(agent, field, value)  # agent.<field> = value 와 같아요.
    _commit_or_conflict(session, agent.name)
    session.refresh(agent)
    return agent
```

</details>

**커밋**: `fix: 에이전트 수정 시 이름 중복이면 409 반환`

---

## 리뷰 2: 꼭 있어야 하는 필드에 null을 보내면 500 → 422

### 무엇이 문제인가요?

PATCH 본문에 `{"name": null}`을 보내면 500이 나요. `model`, `system_prompt`, `temperature`도 마찬가지예요.

`AgentUpdate`의 필드가 `str | None`이라서 null이 검증을 통과하고, DB에 저장할 때 NOT NULL 규칙에 걸려서 터져요.
`str | None`은 원래 "**안 보내도 된다**"를 표현하려던 건데, "**null을 보내도 된다**"까지 허용해 버린 거예요.

| 요청 본문 | 뜻 | 원하는 결과 |
|---|---|---|
| `{}` | 아무것도 안 바꿔요 | 200 |
| `{"name": "new"}` | 이름을 바꿔요 | 200 |
| `{"name": null}` | 이름을 없애요? | **422** (이름은 꼭 있어야 해요) |
| `{"description": null}` | 설명을 지워요 | 200 (설명은 비워도 돼요) |

### 어떻게 고치나요?

잘못된 요청은 **입구에서** 막는 게 좋아요. 요청이 들어오면 스키마(`AgentUpdate`)가 제일 먼저 검사하니까, 거기서 null을 거절해요.

```text
요청 ──▶ [스키마 검사] ──▶ 서비스 ──▶ DB
          여기서 막아요 (422)          지금은 여기까지 가서 터져요 (500)
```

### 2-1. 테스트 먼저 쓰기

**파일**: `backend/tests/test_agents.py` (맨 아래)

**할 일**: `[리뷰 2-1]` 블록 15줄의 주석을 풀고, 빈칸 2개를 채워요. 테스트 두 개가 한꺼번에 생겨요.

| 빈칸 | 힌트 |
|---|---|
| `json={"name": ____}` | JSON의 `null`을 Python으로 쓰면 무엇일까요? 대문자로 시작해요. |
| `== ____` | 요청 형식이 잘못됐을 때 FastAPI가 주는 상태 코드예요. temperature에 1.5를 보냈을 때와 같아요. |

두 번째 테스트(`test_update_agent_can_clear_description`)는 빈칸이 없어요. "설명은 null로 지울 수 있다"는 걸 확인해요.
고치다가 이 동작까지 막아 버리지 않도록 지켜 주는 테스트예요.

<details>
<summary>정답 보기</summary>

```python
def test_update_agent_rejects_null_for_required_field(client: TestClient) -> None:
    agent = create(client, "beta")

    response = client.patch(f"/api/agents/{agent['id']}", json={"name": None})

    assert response.status_code == 422
```

</details>

### 2-2. 실패 확인하기 (빨강)

`uv run pytest` → 1개 실패. 이번엔 이런 줄이 보여요.

```text
E       assert 409 == 422
```

**왜 409일까요?** 리뷰 1에서 `IntegrityError`가 나면 409로 바꾸게 했죠.
그런데 `IntegrityError`는 **이름 중복(UNIQUE)**뿐 아니라 **NOT NULL 위반**에도 나요.
그래서 null을 보냈는데 "이름이 이미 있어요"라는 엉뚱한 409가 나온 거예요.

그래서 null은 DB까지 보내지 말고, 입구(스키마)에서 먼저 막아야 해요.

### 2-3. 스키마에 검증 추가하기 (초록)

**파일**: `backend/app/schemas/agent.py`

**할 일**

1. 위쪽 `[리뷰 2-3]` 아래 import 1줄의 주석을 풀어요.
2. `AgentUpdate` 클래스 안의 `[리뷰 2-3]` 블록 7줄의 주석을 풀고, 빈칸 2개를 채워요.

| 빈칸 | 힌트 |
|---|---|
| `if value is ____:` | null인지 확인해요. 2-1의 첫 번째 빈칸과 같은 값이에요. Python에서 null 비교는 `==`가 아니라 `is`로 해요. |
| `raise ____("null is not allowed")` | "값이 잘못됐어요"를 뜻하는 Python 기본 예외예요. Java의 `IllegalArgumentException`에 해당해요. |

**이 코드가 하는 일**

- `@field_validator("name", "model", "system_prompt", "temperature")`: 이 네 필드에 값이 들어오면 아래 함수로 한 번 더 검사해요.
  Spring의 커스텀 Bean Validation(`ConstraintValidator`)과 비슷해요.
- 검사 함수에서 `ValueError`를 던지면 Pydantic이 422 응답으로 바꿔줘요.
- `description`은 목록에 없어요. DB에서도 NULL을 허용하는 칸이라 null로 지울 수 있어야 하니까요.
- 필드를 **안 보내면** 이 검사는 실행되지 않아요. 그래서 "안 보내기"는 여전히 괜찮아요.
- `@classmethod`는 Pydantic 검사 함수의 정해진 형식이에요. 객체가 아니라 클래스에 붙는 함수라서
  (Java의 `static`과 비슷해요) 첫 인자가 `self` 대신 `cls`예요.

**확인**

1. `uv run pytest` → **19 passed**
2. /docs에서 PATCH 본문을 `{"name": null}`로 보내면 → 422, `detail`에 `null is not allowed`

<details>
<summary>정답 보기</summary>

```python
class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    model: str | None = Field(default=None, max_length=100)
    system_prompt: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=1.0)

    # 안 보내는 건 괜찮지만, DB에서 NOT NULL인 필드에 null을 보내면 422로 막아요.
    @field_validator("name", "model", "system_prompt", "temperature")
    @classmethod
    def reject_null(cls, value: object) -> object:
        if value is None:
            raise ValueError("null is not allowed")
        return value
```

파일 맨 위 import는 저장 후 이렇게 정리돼요.

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator
```

</details>

**커밋**: `fix: 에이전트 수정 시 필수 필드 null 거부`

---

## 리뷰 3 (선택): 주석 위치 정리

`backend/app/api/agents.py`의 `delete_agent`는 함수 줄 끝에 긴 주석이 붙어 있어서,
저장할 때 자동 정리가 함수 선언을 세 줄로 쪼갰어요. 설명 주석은 코드 **위 줄**에 쓰는 게 읽기 좋아요.

**지금**

```python
@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(
    agent_id: int, session: SessionDep
) -> None:  # 돌려줄 본문이 없으니 반환 타입이 `-> None`이에요. Java의 `void`예요.
    agent_service.delete_agent(session, agent_id)
```

**바꾼 후**

```python
# 돌려줄 본문이 없으니 반환 타입이 `-> None`이에요. Java의 `void`예요.
@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: int, session: SessionDep) -> None:
    agent_service.delete_agent(session, agent_id)
```

**커밋**: `style: 삭제 API 주석 위치 정리`

---

## 다 끝났으면

- [ ] `uv run pytest` → 19 passed
- [ ] `uv run ruff check .` → All checks passed!
- [ ] 코드에 `[리뷰`와 `____`가 남아 있지 않아요 (`Ctrl+Shift+F`로 폴더 전체 검색)
- [ ] 리뷰마다 커밋했어요

그다음 [1단계 가이드](01-agent-crud-api.md)의 **6번 "PR 만들고 merge하기"**로 가서 push → PR → merge를 해요.
