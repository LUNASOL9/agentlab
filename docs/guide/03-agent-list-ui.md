# 3단계 (전반): React로 에이전트 목록 화면 만들기

**이번 단계 목표**

- 브라우저 화면(React)에서 백엔드 API를 불러 **에이전트 목록**을 보여준다
- TypeScript로 API 응답의 모양(타입)을 적는다
- 시간을 **한국 시간**으로 보여주고, 그 함수를 **Vitest**로 테스트한다
- 이번에도 브랜치 → PR → 리뷰 → merge

예상 시간: 하루 1~2시간 기준 3~4일

에이전트를 **만드는 폼**은 3단계 후반에 해요.

> 이번 내용도 이 PC에서 빈칸을 처음부터 끝까지 채워 보고, 단계마다 빌드·린트·테스트 결과가 아래 적힌 대로 나오는지 확인했어요.
> 완성된 화면도 실제 백엔드에 붙여서 목록이 나오는 걸 봤어요.

---

## 제가 미리 해 둔 것

- 브랜치 `feat/agent-list-ui`를 만들었어요. 지금 이 브랜치에 있어요 (`git branch`로 확인).
- Vite 기본 화면에 쓰던 그림 파일을 지웠어요 (`src/assets/`, `public/icons.svg`).
- `App.css`를 목록 화면용 스타일로 바꿨어요. `index.css`는 가운데 정렬을 왼쪽 정렬로 바꿨어요.
- 빈칸 템플릿을 넣었어요. `[3단계 2]`처럼 번호가 붙어 있어요.

```text
frontend/
├── vite.config.ts                  # 개발 서버 설정 (2번)
└── src/
    ├── types/agent.ts              # 에이전트의 모양 (3번)
    ├── api/agents.ts               # 백엔드를 부르는 함수 (4번)
    ├── utils/format.ts             # 한국 시간으로 바꾸는 함수 (5번)
    ├── utils/format.test.ts        # 그 함수의 테스트 (5번)
    ├── components/AgentList.tsx    # 목록 표 (6번)
    └── App.tsx                     # 첫 화면, 위의 것들을 연결해요 (7번)
```

**지금 상태**: `npm run build` → 성공, `npm run lint` → 아무것도 안 나와요 (통과).
화면에는 제목과 "목록은 7번에서 보여 줄 거예요."만 나와요.

**프론트엔드 명령은 모두 `frontend` 폴더에서** 실행해요.

```powershell
cd frontend
```

### 빈칸 채우기 방법 (전과 같아요, 주석 기호만 달라요)

- TypeScript의 주석은 `//`예요 (Python은 `#`). 똑같이 `Ctrl+/`로 풀어요.
- `// // 설명`을 풀면 `// 설명`이 돼요. 설명 주석은 그대로 남아요.
- 화면 코드(JSX) 안의 주석은 `{/* ... */}` 모양이에요. 풀어도 주석으로 남는 게 정상이에요.
- 프론트엔드 파일은 저장해도 자동 정리가 안 돼요. 들여쓰기는 템플릿 그대로 두면 돼요.
- 다 채운 안내 줄(`[3단계 ...]`)은 지워요. 막히면 단계 맨 아래 **정답 보기**를 눌러요.

### 전체 그림

```text
 브라우저 (http://localhost:5173)
    │  ① 화면 파일(HTML, JS)과 ② /api 요청을 모두 5173으로 보내요
    ▼
 Vite 개발 서버 (npm run dev, 5173)
    │  /api로 시작하는 요청만 백엔드로 넘겨요 (프록시, 2번에서 설정해요)
    ▼
 FastAPI (uv run fastapi dev, 8000)  ──▶  PostgreSQL (Docker, 5432)
```

---

## 0. React는 뭘 하나요?

1·2단계에서는 /docs(Swagger)로 API를 불렀어요. 이번엔 **우리가 만든 화면**이 API를 불러요.

