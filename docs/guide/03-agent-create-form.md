# 3단계 (후반): 에이전트 만들기 폼

**이번 단계 목표**

- 화면에서 에이전트를 **만든다** (`POST /api/agents`)
- 서버가 보낸 에러(409, 422)를 사람이 읽을 수 있는 문구로 보여준다
- 만든 다음 목록을 다시 불러온다 (함수를 props로 넘기기)
- 이번에도 브랜치 → PR → 리뷰 → merge

예상 시간: 하루 1~2시간 기준 3~4일

> **이번엔 실습을 조금 늘렸어요.**
> 빈칸 17개에 더해, 몇 줄을 직접 쓰는 **"직접 써 보기"**가 3곳 있어요.
> 맨 뒤에는 원하면 해 보는 **"더 해 보기"** 3개도 넣었어요.

> 이번 내용도 빈칸을 처음부터 끝까지 채워 보고, 단계마다 빌드·린트·테스트 결과가 아래 적힌 대로 나오는지 확인했어요.
> 완성된 폼으로 만들기, 같은 이름(409), 빈 이름(422), 백엔드 꺼짐(502)까지 브라우저에서 직접 해 봤어요.
> 확인할 때는 테스트 DB를 써서, 개발 DB에는 아무것도 넣지 않았어요.

---

## 제가 미리 해 둔 것

- PR #5 merge 뒤의 main을 받아 와서, 브랜치 `feat/agent-create-form`을 만들었어요. 지금 이 브랜치에 있어요.
- `App.css`에 폼 스타일을 넣었어요.
- 빈칸 템플릿을 넣었어요. `[3단계 후반 1]`처럼 번호가 붙어 있어요.

```text
frontend/src/
├── types/agent.ts            # 보낼 값의 모양 (1번, 직접 써 보기)
├── utils/errors.test.ts      # 에러 문구 테스트 (2-1번)
├── utils/errors.ts           # 에러 문구 함수 (2-2번)
├── api/agents.ts             # 만들기 API 함수 (3번)
├── components/AgentForm.tsx  # 만들기 폼 (4번, 직접 써 보기 2곳)
├── components/AgentList.tsx  # 빈 목록 안내 문구 (5번)
└── App.tsx                   # 폼과 목록 연결 (5번)
```

**지금 상태**: `npm run build` 성공, `npm run lint` 통과, `npm test`는 아래처럼 나와요.

```text
 Test Files  1 passed | 1 skipped (2)
      Tests  2 passed (2)
```

`skipped` 1개는 `errors.test.ts`예요. 테스트를 쓰기 전이라 "나중에 써요"(`describe.todo`) 표시만 넣어 뒀어요.

> 전반에서 쓰던 로컬 브랜치 `feat/agent-list-ui`는 아직 남아 있어요. 이미 merge됐으니 지워도 돼요.
>
> ```powershell
> git branch -d feat/agent-list-ui
> ```

### 새로 해 보는 "직접 써 보기"

- `____` 한 칸이 아니라 **몇 줄**을 직접 써요. 바로 위에 비슷한 코드가 있어서, 보고 따라 쓰면 돼요.
- 다 쓰면 `[직접 써 보기 ...]` 안내 주석 줄도 지워요.
- 막히면 정답 보기를 눌러요. 정답과 글자 하나까지 같지 않아도, 빌드와 화면이 되면 괜찮아요.

### 이번에 만들 것

```text
[만들기 버튼]
   │ ① handleSubmit: 입력칸의 값으로 createAgent(...)를 불러요
   ▼
createAgent ── POST /api/agents (JSON) ──▶ FastAPI ──▶ PostgreSQL
   │
   ├─ ② 201 (성공) → onCreated() → App의 loadAgents() → 목록을 다시 불러와요
   └─ ③ 409, 422 (실패) → toErrorMessage(...)로 문구를 만들어 폼 아래에 보여줘요
```

---

## 1. 보낼 값의 모양 적기 (직접 써 보기)

**파일**: `frontend/src/types/agent.ts`

만들 때 보내는 값은 `Agent`에서 **서버가 정해 주는 값**(`id`, `created_at`, `updated_at`)을 뺀 모양이에요.
`backend/app/schemas/agent.py`의 `AgentCreate`와 짝이에요.

주석을 풀고, `____` 자리에 필드 6개를 직접 써요. 바로 위 `Agent`를 보고 쓰면 돼요.

<details>
<summary>정답 보기</summary>

