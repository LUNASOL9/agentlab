# 0단계: 개발 환경과 Git 첫걸음

**이번 단계 목표**

- 백엔드(FastAPI)와 프론트엔드(React)를 내 PC에서 실행해 본다
- Git으로 커밋을 만들고 GitHub에 올린다
- "코드 수정 → 테스트 → 커밋 → 푸시"를 한 바퀴 직접 돌아본다

예상 시간: 1~2시간

---

## 1. VS Code로 프로젝트 열기

1. VS Code → **파일 → 폴더 열기** → `agentlab` 폴더 선택
2. 오른쪽 아래에 "권장 확장" 알림이 뜨면 **모두 설치**해요.
   (알림이 안 보이면 확장 탭에서 `@recommended` 검색)
   - **Python**: 파이썬 실행, 디버깅, 테스트
   - **Ruff**: 파이썬 린트와 자동 포맷 (Checkstyle + 포매터 역할)
   - **Oxc**: TypeScript / React 린트
   - **Git Graph**: 브랜치와 커밋 히스토리를 그림으로 보여줘요
3. 터미널 열기: `` Ctrl+` `` (숫자 1 왼쪽 키)

이번 실습에서는 터미널 3개를 써요. 터미널 패널 오른쪽 위 `+`로 새 터미널을 열 수 있어요.

| 터미널 | 용도 |
|---|---|
| 1 | 백엔드 서버 (켜두기) |
| 2 | 프론트엔드 서버 (켜두기) |
| 3 | 작업용: 테스트, Git 명령 |

## 2. 프로젝트 구조

```text
agentlab/
├── backend/            # FastAPI (Python)
│   ├── app/main.py     # 애플리케이션 진입점
│   ├── tests/          # pytest 테스트
│   ├── pyproject.toml  # 의존성과 설정 (build.gradle 역할)
│   └── uv.lock         # 정확한 버전 고정 (커밋해요)
├── frontend/           # React + TypeScript (Vite)
│   ├── src/App.tsx     # 첫 화면 컴포넌트
│   └── package.json    # 의존성과 스크립트
├── docs/guide/         # 단계별 실습 가이드 (지금 이 문서)
├── .gitignore          # Git이 무시할 파일 목록
└── README.md
```

## 3. 백엔드 실행 (터미널 1)

```powershell
cd backend
uv run fastapi dev app/main.py
```

- http://localhost:8000 → `{"message":"Hello, AgentLab!"}`
- http://localhost:8000/docs → Swagger UI. springdoc 설정 없이 자동으로 생겨요.
- `fastapi dev`는 코드를 저장하면 자동으로 재시작돼요 (Spring DevTools와 비슷해요).
- 종료할 때는 `Ctrl+C`

### uv 명령어를 Gradle에 비유하면

| uv | Gradle에서는 | 하는 일 |
|---|---|---|
| `uv sync` | 의존성 내려받기 | `uv.lock`에 적힌 버전대로 `.venv`에 설치 |
| `uv add fastapi` | `implementation` 추가 | 의존성 추가 + 설치 |
| `uv add --dev pytest` | `testImplementation` 추가 | 개발할 때만 쓰는 의존성 |
| `uv run <명령>` | `./gradlew bootRun` | 프로젝트 전용 환경(`.venv`)에서 실행 |

`.venv` 폴더는 이 프로젝트 전용 파이썬과 라이브러리가 들어 있는 곳이에요. 각자 PC에서 `uv sync`로 다시 만들 수 있어서 커밋하지 않아요.

## 4. 프론트엔드 실행 (터미널 2)

```powershell
cd frontend
npm run dev
```

- http://localhost:5173 → Vite + React 기본 화면

## 5. 테스트 실행 (터미널 3)

```powershell
cd backend
uv run pytest
```

`1 passed`가 나오면 성공이에요. VS Code 왼쪽의 플라스크 아이콘(테스트 탭)에서도 실행할 수 있어요.

---

## 6. Git 핵심 개념 (5분)

Git은 파일의 **저장 지점(커밋)**을 기록하는 도구예요. 변경 사항은 아래 순서로 이동해요.

```text
 작업 폴더  ──git add──▶  스테이징  ──git commit──▶  로컬 저장소  ──git push──▶  GitHub