| | Spring MVC + JSP (서버에서 HTML 만들기) | React |
|---|---|---|
| HTML을 만드는 곳 | 서버 | 브라우저 |
| 서버가 주는 것 | 완성된 HTML | JSON 데이터 |
| 데이터가 바뀌면 | 페이지 전체를 다시 받아요 | 바뀐 부분만 다시 그려요 |

### 용어 4개만 알면 돼요

| 용어 | 뜻 | Java로 비유하면 |
|---|---|---|
| 컴포넌트 | 화면 조각을 그리는 함수예요. 이름이 대문자로 시작해요 (`AgentList`) | 화면을 돌려주는 메서드 |
| props | 컴포넌트에 넘기는 값이에요 | 메서드의 매개변수 |
| state (`useState`) | 바뀌면 화면이 다시 그려지는 값이에요 | 필드인데, 값을 바꾸면 화면이 저절로 다시 그려져요 |
| effect (`useEffect`) | 화면이 그려진 **다음에** 할 일이에요 (예: API 부르기) | (비유 없음) |

**TypeScript**는 JavaScript에 **타입**을 붙인 언어예요. Java처럼 빌드할 때 타입 실수를 잡아 줘요. 브라우저에서 돌 때는 타입을 지운 JavaScript로 바뀌어요.

---

## 1. 서버 켜기

이번 단계는 터미널 2개를 켜 두고 해요.

| 터미널 | 폴더 | 명령 |
|---|---|---|
| 1 | `C:\agentlab` → `backend` | `docker compose up -d` 한 다음 `cd backend`, `uv run fastapi dev app/main.py` |
| 2 | `frontend` | `npm run dev` |

http://localhost:5173 을 열면 "AgentLab" 제목과 "목록은 7번에서 보여 줄 거예요."가 보여요.

> http://localhost:8000/docs 에서 에이전트를 2~3개 만들어 두세요. 7번에서 목록에 나와요. (이미 있으면 안 만들어도 돼요)

---

## 2. Vite 프록시 설정하기

### 왜 필요해요?

화면은 5173에서 오고, API는 8000에 있어요. 브라우저는 **화면을 받은 주소와 다른 주소**로 요청하는 걸 기본으로 막아요.
다른 사이트가 내 정보를 몰래 가져가지 못하게 하는 브라우저의 보안 규칙(CORS)이에요.

그래서 화면은 5173에만 요청하고, Vite 개발 서버가 `/api` 요청을 백엔드로 넘겨 줘요(프록시).

```text
브라우저 ── GET /api/agents ──▶ Vite(5173) ── 그대로 전달 ──▶ FastAPI(8000)
```

### 빈칸 채우기

**파일**: `frontend/vite.config.ts`

`[3단계 2]`의 주석을 풀고 `____`를 채워요. 백엔드가 쓰는 포트 번호예요.

<details>
<summary>정답 보기</summary>

```ts
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:8000',
    },
  },
```

</details>

저장하면 터미널 2에 `vite.config.ts changed, restarting server...`가 나오고 Vite가 알아서 다시 켜져요.

**확인**: 브라우저에서 http://localhost:5173/api/health 를 열어요.

```text
{"status":"ok","database":"ok"}
```

5173으로 요청했는데 백엔드의 응답이 왔어요. 프록시가 동작하는 거예요.

---

## 3. 에이전트의 모양 적기 (타입)

**파일**: `frontend/src/types/agent.ts`

백엔드가 돌려주는 JSON이 어떻게 생겼는지 TypeScript로 적어요. `backend/app/schemas/agent.py`의 `AgentRead`와 짝이에요.
주석을 모두 풀고 `____` 세 군데를 채워요.

| Python (백엔드) | TypeScript (프론트엔드) | Java |
|---|---|---|
| `int`, `float` | `number` (숫자 타입은 하나예요) | `int`, `double` |
| `str` | `string` | `String` |
| `str \| None` | `string \| null` | 값이 없을 수 있는 `String` |
| `datetime` | `string` (JSON에서는 글자로 와요) | |