```ts
export type AgentCreateInput = {
  name: string
  description: string | null
  model: string
  system_prompt: string
  temperature: number
  max_steps: number
}
```

</details>

**확인**: `npm run build` → 성공

---

## 2. 에러 문구 만들기 (테스트부터)

### 서버가 보내는 에러는 두 가지 모양이에요

```text
409 (이름이 겹칠 때, 1단계에서 우리가 만든 에러)
{ "detail": "Agent name already exists: alpha" }                    ← detail이 글자

422 (입력 검사에 걸렸을 때, Pydantic이 만든 에러)
{ "detail": [ { "loc": ["body", "name"],
                "msg": "String should have at least 1 character", ... } ] }   ← detail이 목록
```

화면에는 이렇게 보여 줄 거예요.

| 상태 | 화면에 보일 문구 |
|---|---|
| 409 | `Agent name already exists: alpha` (그대로) |
| 422 | `name: String should have at least 1 character` (`필드: 설명`) |
| 그 밖 (예: 백엔드가 꺼져서 502) | `요청이 실패했어요 (HTTP 502)` |

### 2-1. 테스트 먼저 쓰기

**파일**: `frontend/src/utils/errors.test.ts`

1. 위쪽(`[3단계 후반 2-1] 이 줄부터` ~ `여기까지 지워요.`)을 지워요. 자리 표시였어요.
2. 아래쪽 주석을 모두 풀고 `____` 두 군데를 채워요.

<details>
<summary>정답 보기</summary>

```ts
    expect(toErrorMessage(422, body)).toBe('name: String should have at least 1 character')
```

```ts
    expect(toErrorMessage(502, null)).toBe('요청이 실패했어요 (HTTP 502)')
```

</details>

```powershell
npm test
```

→ 아직 함수가 없어서 **3개 실패**가 정상이에요.

```text
TypeError: toErrorMessage is not a function
 Test Files  1 failed | 1 passed (2)
      Tests  3 failed | 2 passed (5)
```

(지금은 `npm run build`도 `error TS2305: Module '"./errors"' has no exported member 'toErrorMessage'`로 실패해요. 2-2를 하면 해결돼요.)

### 2-2. 함수 만들기

**파일**: `frontend/src/utils/errors.ts`

주석을 모두 풀고 `____` 세 군데를 채워요.

| 코드 | 뜻 |
|---|---|
| `type ErrorBody = { detail?: ... } \| null` | `detail?`: 있을 수도 없을 수도 있는 필드예요 |
| `body?.detail` | `body`가 `null`이면 에러 없이 `undefined`를 줘요 |
| `typeof detail === 'string'` | 값의 종류를 글자로 알려 줘요. 글자면 `'string'`이에요 |
| `Array.isArray(detail)` | 배열이면 `true`예요 |
| `issue.loc.at(-1)` | 배열의 마지막 값이에요 (Python의 `loc[-1]`) |
| `.map(...).join(', ')` | 문제마다 글자로 바꾸고, 쉼표로 이어 붙여요 (Java의 `Collectors.joining(", ")`) |

<details>
<summary>정답 보기</summary>

```ts
  if (typeof detail === 'string') {
```

```ts
  if (Array.isArray(detail)) {
```

```ts
    return detail.map((issue) => `${issue.loc.at(-1)}: ${issue.msg}`).join(', ')
```

</details>

```powershell
npm test
```

```text
 Test Files  2 passed (2)
      Tests  5 passed (5)
```

**커밋 1**: `feat: 에이전트 만들기 타입과 에러 문구 함수`

---

## 3. 만들기 API 함수

**파일**: `frontend/src/api/agents.ts`

`[3단계 후반 3]`이 두 군데예요.

1. 맨 위: 지금 있는 `import type { Agent } ...` 줄을 지우고, 그 밑의 주석 2줄을 풀어요.
2. 맨 아래: 주석을 풀고 `____` 네 군데를 채워요.

| 코드 | 뜻 |
|---|---|
| `fetch(주소, { method, headers, body })` | 두 번째 인자로 요청 방법을 정해요. 안 쓰면 `GET`이에요 |
| `'Content-Type': 'application/json'` | 본문이 JSON이라고 알려 줘요. 그래야 FastAPI가 JSON으로 읽어요 |
| `JSON.stringify(input)` | 객체를 JSON 글자로 바꿔요 (Jackson의 `writeValueAsString`) |
| `response.json().catch(() => null)` | 본문을 JSON으로 읽다가 실패하면(예: 502) 에러 대신 `null`을 줘요 |