(파일 수정)              (담아두기)                  (.git 폴더)                (원격 저장소)
```

- **작업 폴더**: 지금 VS Code에서 편집하는 파일
- **스테이징**: "이번 커밋에 넣을 변경"을 골라 담는 장바구니
- **커밋**: 장바구니를 하나의 저장 지점으로 확정해요. 메시지가 붙어요.
- **push**: 내 PC의 커밋을 GitHub로 올려요.

## 7. 실습 ① 내 정보 확인 (처음 한 번만)

```powershell
git config --global user.name
git config --global user.email
```

- **이름**은 모든 커밋에 작성자로 찍혀요. 포트폴리오용이면 본인 이름이나 GitHub 아이디로 해두세요.
- **이메일**은 GitHub 계정에 등록된 이메일과 같아야 커밋이 GitHub 프로필(잔디)에 표시돼요.

바꾸려면:

```powershell
git config --global user.name "내 이름"
git config --global user.email "GitHub에 등록된 이메일"
```

## 8. 실습 ② 저장소 만들고 첫 커밋 (터미널 3)

프로젝트 루트(`agentlab` 폴더)로 돌아와서 시작해요.

```powershell
cd ..
git init -b main
git status
```

- `git init -b main`: 이 폴더를 Git 저장소로 만들고, 기본 브랜치 이름을 `main`으로 정해요.
- `git status`: 빨간 글씨는 아직 Git이 추적하지 않는 파일(Untracked)이에요.
  목록에 `.venv`, `node_modules`가 **없는** 걸 확인해 보세요. `.gitignore` 덕분이에요.

```powershell
git add -A
git status
```

초록 글씨로 바뀌면 스테이징된 거예요.

> `git add -A`는 어느 폴더에서 실행하든 저장소 전체의 변경을 담아요.
> `git add .`는 **현재 폴더 아래만** 담아서, 하위 폴더에서 실행하면 일부가 빠질 수 있어요.

```powershell
git commit -m "chore: 프로젝트 초기 구성 (FastAPI + React/TS)"
git log --oneline
```

첫 커밋 완성이에요.

### 커밋 메시지 규칙 (Conventional Commits)

`타입: 무엇을 했는지` 형식으로 써요. 히스토리가 깔끔해서 면접관이 보기에도 좋아요.

| 타입 | 언제 쓰나요 |
|---|---|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `docs` | 문서만 변경 |
| `test` | 테스트 추가, 수정 |
| `refactor` | 동작은 그대로 두고 코드 구조만 개선 |
| `chore` | 설정, 빌드, 의존성 같은 잡일 |

## 9. 실습 ③ GitHub에 올리기

1. https://github.com 로그인 → 오른쪽 위 `+` → **New repository**
2. Repository name은 `agentlab`, 공개 범위는 **Public**
3. **README, .gitignore, license 추가 옵션은 모두 선택하지 마세요.**
   이미 로컬에 있어서, 선택하면 첫 push에서 충돌이 나요.
4. **Create repository**를 누르고, 화면에 나오는 주소(`https://github.com/<아이디>/agentlab.git`)를 복사해요.

```powershell
git remote add origin https://github.com/<아이디>/agentlab.git
git push -u origin main
```

- `remote add origin`: GitHub 저장소를 `origin`이라는 이름으로 등록해요.
- `-u`: 연결을 기억해 둬서 다음부터는 `git push`만 쳐도 돼요.
- 처음 push할 때 브라우저 로그인 창이 뜨면 GitHub 계정으로 로그인하세요.

GitHub 페이지를 새로고침하면 README가 보여요.

## 10. 실습 ④ 수정 → 테스트 → 커밋 → 푸시 (직접 해보기)

### 과제 A: 백엔드 메시지 바꾸기 (테스트를 일부러 깨뜨려 보기)

1. `backend/app/main.py`의 메시지를 원하는 문구로 바꾸고 저장해요.
2. http://localhost:8000 을 새로고침해서 바뀐 메시지를 확인해요 (서버는 자동 재시작돼요).
3. 터미널 3에서 테스트를 돌려 보세요. **실패(FAILED)**할 거예요.
   ```powershell
   cd backend
   uv run pytest
   ```
   에러 메시지에서 기대값과 실제값이 어떻게 다른지 읽어 보세요.
4. `backend/tests/test_main.py`의 기대값도 고친 다음 다시 `uv run pytest` → 통과
5. 무엇이 바뀌었는지 확인해요.
   ```powershell
   git diff
   ```
6. 커밋하고 올려요.
   ```powershell
   git add -A
   git commit -m "feat: 루트 응답 메시지 변경"
   git push
   ```

### 과제 B: 프론트 제목 바꾸기 (이번엔 VS Code 화면으로 커밋)

1. `frontend/src/App.tsx`에서 `Get started`를 `AgentLab`으로 바꾸고 저장해요.
2. 브라우저(http://localhost:5173)가 **새로고침 없이** 바로 바뀌는 걸 확인해요 (HMR).
3. 이번엔 명령어 대신 VS Code **소스 제어 탭**(`Ctrl+Shift+G`)을 써 보세요.
   - 변경된 파일 옆 `+` 버튼 = `git add`
   - 위쪽 메시지 칸에 `feat: 첫 화면 제목 변경` 입력 → **커밋** 버튼 = `git commit`
   - **변경 내용 동기화** 버튼 = `git pull` + `git push`

### 과제 C: README 로드맵 체크

1. `README.md` 로드맵에서 `- [ ] 0.`을 `- [x] 0.`으로 바꿔요.
2. 원하는 방법(명령어 또는 VS Code)으로 `docs: 0단계 완료 표시` 커밋 → push

### 과제 D: 히스토리 구경하기

- 명령어로: `git log --oneline --graph`
- 그림으로: `Ctrl+Shift+P` → `Git Graph: View Git Graph`

## 11. 자주 쓰는 명령어

| 명령어 | 하는 일 |
|---|---|
| `git status` | 지금 상태 확인 (제일 자주 써요) |
| `git add -A` | 모든 변경을 스테이징 |
| `git add <파일>` | 특정 파일만 스테이징 |
| `git commit -m "메시지"` | 커밋 |
| `git push` | GitHub로 올리기 |
| `git pull` | GitHub의 최신 커밋 받아오기 |
| `git log --oneline` | 커밋 목록 |
| `git diff` | 아직 스테이징 안 한 변경 보기 |
| `git diff --staged` | 스테이징한 변경 보기 |
| `git restore --staged <파일>` | 스테이징만 취소 (수정 내용은 그대로) |
| `git restore <파일>` | 파일 수정을 마지막 커밋 상태로 되돌리기 (**되돌린 내용은 복구 안 돼요**) |

## 12. 완료 체크리스트

- [ ] http://localhost:8000/docs 가 열린다
- [ ] http://localhost:5173 이 열린다
- [ ] `uv run pytest`가 통과한다
- [ ] 과제 A에서 테스트가 실패하는 걸 직접 봤다
- [ ] GitHub 저장소에 커밋이 4개 이상 있다

막히면 에러 메시지를 통째로 복사해서 물어보세요.
다 끝나면 커밋 히스토리를 같이 보고 **1단계: 에이전트 CRUD API**로 넘어가요.