<details>
<summary>정답 보기</summary>

```ts
  id: number
```

```ts
  description: string | null
```

```ts
  max_steps: number
```

</details>

**확인**: `npm run build` → 성공 (`✓ built in ...`). 빌드할 때 TypeScript가 타입을 검사해요.

---

## 4. 백엔드를 부르는 함수 만들기

**파일**: `frontend/src/api/agents.ts`

주석을 모두 풀고 `____` 세 군데를 채워요.

#### 새로 나온 것

| 코드 | 뜻 |
|---|---|
| `import type { Agent }` | 타입만 가져와요. 실행되는 코드에는 안 들어가요 |
| `async function` / `await` | `await`에서 응답이 올 때까지 기다려요. 그동안 화면은 멈추지 않아요 |
| `Promise<Agent[]>` | "나중에 Agent 배열이 와요"라는 약속이에요 (Java의 `CompletableFuture<List<Agent>>`) |
| `fetch('/api/agents')` | 브라우저에 들어 있는 HTTP 요청 함수예요 |
| `response.ok` | 상태 코드가 200~299면 `true`예요 |
| `` `... ${response.status}` `` | 글자 안에 값을 넣어요 (Python의 f-string) |

<details>
<summary>정답 보기</summary>

```ts
export async function fetchAgents(): Promise<Agent[]> {
  const response = await fetch('/api/agents')
  if (!response.ok) {
```

</details>

**확인**: `npm run build` → 성공

**커밋 1**: `chore: 기본 화면 정리와 API 프록시 설정`
**커밋 2**: `feat: 에이전트 타입과 목록 API 함수 추가`
(커밋할 파일은 맨 아래 9-1에 정리해 뒀어요)

---

## 5. 한국 시간으로 보여주기 + 첫 프론트엔드 테스트

API는 시간을 `2026-11-07T00:54:49.334043Z`(UTC)로 줘요. 화면에는 `2026. 11. 7. 오전 9:54:49`(한국 시간)로 보여 줄 거예요.
이번에도 **테스트부터** 써요. 프론트엔드 테스트 도구는 **Vitest**예요 (백엔드의 pytest 역할).

### 5-1. Vitest 설치하기

```powershell
# -D: 개발할 때만 쓰는 도구로 설치해요. (uv add --dev와 같아요)
npm install -D vitest
```

→ `added 20 packages ...`

`package.json`의 `scripts`에 `test` 한 줄을 추가해요. 바로 위 줄 끝에 **쉼표**를 붙이는 걸 잊지 마세요.

```json
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "oxlint",
    "preview": "vite preview",
    "test": "vitest run"
  },
```

`vitest run`은 테스트를 한 번만 돌리고 끝나요 (`uv run pytest`처럼요).

### 5-2. 테스트 먼저 쓰기

**파일**: `frontend/src/utils/format.test.ts`

주석을 모두 풀고 `____` 두 군데를 채워요. **9시간을 더하면** 몇 시, 며칠인지 생각해 보세요.

| Vitest | pytest |
|---|---|
| `describe('이름', () => { ... })` | 테스트 묶음 (파일이나 클래스) |
| `it('설명', () => { ... })` | `def test_...():` |
| `expect(값).toBe(기댓값)` | `assert 값 == 기댓값` |

<details>
<summary>정답 보기</summary>

```ts
    expect(formatDateTime('2026-11-07T00:54:49.334043Z')).toBe('2026. 11. 7. 오전 9:54:49')
```

```ts
    expect(formatDateTime('2026-11-07T15:04:05Z')).toBe('2026. 11. 8. 오전 12:04:05')
```

UTC 15시 4분에 9시간을 더하면 다음 날 0시 4분이에요. 한국어 형식에서는 0시를 `오전 12시`로 써요.

</details>

```powershell
npm test
```