<details>
<summary>정답 보기</summary>

```ts
import type { Agent, AgentCreateInput } from '../types/agent'
import { toErrorMessage } from '../utils/errors'
```

```ts
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
```

```ts
    throw new Error(toErrorMessage(response.status, body))
```

</details>

**확인**: `npm run build` → 성공

**커밋 2**: `feat: 에이전트 만들기 API 함수`

---

## 4. 만들기 폼 컴포넌트

**파일**: `frontend/src/components/AgentForm.tsx`

주석을 모두 풀고 `____` 다섯 군데를 채워요. 그리고 **직접 써 보기 2곳**은 안내 주석을 보고 몇 줄을 직접 써요.

### 입력칸은 이렇게 동작해요 (제어 컴포넌트)

```text
글자를 침 → onChange → setName('새 글자') → state가 바뀜 → 다시 그리기 → 칸에 '새 글자'가 보여요
```

입력칸에 보이는 값은 **늘 state**예요. 그래서 `setName('')`만 하면 칸이 비워져요.

#### 새로 나온 것

| 코드 | 뜻 |
|---|---|
| `value={name}` | 칸에 보일 값이에요 |
| `onChange={(e) => setName(e.target.value)}` | 글자를 칠 때마다 불려요. `e.target.value`는 칸에 지금 쓰인 글자예요 |
| `onSubmit={handleSubmit}` | 폼을 제출할 때(버튼, 엔터) 불려요 |
| `event: SubmitEvent<HTMLFormElement>` | 폼 제출 이벤트예요. `<HTMLFormElement>`는 "폼(`<form>`)에서 일어난 이벤트"라는 뜻이에요 |
| `event.preventDefault()` | 브라우저의 기본 동작(페이지 새로고침)을 막아요 |
| `try { } catch (err) { } finally { }` | Java와 같아요 |
| `(err as Error).message` | `err`를 `Error`로 보고 문구를 꺼내요 (Java의 형변환 `(Error) err`) |
| `description \|\| null` | 왼쪽이 **빈 글자**면 오른쪽 값을 써요 |
| `disabled={submitting}` | `true`면 버튼을 누를 수 없어요 |
| `submitting ? '만드는 중...' : '만들기'` | 조건 연산자예요. Java와 같아요 |

> **`??`(전반)와 `||`(이번)의 차이**
> `??`는 왼쪽이 `null`일 때만 오른쪽을 써요. `||`는 빈 글자(`''`)일 때도 오른쪽을 써요.
> 설명 칸을 비우면 `''`가 와요. 그래서 이번엔 `||`를 써야 `null`로 보내져요.

#### `FormEvent` 대신 `SubmitEvent`를 써요

템플릿에는 `FormEvent`라고 적혀 있었어요. 그런데 VS Code에서 줄이 그어지고 `'FormEvent' is deprecated`가 떠요.

- **deprecated**: "아직 동작하지만 앞으로는 쓰지 마세요"라는 표시예요. Java의 `@Deprecated`와 같아요.
- 이유: 설치된 React 타입(`@types/react` 19.3.0)에 이렇게 적혀 있어요. "React에는 FormEvent라는 이벤트가 따로 없어요. 제출이면 `SubmitEvent`, 입력칸 변경이면 `ChangeEvent`를 쓰세요."
- 빌드·린트·테스트는 이 표시를 잡지 못해요. 그래서 VS Code에서만 보여요.

두 곳을 이렇게 써요. (맨 위 import, 그리고 `handleSubmit` 줄)

```tsx
// SubmitEvent: 폼 제출 이벤트의 타입이에요. 타입만 쓰니까 import type이에요.
import type { SubmitEvent } from 'react'
import { useState } from 'react'
```

```tsx
  async function handleSubmit(event: SubmitEvent<HTMLFormElement>) {
    // 브라우저 기본 동작(페이지 새로고침)을 막아요.
    event.preventDefault()
```

import 줄을 빠뜨리면 `npm run build`가 `Type 'SubmitEvent' is not generic`으로 실패해요.
import가 없으면 TypeScript는 브라우저에 원래 있는 `SubmitEvent` 타입을 써요. 그 타입은 `<HTMLFormElement>` 같은 꺾쇠를 받지 않거든요.

<details>
<summary>정답 보기 (빈칸 5개)</summary>

```tsx
    event.preventDefault()
```

```tsx
        description: description || null,
```

```tsx
      onCreated()
```