→ **2개 실패**가 정상이에요. 아직 함수를 안 만들었어요.

```text
TypeError: formatDateTime is not a function
 Test Files  1 failed (1)
      Tests  2 failed (2)
```

(지금은 `npm run build`도 `error TS2305: Module '"./format"' has no exported member 'formatDateTime'`로 실패해요. 5-3을 하면 둘 다 해결돼요.)

### 5-3. 함수 만들기

**파일**: `frontend/src/utils/format.ts`

주석을 모두 풀고 `____`를 채워요. 한국 시간대의 이름이에요 (주석에 힌트가 있어요).

<details>
<summary>정답 보기</summary>

```ts
  return new Date(isoText).toLocaleString('ko-KR', { timeZone: 'Asia/Seoul' })
```

</details>

```powershell
npm test
```

```text
 Test Files  1 passed (1)
      Tests  2 passed (2)
```

**커밋 3**: `feat: 한국 시간 표시 함수와 첫 프론트엔드 테스트`

---

## 6. 목록 표 컴포넌트 만들기

**파일**: `frontend/src/components/AgentList.tsx`

주석을 모두 풀고 `____` 세 군데를 채워요.

#### 새로 나온 것

| 코드 | 뜻 |
|---|---|
| `function AgentList({ agents }: AgentListProps)` | 컴포넌트예요. props 객체에서 `agents`만 꺼내 써요 (구조 분해) |
| `return <table>...</table>` | 돌려주는 값이 화면이에요. HTML처럼 생긴 이 문법을 **JSX**라고 해요 |
| `className="..."` | HTML의 `class`예요. `class`는 자바스크립트 예약어라서 이름이 달라요 |
| `{ 값 }` | JSX 안에서 자바스크립트 값을 쓸 때 감싸요 |
| `agents.map((agent) => (<tr>...</tr>))` | 배열의 에이전트 하나하나를 `<tr>` 한 줄로 바꿔요 (Java Stream의 `map`) |
| `key={agent.id}` | React가 줄을 구분하는 이름표예요. 겹치지 않는 값을 써요 |
| `agent.description ?? '-'` | 왼쪽 값이 `null`이면 오른쪽 값을 써요 |

<details>
<summary>정답 보기</summary>

```tsx
  if (agents.length === 0) {
```

```tsx
        {agents.map((agent) => (
```

```tsx
          <tr key={agent.id}>
```

</details>

**확인**: `npm run build` → 성공. 아직 화면에는 안 나와요. `App`에서 이 컴포넌트를 쓰지 않았거든요 (7번에서 연결해요).

---

## 7. App에 연결하기

**파일**: `frontend/src/App.tsx`

1. 위쪽(`[3단계 7] 이 줄부터` ~ `[3단계 7] 여기까지 지워요.`)을 **전부 지워요.** 지금 보이는 임시 화면이에요.
2. 아래쪽 주석을 **모두 풀고** `____` 다섯 군데를 채워요.

#### 새로 나온 것

| 코드 | 뜻 |
|---|---|
| `const [agents, setAgents] = useState<Agent[]>([])` | `agents`는 지금 값, `setAgents`는 값을 바꾸는 함수예요. 처음 값은 빈 배열이에요 |
| `setAgents(data)` | 값을 바꿔요. 그러면 React가 화면을 **다시 그려요** |
| `useEffect(() => { ... }, [])` | 화면이 처음 그려진 다음 **한 번만** 실행해요 |
| `.then(...)` / `.catch(...)` / `.finally(...)` | 성공했을 때 / 실패했을 때 / 어느 쪽이든 끝났을 때 할 일이에요 |
| `{loading && <p>...</p>}` | `loading`이 `true`일 때만 보여줘요 |
| `<AgentList agents={agents} />` | 컴포넌트에 props로 목록을 넘겨요 (메서드에 인자를 넘기는 것과 같아요) |

#### 화면이 그려지는 순서