```tsx
        <input value={name} onChange={(e) => setName(e.target.value)} required maxLength={100} />
```

```tsx
      <button type="submit" disabled={submitting}>
```

</details>

<details>
<summary>정답 보기 (직접 써 보기 1: 모델 칸)</summary>

```tsx
      <label>
        모델
        <input value={model} onChange={(e) => setModel(e.target.value)} required maxLength={100} />
      </label>
```

</details>

<details>
<summary>정답 보기 (직접 써 보기 2: 최대 스텝 칸)</summary>

```tsx
      <label>
        최대 스텝
        <input
          type="number"
          min={1}
          max={20}
          value={maxSteps}
          onChange={(e) => setMaxSteps(Number(e.target.value))}
        />
      </label>
```

`Number(...)`를 빠뜨리면 빌드가 `Argument of type 'string' is not assignable to parameter of type 'SetStateAction<number>'`로 실패해요.
입력칸의 값은 늘 글자로 와서, 숫자로 바꿔야 해요.

</details>

**확인**: `npm run build` → 성공. 아직 화면에는 안 나와요. `App`에서 쓰지 않았거든요.

---

## 5. App에 연결하기

### 5-1. 빈 목록 안내 문구 바꾸기

**파일**: `frontend/src/components/AgentList.tsx`

이제 화면에 만들기 폼이 있어요. `[3단계 후반 5]` 바로 아래 `return` 줄을 지우고, 그 밑의 주석을 풀어요.

### 5-2. App에 폼 넣기

**파일**: `frontend/src/App.tsx`

1. 위쪽(`[3단계 후반 5] 이 줄부터` ~ `여기까지 지워요.`)을 전부 지워요.
2. 아래쪽 주석을 모두 풀고 `____` 세 군데를 채워요.

#### 바뀌는 점

- 목록을 불러오는 코드를 `loadAgents` 함수로 뺐어요. **두 군데**에서 부르거든요. 처음 화면을 그릴 때(`useEffect`)와 에이전트를 만든 뒤(`onCreated`)예요.
- `<AgentForm onCreated={loadAgents} />`: **함수도 props로 넘길 수 있어요.** 폼은 만들기에 성공하면 이 함수를 불러요.
  Java로 치면 메서드에 `Runnable`을 넘기고, 받은 쪽이 `run()`을 부르는 것과 같아요.
- 다시 불러오기에 성공하면 `setError(null)`로 예전 에러 문구를 지워요.

<details>
<summary>정답 보기</summary>

```tsx
        setError(null) // 전에 났던 에러 문구는 지워요.
```

```tsx
  useEffect(() => {
    loadAgents()
  }, [])
```

```tsx
      <AgentForm onCreated={loadAgents} />
```

</details>

**확인**

```powershell
npm run build
```

```powershell
npm run lint
```

```powershell
npm test
```

빌드 성공, 린트는 아무것도 안 나오고, 테스트는 `Tests  5 passed (5)`예요.

**커밋 3**: `feat: 에이전트 만들기 폼`

---

## 6. 직접 확인하기

백엔드(`uv run fastapi dev app/main.py`)와 프론트엔드(`npm run dev`)를 켜고 http://localhost:5173 을 열어요.

| 해 볼 것 | 이렇게 보여야 해요 |
|---|---|
| 이름을 쓰고 **만들기** | 목록에 바로 추가돼요. 이름·설명 칸은 비워지고, 나머지 칸은 그대로예요 |
| 방금 만든 이름으로 한 번 더 | 폼 아래에 `Agent name already exists: (이름)` |
| 이름 칸에 **스페이스만** 넣고 만들기 | `name: String should have at least 1 character` |
| 이름 칸을 비우고 만들기 | 브라우저가 "이 입력란을 작성하세요." 같은 말풍선으로 막아요 (`required`) |
| 터미널에서 백엔드를 끄고(`Ctrl+C`) 만들기 | `요청이 실패했어요 (HTTP 502)` |

> **스페이스만 넣으면 왜 422예요?** 브라우저는 스페이스도 글자로 봐서 그냥 보내요.
> 그런데 백엔드가 앞뒤 공백을 지워요(1단계의 `str_strip_whitespace`). 그러면 빈 이름이 돼서 422가 나요.

만든 에이전트는 개발 DB에 저장돼요. http://localhost:8000/docs 의 `GET /api/agents`에서도 보여요.

---

## 7. 더 해 보기 (선택)