```text
① 처음 그리기: agents=[], loading=true      → "불러오는 중..."
② useEffect 실행: fetchAgents()로 백엔드에 요청
③ 응답 도착: setAgents(목록), setLoading(false) → 값이 바뀌어서 다시 그리기
④ 다시 그리기: loading=false, error=null    → <AgentList agents={목록} />
```

<details>
<summary>정답 보기</summary>

```tsx
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
```

```tsx
      .finally(() => setLoading(false))
  }, [])
```

```tsx
      {!loading && !error && <AgentList agents={agents} />}
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

빌드 성공, 린트는 아무것도 안 나오고, 테스트는 `Tests  2 passed (2)`예요.

브라우저에서 http://localhost:5173 을 다시 보면 목록이 보여요.

```text
에이전트 목록
이름     설명     모델   temperature   최대 스텝   만든 시각
QWER     string   mock   0.7           5           2026. 11. 7. 오전 11:35:28
alpha    string   mock   0.7           5           2026. 11. 7. 오전 11:36:01
```

(이름과 시간은 각자 만든 에이전트에 따라 달라요. `string`은 /docs에서 예시 값을 안 바꾸고 만들어서 그래요.)

**커밋 4**: `feat: 에이전트 목록 화면`

---

## 8. 직접 확인하기

1. **한국 시간**: `만든 시각`이 /docs의 `created_at`보다 9시간 늦게 보이면 맞아요. (`...T02:35:28Z` → `오전 11:35:28`)
2. **백엔드가 꺼졌을 때**: 터미널 1에서 `Ctrl+C`로 백엔드를 끄고 화면을 새로고침해요.

   ```text
   목록을 불러오지 못했어요 (HTTP 502)
   ```

   터미널 2(Vite)에는 이런 줄이 나와요. 백엔드(8000)에 연결이 안 된다는 뜻이에요.

   ```text
   [vite] http proxy error: /api/agents
   Error: connect ECONNREFUSED 127.0.0.1:8000
   ```

   다시 `uv run fastapi dev app/main.py`로 켜고 새로고침하면 목록이 돌아와요.
3. **요청이 두 번 가요**: 브라우저에서 `F12` → **Network** 탭을 열고 새로고침해 보세요. `agents` 요청이 **2번** 보여요.
   개발 모드에서는 React의 `StrictMode`(`main.tsx`)가 실수를 찾으려고 effect를 일부러 두 번 실행해요. 배포용(`npm run build`)에서는 한 번이에요. 정상이에요.

---

## 9. README 업데이트

`README.md`를 이렇게 바꿔요.

1. 5번째 줄: `현재 상태: **3단계 진행 중** (목록 화면 완료, 만들기 폼 예정)`
2. 기술 스택 표의 Tooling 줄: `| Tooling | uv, pytest, Ruff, Vitest, Oxlint, Docker, Git / GitHub |`
3. "프론트엔드" 섹션 코드 블록 위에 한 줄을 넣어요.
   `백엔드를 먼저 켜요. 화면의 /api 요청은 백엔드(8000)로 넘어가요.`
4. "테스트" 섹션에 프론트엔드 테스트를 추가해요.

   ```bash
   cd frontend
   npm test
   ```

**커밋 5**: `docs: README에 프론트엔드 실행·테스트 방법 추가`

### 9-1. 커밋할 파일 정리

명령은 프로젝트 맨 위 폴더(`C:\agentlab`)에서 쳐요. `git add .`는 쓰지 말고 파일을 골라서 넣어요.
아직 안 한 단계의 템플릿 파일이 섞이지 않게 하려는 거예요.

| 커밋 | 언제 | 파일 |
|---|---|---|
| 1 `chore: 기본 화면 정리와 API 프록시 설정` | 2번 뒤 | `frontend/src/App.tsx`, `frontend/src/App.css`, `frontend/src/index.css`, `frontend/src/assets`, `frontend/public/icons.svg`, `frontend/vite.config.ts`, `docs/guide/03-agent-list-ui.md` |
| 2 `feat: 에이전트 타입과 목록 API 함수 추가` | 4번 뒤 | `frontend/src/types/agent.ts`, `frontend/src/api/agents.ts` |
| 3 `feat: 한국 시간 표시 함수와 첫 프론트엔드 테스트` | 5번 뒤 | `frontend/src/utils/format.ts`, `frontend/src/utils/format.test.ts`, `frontend/package.json`, `frontend/package-lock.json` |
| 4 `feat: 에이전트 목록 화면` | 7번 뒤 | `frontend/src/components/AgentList.tsx`, `frontend/src/App.tsx` |
| 5 `docs: README에 프론트엔드 실행·테스트 방법 추가` | 9번 뒤 | `README.md` |

- 커밋 1의 `frontend/src/assets`와 `frontend/public/icons.svg`는 **지운 파일**이에요. `git add`에 지운 파일 경로를 쓰면 "지웠음"이 커밋에 담겨요.
- 커밋 1의 `App.tsx`에는 7번 템플릿이 주석으로 같이 들어가요. 7번에서 바뀌니까 괜찮아요.

---

## 10. PR 만들고 merge하기

1. `git push -u origin feat/agent-list-ui`
2. GitHub에서 PR을 만들어요. 제목은 `feat: 에이전트 목록 화면 (3단계 전반)`이에요.
3. **merge하기 전에 저에게 리뷰를 요청하세요.**
4. 리뷰 반영 → **Create a merge commit** → 로컬 정리 (`git switch main`, `git pull`, `git branch -d feat/agent-list-ui`)

---

## 11. 자주 만나는 에러

| 증상 | 원인 | 해결 |
|---|---|---|
| 화면에 `목록을 불러오지 못했어요 (HTTP 502)` | 백엔드(8000)가 꺼져 있어요 | 터미널 1에서 `uv run fastapi dev app/main.py` |
| 화면에 `목록을 불러오지 못했어요 (HTTP 500)` | 백엔드는 켜져 있는데 DB가 꺼져 있어요 | `docker compose up -d` |
| 화면에 `목록을 불러오지 못했어요 (HTTP 404)` | 4번 `fetch('/api/____')`의 빈칸을 안 채웠어요 | `'/api/agents'` |
| `npm run build`에서 `Cannot find name '____'` | 빈칸을 안 채운 곳이 있어요 | `Ctrl+Shift+F`로 `____`를 찾아요 |
| `npm test`에서 `Missing script: "test"` | 5-1에서 `scripts`에 `test`를 안 넣었어요 | `"test": "vitest run"` 추가 |
| `npm test`에서 `TypeError: formatDateTime is not a function` | 5-3을 아직 안 했어요 (5-2 바로 뒤에는 정상이에요) | `format.ts` 주석 풀기 |
| `package.json`을 고친 뒤 `EJSONPARSE`가 들어간 에러 | `"preview": "vite preview"` 줄 끝의 쉼표를 빠뜨렸어요 | 쉼표 추가 |
| 시간이 9시간 다르게 보여요 | `timeZone` 옵션을 빠뜨렸어요 | `{ timeZone: 'Asia/Seoul' }` |

## 12. 완료 체크리스트

- [ ] http://localhost:5173 에 에이전트 목록이 한국 시간으로 보여요
- [ ] 백엔드를 끄면 `목록을 불러오지 못했어요 (HTTP 502)`가 보여요
- [ ] `npm run build` → 성공
- [ ] `npm run lint` → 아무것도 안 나와요
- [ ] `npm test` → `Tests  2 passed (2)`
- [ ] `[3단계` 안내 줄을 모두 지웠고, `____`가 남아 있지 않아요 (`Ctrl+Shift+F`로 검색)
- [ ] 커밋 5개 (정리·프록시, 타입·API, 시간 표시·테스트, 목록 화면, README)
- [ ] PR → 리뷰 → merge