여유가 있으면 해 보세요. 안 해도 PR에는 문제없어요. 했다면 커밋을 하나 더 해요.
(예: `feat: 목록 개수와 만들기 성공 문구 표시`)

### 7-1. 목록 제목 옆에 개수 보여주기

`에이전트 목록 (3)`처럼 보이게 해 보세요. **힌트**: `App.tsx`의 `<h2>`예요. 배열의 개수는 `agents.length`예요.

<details>
<summary>정답 보기</summary>

```tsx
      <h2>에이전트 목록 ({agents.length})</h2>
```

</details>

### 7-2. 만들기에 성공하면 "만들었어요: 이름" 보여주기

**힌트**

1. `AgentForm.tsx`에 state를 하나 더 만들어요 (`created`, 처음 값은 `null`).
2. 제출을 시작할 때 `setCreated(null)`로 지우고, 성공하면 `setCreated(name)`으로 이름을 넣어요.
3. 에러 문구처럼 `created && ...`로 보여줘요. `className="success"`를 붙여요.
4. `App.css` 맨 아래에 초록색 스타일을 넣어요.

<details>
<summary>정답 보기</summary>

```tsx
  const [error, setError] = useState<string | null>(null)
  // 방금 만든 에이전트 이름이에요. 만들기에 성공하면 문구로 보여줘요.
  const [created, setCreated] = useState<string | null>(null)
```

```tsx
    setError(null)
    setCreated(null)
```

```tsx
      setCreated(name)
      setName('')
```

```tsx
      {error && <p className="error">{error}</p>}
      {created && <p className="success">만들었어요: {created}</p>}
```

`App.css` 맨 아래:

```css
.agent-form .success {
  grid-column: 1 / -1;
  color: #30a46c;
}
```

</details>

### 7-3. 422 에러가 두 개일 때 테스트

이름도 비고 temperature도 1을 넘으면, 422의 `detail` 목록에 문제가 **2개** 들어와요.
`errors.test.ts`에 테스트를 하나 더 써 보세요. 쉼표로 이어진 문구가 나와야 해요.

<details>
<summary>정답 보기</summary>

```ts
  it('문제가 여러 개면 쉼표로 이어서 보여줘요', () => {
    const body = {
      detail: [
        { loc: ['body', 'name'], msg: 'String should have at least 1 character' },
        { loc: ['body', 'temperature'], msg: 'Input should be less than or equal to 1' },
      ],
    }

    expect(toErrorMessage(422, body)).toBe(
      'name: String should have at least 1 character, temperature: Input should be less than or equal to 1',
    )
  })
```

`npm test` → `Tests  6 passed (6)`

</details>

---

## 8. README와 SETUP.md 업데이트

**README.md**

1. 5번째 줄: `현재 상태: **3단계 완료** (에이전트 목록, 만들기 폼)`
2. 로드맵: `- [x] 3. React 화면: 에이전트 목록 / 생성`

**SETUP.md** (PR #4에서 들어온 설치 가이드예요)

1. "6. 테스트·검사·마이그레이션"의 코드 블록에서 `npm.cmd run build` 아래에 한 줄을 넣어요.

   ```text
   npm.cmd test
   ```

2. 같은 절 맨 아래 "이 PC에서 확인한 결과" 문단의 마지막 문장을 바꿔요.
   - 지금: `` `fastapi dev` 서버를 띄워 브라우저로 확인하는 것은 아직 해 보지 않았습니다. ``
   - 바꾼 뒤: `` YYYY-MM-DD에 `fastapi dev`와 `npm run dev`를 띄워 브라우저에서 목록과 만들기 폼을 확인했습니다. ``
   - `YYYY-MM-DD`에는 6번에서 화면을 직접 확인한 날짜를 써요.

SETUP.md는 "~습니다" 말투로 쓰여 있어서, 고칠 때도 그 말투에 맞춰요.

**커밋 4**: `docs: README와 SETUP에 3단계 완료 반영`

### 8-1. 커밋할 파일 정리

명령은 프로젝트 맨 위 폴더(`C:\agentlab`)에서 쳐요. 이번에도 `git add .`는 쓰지 말고 파일을 골라서 넣어요.

| 커밋 | 언제 | 파일 |
|---|---|---|
| 1 `feat: 에이전트 만들기 타입과 에러 문구 함수` | 2번 뒤 | `frontend/src/types/agent.ts`, `frontend/src/utils/errors.ts`, `frontend/src/utils/errors.test.ts`, `docs/guide/03-agent-create-form.md` |
| 2 `feat: 에이전트 만들기 API 함수` | 3번 뒤 | `frontend/src/api/agents.ts` |
| 3 `feat: 에이전트 만들기 폼` | 5번 뒤 | `frontend/src/components/AgentForm.tsx`, `frontend/src/components/AgentList.tsx`, `frontend/src/App.tsx`, `frontend/src/App.css`, `docs/guide/03-agent-create-form.md` (4번 `SubmitEvent` 수정분) |
| (선택) `feat: 목록 개수와 만들기 성공 문구 표시` | 7번 뒤 | 7번에서 바꾼 파일 |
| 4 `docs: README와 SETUP에 3단계 완료 반영` | 8번 뒤 | `README.md`, `SETUP.md` |

---

## 9. PR 만들고 merge하기

1. `git push -u origin feat/agent-create-form`
2. GitHub에서 PR을 만들어요. 제목은 `feat: 에이전트 만들기 폼 (3단계 후반)`이에요.
   (PR을 만들 때 **제목 칸을 꼭 확인**해요. 지난번처럼 브랜치 이름이 들어가 있으면 바꿔요.)
3. "화면" 섹션에 폼이 보이는 캡처를 넣어요.
4. **merge하기 전에 저에게 리뷰를 요청하세요.**
5. 리뷰 반영 → **Create a merge commit** → 로컬 정리 (`git switch main`, `git pull`, `git branch -d feat/agent-create-form`)

---

## 10. 자주 만나는 에러

| 증상 | 원인 | 해결 |
|---|---|---|
| `npm test`에서 `TypeError: toErrorMessage is not a function` | 2-2를 아직 안 했어요 (2-1 바로 뒤에는 정상이에요) | `errors.ts` 주석 풀기 |
| `npm run build`에서 `Cannot find name 'AgentCreateInput'` 또는 `'toErrorMessage'` | 3번 맨 위 import를 안 바꿨어요 | 3번 1을 해요 |
| `npm run build`에서 `Cannot find name '____'` | 빈칸이 남아 있어요 | `Ctrl+Shift+F`로 `____`를 찾아요 |
| `Argument of type 'string' is not assignable to ... SetStateAction<number>` | 숫자 칸에서 `Number(...)`를 빠뜨렸어요 | `setMaxSteps(Number(e.target.value))` |
| VS Code에서 `FormEvent`에 줄이 그어지고 `'FormEvent' is deprecated` | React 타입에서 "쓰지 마세요" 표시가 붙은 이름이에요 (빌드는 돼요) | `SubmitEvent`로 바꿔요 (4번) |
| `npm run build`에서 `Type 'SubmitEvent' is not generic` | `import type { SubmitEvent } from 'react'` 줄이 빠졌어요 | 맨 위에 import 줄을 넣어요 (4번) |
| 만들기를 누르면 페이지가 새로고침돼요 | `event.preventDefault()`가 빠졌어요 | 4번 첫 빈칸 |
| 입력칸에 글자가 안 써져요 | `value`는 있는데 `onChange`가 없어요 (state가 안 바뀌어요) | `onChange`를 넣어요 |
| 만들었는데 목록이 안 바뀌어요 | `onCreated()`를 안 불렀거나, App에서 `onCreated={loadAgents}`를 안 넘겼어요 | 4번 세 번째 빈칸, 5-2 |
| 설명을 비웠는데 목록에 `-` 대신 빈칸이 보여요 | `description \|\| null`이 빠져서 빈 글자가 저장됐어요 | 4번 두 번째 빈칸 |
| 폼 아래에 `요청이 실패했어요 (HTTP 502)` | 백엔드가 꺼져 있어요 | `uv run fastapi dev app/main.py` |

## 11. 완료 체크리스트

- [ ] 화면에서 만들면 목록에 바로 나와요
- [ ] 같은 이름 → 409 문구, 스페이스만 넣은 이름 → 422 문구, 백엔드를 끄면 502 문구가 나와요
- [ ] `npm run build` → 성공
- [ ] `npm run lint` → 아무것도 안 나와요
- [ ] VS Code에서 줄이 그어진 이름(deprecated)이 없어요
- [ ] `npm test` → `Tests  5 passed (5)` (7-3을 했으면 6)
- [ ] `[3단계`, `[직접 써 보기` 안내 줄과 `____`가 남아 있지 않아요 (`Ctrl+Shift+F`로 검색)
- [ ] 커밋 4개 (더 해 보기를 했으면 5개)
- [ ] PR → 리뷰 → merge
