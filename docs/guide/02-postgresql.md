# 2단계 (후반): PostgreSQL(Docker)로 바꾸기

**이번 단계 목표**

- 개발용 DB를 SQLite에서 **PostgreSQL**로 바꾼다 (Docker로 띄워요)
- 테스트도 PostgreSQL에서 돌린다 (테스트 전용 DB를 따로 써요)
- 시간 컬럼에 **시간대(timezone)** 까지 저장한다
- DB가 꺼져 있으면 헬스체크가 **503**을 준다
- 이번에도 브랜치 → PR → 리뷰 → merge

예상 시간: 하루 1~2시간 기준 4~5일 (Docker 설치 포함)

> **3번부터는 이 PC의 Docker로 직접 돌려 봤어요.**
> 빈칸을 순서대로 채우는 과정을 처음부터 끝까지 따라 해 보고, 단계마다 테스트 결과가 아래 적힌 대로 나오는지 확인했어요.

---

## 제가 미리 해 둔 것

- 브랜치 `feat/postgresql`을 만들었어요. 지금 이 브랜치에 있어요 (`git branch`로 확인).
- 이 PC를 확인해 봤어요. Windows 11 Pro, 64비트(AMD64), 메모리 31GB이고, BIOS에서 가상화도 켜져 있어요.
- 새 파일 2개를 만들었어요.
  - `compose.yaml` (프로젝트 맨 위): PostgreSQL 컨테이너 설정이에요 (빈칸 있음).
  - `docker/postgres-init/create-test-db.sql`: 테스트 전용 DB를 만드는 SQL이에요.
- `backend/.env.example`의 DB 주소를 PostgreSQL로 바꿨어요.
- 코드 파일 9개에 빈칸 템플릿을 넣었어요. `[2단계 4-2]`처럼 번호가 붙어 있어요.
- 확인하면서 PostgreSQL 18 이미지를 받아 뒀어요. 그래서 3번의 `docker compose up -d`가 금방 끝나요.

**지금 상태**: `uv run pytest` → **30 passed**, `uv run ruff check .` → **All checks passed!**
(템플릿은 전부 주석이라서 아직 아무것도 안 바뀌었어요.)

### 빈칸 채우기 방법 (전반과 같아요)

- `Ctrl+Shift+F`로 `[2단계 4-2]`처럼 번호가 붙은 안내 줄을 찾아요.
- 주석 풀기는 `Ctrl+/`, 줄 지우기는 `Ctrl+Shift+K`, 저장은 `Ctrl+S`예요.
- **저장하면 VS Code가 import 순서와 줄 맞춤을 알아서 정리해요.** 그래서 import 주석을 아무 데서나 풀어도 괜찮아요.
- 다 채운 안내 줄(`[2단계 ...]`)은 지워요.
- 막히면 단계 맨 아래 **정답 보기**를 눌러요.

### 전체 그림

```text
 내 PC                                         Docker 컨테이너 (db)
 ─────────────────────                         ──────────────────────────────
 uv run fastapi dev   ─┐                       PostgreSQL 18
 uv run alembic ...   ─┼──▶ 127.0.0.1:5432 ──▶   ├─ DB agentlab       (개발용)
 uv run pytest        ─┘                         └─ DB agentlab_test  (테스트용)
                                               데이터는 볼륨(pgdata)에 저장돼요
```

---

## 0. 왜 PostgreSQL로 바꿀까요?

지금까지 쓴 SQLite는 파일 하나로 된 DB예요. 설치가 필요 없어서 연습하기 좋아요.
그런데 실제 서비스에서는 PostgreSQL 같은 **DB 서버**를 많이 써요.

문제는 SQLite가 **규칙을 느슨하게 지킨다**는 거예요. 우리 마이그레이션으로 만든 테이블에 직접 넣어 봤어요.

| 해 본 것 | SQLite | PostgreSQL |
|---|---|---|
| `name`은 `VARCHAR(100)`인데 150글자 넣기 | 그냥 저장돼요 (길이 150) | 에러: `value too long for type character varying(100)` |
| `max_steps`는 `INTEGER`인데 `'abc'` 넣기 | 그냥 저장돼요 (글자로) | 에러: `invalid input syntax for type integer: "abc"` |
| `created_at`에 한국 시간 `09:00+09:00` 넣기 | `09:00`만 남고 `+09:00`은 사라져요 | 시간대까지 저장하는 타입(`timestamptz`)이 있어요 (6번에서 바꿔요) |

API로 넣을 때는 Pydantic이 앞에서 막아 줘서(422) 이런 일이 잘 안 생겨요.
하지만 DB도 같은 규칙을 지켜야 실수를 끝까지 막을 수 있어요.

> **그래서 개발과 테스트도 운영과 같은 DB로 해요.**
> SQLite에서 통과한 테스트가 PostgreSQL에서는 실패할 수 있거든요.

---

## 1. Docker가 뭐예요?

PostgreSQL을 Windows에 직접 설치할 수도 있어요 (Oracle을 설치하던 것처럼요).
하지만 요즘은 **Docker**로 띄우는 경우가 많아요.

- 설치 프로그램 없이 명령 한 줄로 켜고, 지우고, 다시 만들 수 있어요.
- 버전(예: PostgreSQL 18)을 파일에 적어 두면, 다른 PC에서도 똑같은 DB가 떠요. 7단계의 GitHub Actions도 이 방식을 써요.
- PC에 이것저것 설치되지 않아서 깔끔해요.

### 용어 4개만 알면 돼요

| 용어 | 뜻 | Java로 비유하면 |
|---|---|---|
| 이미지 (image) | 프로그램과 실행 환경을 통째로 묶은 꾸러미예요. 예: `postgres:18` | 클래스 (설계도) |
| 컨테이너 (container) | 이미지를 실행한 것이에요. 같은 이미지로 여러 개 띄울 수 있어요 | `new`로 만든 객체 |
| 볼륨 (volume) | 컨테이너를 지워도 남는 저장 공간이에요. DB 데이터를 여기에 둬요 | (비유 없음) 외장 하드라고 생각하면 돼요 |
| 포트 연결 | 내 PC의 5432번 포트를 컨테이너 안의 5432번 포트로 이어 줘요. 그래서 앱은 내 PC에 PostgreSQL이 설치된 것처럼 접속해요 | (비유 없음) |

### 설치할 프로그램 2개

| 설치할 것 | 하는 일 |
|---|---|
| WSL 2 | Windows 안에서 Linux를 돌리는 Windows 기능이에요. Docker 컨테이너는 Linux 위에서 돌아서 이게 필요해요. |
| Docker Desktop | Windows에서 Docker를 쓰게 해 주는 프로그램이에요. `docker` 명령도 같이 설치돼요. |

---

## 2. 설치하기 (30분~1시간, 재부팅 1번)

### 2-1. WSL 설치

1. `Win + X` → **터미널(관리자)** 을 눌러요. "이 앱이 디바이스를 변경하도록 허용하시겠어요?"가 나오면 **예**.
   (VS Code 터미널은 관리자 권한이 아니라서 여기서는 안 돼요.)
2. 아래 명령을 실행해요.

   ```powershell
   # WSL을 설치해요.
   # --no-distribution: Ubuntu 같은 Linux는 설치하지 않아요. Docker는 자기 Linux를 따로 써서 지금은 필요 없어요.
   wsl --install --no-distribution
   ```

3. 끝나면 **PC를 재부팅**해요. 재부팅하라는 말이 안 나와도 한 번 해 주세요.
4. 재부팅한 뒤 터미널(이번엔 관리자 아니어도 돼요)에서 확인해요.

   ```powershell
   # 설치된 WSL 버전을 보여줘요.
   wsl --version
   ```

   `WSL 버전: 3.0.3.0`처럼 버전이 나오면 성공이에요.

### 2-2. Docker Desktop 설치

1. https://www.docker.com/products/docker-desktop/ 에서 **Download for Windows – AMD64**를 눌러 설치 파일을 받아요. 용량이 커서 몇 분 걸려요.
2. 받은 `Docker Desktop Installer.exe`를 실행해요.
3. 설정 화면에서 **Use WSL 2 instead of Hyper-V (recommended)** 가 체크된 그대로 **OK**를 눌러요.
4. 설치가 끝나면 **Close**. 로그아웃하라고 나오면 로그아웃했다가 다시 로그인해요.
5. 시작 메뉴에서 **Docker Desktop**을 실행해요.
   - 처음 실행하면 **이용 약관**(Docker Subscription Service Agreement)이 나와요. 읽어 보고 직접 결정해서 **Accept**를 눌러요. 개인 공부와 포트폴리오는 무료로 쓸 수 있어요.
   - 로그인 화면은 **Skip**해도 돼요. 설문도 건너뛰어도 돼요.
6. 창 왼쪽 아래에 초록색 **Engine running**이 보이면 준비 끝이에요.

> Docker Desktop이 **켜져 있어야** `docker` 명령이 동작해요. 작업 표시줄 오른쪽 아래에 고래 아이콘이 있으면 켜져 있는 거예요.
> 매번 켜기 번거로우면 Settings → General → **Start Docker Desktop when you sign in to your computer**를 체크해요.

### 2-3. 잘 설치됐는지 확인하기

먼저 **VS Code를 완전히 껐다가 다시 켜요.** 설치 전에 열어 둔 터미널은 `docker` 명령을 몰라요.

```powershell
# Docker 버전을 보여줘요. Client와 Server가 둘 다 나와야 해요.
docker version
```

```powershell
# docker compose: 컨테이너 설정을 파일 하나(compose.yaml)에 적어 두고 관리하는 기능이에요. 3번에서 써요.
docker compose version
```

```powershell
# 연습용 이미지(hello-world)를 받아서 컨테이너로 한 번 실행해요.
# --rm: 실행이 끝나면 컨테이너를 자동으로 지워요.
docker run --rm hello-world
```

`Hello from Docker!`가 보이면 설치 성공이에요. 처음에는 이미지를 받느라 몇 초 걸려요.

### 2-4. 자주 만나는 문제

| 증상 | 원인 | 해결 |
|---|---|---|
| `wsl --install`에서 관리자 권한(권한 상승)이 필요하다고 나와요 | 관리자 터미널이 아니에요 | `Win + X` → **터미널(관리자)** 에서 다시 해요 |
| `--no-distribution`을 모르는 옵션이라고 나와요 | WSL이 오래된 버전이에요 | `wsl --install`만 쳐요. 재부팅 후 Ubuntu 사용자 이름과 비밀번호를 물으면 아무거나 정해요 (Docker와는 상관없어요) |
| `'docker' 용어가 ... 인식되지 않습니다` (영어로는 `The term 'docker' is not recognized`) | 설치 전에 연 터미널이에요 | VS Code를 완전히 껐다 켜요 |
| `docker version`에서 Server 대신 `error during connect`로 시작하는 에러가 나와요 | Docker Desktop이 꺼져 있거나 아직 켜지는 중이에요 | Docker Desktop을 켜고 **Engine running**을 기다려요 |
| Docker Desktop이 WSL을 업데이트하라고 해요 | WSL이 오래됐어요 | 관리자 터미널에서 `wsl --update` |

---

## 3. PostgreSQL 띄우기

**명령은 프로젝트 맨 위 폴더(`C:\agentlab`)에서** 실행해요. `compose.yaml`이 거기 있어요.
(`backend` 폴더에서 쳐도 돼요. Docker가 위 폴더의 `compose.yaml`을 찾아 줘요.)

### 3-1. compose.yaml 읽고 빈칸 채우기

**파일**: `compose.yaml` (프로젝트 맨 위)

모든 줄에 설명 주석이 있어요. 위에서부터 천천히 읽고, `____` 두 군데를 채워요.

#### 쉽게 말하면

```text
"postgres:18 이미지로 db라는 컨테이너를 하나 띄워 줘.
 사용자, 비밀번호, DB 이름은 모두 agentlab으로 만들고,
 내 PC의 5432번 포트로 접속할 수 있게 하고,
 데이터는 pgdata 볼륨에 보관해 줘."
```

#### 새로 나온 것

| 키 | 뜻 |
|---|---|
| `services` | 띄울 컨테이너 목록이에요 |
| `image` | 어떤 이미지로 띄울지예요. `이름:버전` 형식이에요 |
| `environment` | 컨테이너 안의 환경 변수예요. postgres 이미지는 이 값으로 사용자와 DB를 만들어요 |
| `ports` | `"내 PC 주소:내 PC 포트:컨테이너 포트"`예요 |
| `volumes` | 컨테이너 밖에 두는 저장 공간이에요. 컨테이너를 지워도 데이터가 남아요 |
| `healthcheck` | Docker가 "DB가 접속을 받을 준비가 됐는지" 몇 초마다 확인하는 방법이에요 |

<details>

<summary>정답 보기</summary>

```yaml
    image: postgres:18
```

```yaml
    ports:
      - "127.0.0.1:5432:5432"
```

</details>

### 3-2. 테스트 DB를 만드는 SQL 읽기 (빈칸 없음)

**파일**: `docker/postgres-init/create-test-db.sql`

```sql
CREATE DATABASE agentlab_test;
```

`compose.yaml`에서 이 폴더를 컨테이너의 `/docker-entrypoint-initdb.d`에 붙였어요.
postgres 이미지는 **DB를 처음 만들 때만** 이 폴더의 `.sql` 파일을 실행해요. 그래서 처음 띄우면 DB가 2개 생겨요.

| DB 이름 | 누가 만들어요 | 어디에 써요 |
|---|---|---|
| `agentlab` | `compose.yaml`의 `POSTGRES_DB` | 개발용 (서버를 켜면 쓰는 DB) |
| `agentlab_test` | 이 SQL 파일 | 테스트용 (5번부터 써요) |

### 3-3. 띄우기

```powershell
# compose.yaml에 적힌 컨테이너를 띄워요.
# -d: 뒤에서(백그라운드로) 돌려요. 터미널은 바로 돌아와요.
docker compose up -d
```

`Container agentlab-db-1 Started`가 보이면 돼요.

```powershell
# 지금 떠 있는 컨테이너의 상태를 보여줘요.
docker compose ps
```

```text
NAME            IMAGE         ...   STATUS                   PORTS
agentlab-db-1   postgres:18   ...   Up 5 seconds (healthy)   127.0.0.1:5432->5432/tcp
```

STATUS에 `(healthy)`가 보이면 준비 끝이에요. `(health: starting)`이면 몇 초 뒤에 다시 쳐 봐요.

### 3-4. psql로 들어가 보기

psql은 PostgreSQL에 SQL을 보내는 터미널 프로그램이에요 (Oracle의 SQL*Plus 같은 거예요).
컨테이너 안에 들어 있어서 따로 설치할 필요가 없어요.

```powershell
# docker compose exec db: db 컨테이너 안에서 명령을 실행해요.
# psql -U agentlab: agentlab 사용자로 psql을 실행해요.
# -c "...": 이 SQL 하나만 실행하고 끝내요.
docker compose exec db psql -U agentlab -c "SELECT datname FROM pg_database ORDER BY datname;"
```

```text
    datname
---------------
 agentlab
 agentlab_test
 postgres
 template0
 template1
(5 rows)
```

`agentlab`과 `agentlab_test`가 보이면 성공이에요. 나머지 3개는 PostgreSQL이 원래 갖고 있는 DB예요.

### 3-5. 자주 쓰는 명령

| 명령 | 하는 일 | 데이터 |
|---|---|---|
| `docker compose up -d` | 컨테이너를 만들고 켜요 (이미 있으면 켜기만 해요) | 그대로 |
| `docker compose ps` | 상태를 봐요 | 그대로 |
| `docker compose logs db` | db 컨테이너의 로그를 봐요 | 그대로 |
| `docker compose stop` | 꺼요 | 그대로 |
| `docker compose start` | 다시 켜요 | 그대로 |
| `docker compose down` | 컨테이너를 지워요 | 그대로 (볼륨은 남아요) |
| `docker compose down -v` | 컨테이너와 볼륨을 같이 지워요 | **사라져요** |

> PC를 다시 켜면 Docker Desktop을 먼저 켜고, `docker compose up -d`를 쳐요.

**커밋**: `chore: Docker Compose로 PostgreSQL 띄우기`
(`compose.yaml`, `docker/postgres-init/create-test-db.sql`, `docs/guide/02-postgresql.md`)

---

## 4. 앱을 PostgreSQL에 연결하기

여기서부터 **명령은 모두 `backend` 폴더에서** 실행해요.

```powershell
cd backend
```

### 4-1. PostgreSQL 드라이버 설치하기

```powershell
# psycopg: Python에서 PostgreSQL에 접속하게 해 주는 드라이버예요. (Java의 PostgreSQL JDBC 드라이버 같은 거예요)
# [binary]: 미리 만들어 둔 버전이라 설치가 쉬워요.
uv add "psycopg[binary]"
```

```text
 + psycopg==3.3.8
 + psycopg-binary==3.3.8
 + tzdata==2026.6
```

`pyproject.toml`의 `dependencies`에 `psycopg[binary]`가 추가되고, `uv.lock`도 바뀌어요.
(`tzdata`는 Windows에서 시간대 정보를 쓰려고 같이 설치돼요.)

### 4-2. DB 주소 바꾸기

**파일**: `backend/app/config.py`

`[2단계 4-2]` 바로 아래의 SQLite 주소 줄을 지우고, 그 밑의 주석을 풀어서 `____` 두 군데를 채워요.

DB 주소는 앞에서부터 이렇게 읽어요. 값은 `compose.yaml`과 맞춰요.

| 부분 | 뜻 | compose.yaml에서 |
|---|---|---|
| `postgresql+psycopg://` | PostgreSQL에 psycopg 드라이버로 접속해요 (JDBC URL의 `jdbc:postgresql://`) | |
| `agentlab:agentlab@` | `사용자:비밀번호@` | `POSTGRES_USER`, `POSTGRES_PASSWORD` |
| `127.0.0.1:____` | `주소:포트` | `ports`의 가운데 숫자 |
| `/____` | DB 이름 | `POSTGRES_DB` |
| `?connect_timeout=5` | DB가 꺼져 있으면 5초만 기다리고 포기해요 | |

> **왜 `localhost`가 아니라 `127.0.0.1`이에요?**
> 둘 다 "내 PC 자신"이라는 뜻이에요. 그런데 이 PC에서 재 보니, `localhost`로 쓰면 접속이 **10초 넘게 멈췄다가** 붙었어요.
> Windows가 IPv6 주소(`::1`)로 먼저 접속해 보다가 기다리기 때문이에요. `127.0.0.1`은 바로(0.0초) 붙었어요.
>
> **`connect_timeout=5`는 왜 넣어요?**
> 이 PC에서는 DB가 꺼져 있을 때 접속이 바로 거절되지 않고 계속 기다려요. 이 옵션이 없으면 **2분 넘게** 멈춰 있다가 에러가 났어요.
> 주소에 넣어 두면 서버, 테스트, Alembic이 모두 이 설정을 따라요.

<details>
<summary>정답 보기</summary>

```python
    # 개발용 DB 주소예요. 형식: "드라이버://사용자:비밀번호@주소:포트/DB이름?옵션"
    # 127.0.0.1: 내 PC 자신이에요. localhost라고 쓰면 Windows에서 한참 멈출 수 있어요.
    # connect_timeout=5: DB가 꺼져 있으면 5초만 기다리고 포기해요.
    database_url: str = (
        "postgresql+psycopg://agentlab:agentlab@127.0.0.1:5432/agentlab?connect_timeout=5"
    )
```

`( )`는 줄이 너무 길어서 나눠 쓰려고 넣은 거예요. `database_url: str = "..."` 한 줄과 똑같아요.
(한 줄로 써도 저장하면 VS Code가 이렇게 바꿔 줘요.)

</details>

**확인**: `uv run pytest` → **30 passed**. 테스트는 아직 SQLite 메모리 DB를 써요. 5번에서 바꿔요.

### 4-3. PostgreSQL에 마이그레이션 적용하기

전반에 만든 마이그레이션 파일 2개를 PostgreSQL에 그대로 실행해요. SQLite용으로 따로 만든 게 아니라서 그대로 돼요.

```powershell
# 개발용 DB(agentlab)에 마이그레이션을 끝까지 실행해요.
uv run alembic upgrade head
```

```text
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> b0d8ca8c436e, create agents table
INFO  [alembic.runtime.migration] Running upgrade b0d8ca8c436e -> 087b239f2c96, add max_steps to agents
```

`Context impl PostgresqlImpl`은 이번엔 PostgreSQL에 접속했다는 뜻이에요. 전에는 `SQLiteImpl`이었어요.

```powershell
uv run alembic current
```

→ `087b239f2c96 (head)`

```powershell
uv run alembic check
```

→ `No new upgrade operations detected.`

중간에 `Detected sequence named 'agents_id_seq' ... assuming SERIAL and omitting`이 보여도 괜찮아요.
PostgreSQL이 id 번호를 매기는 방식(시퀀스)을 Alembic이 알아봤다는 안내예요.

### 4-4. 테이블 직접 보기

```powershell
# -d agentlab: agentlab DB에 접속해요.
# \d agents: agents 테이블의 구조를 보여줘요. (Oracle의 DESC agents와 같아요)
docker compose exec db psql -U agentlab -d agentlab -c "\d agents"
```

```text
    Column     |            Type             | Collation | Nullable |              Default
---------------+-----------------------------+-----------+----------+------------------------------------
 id            | integer                     |           | not null | nextval('agents_id_seq'::regclass)
 name          | character varying(100)      |           | not null |
 description   | character varying(500)      |           |          |
 model         | character varying(100)      |           | not null |
 system_prompt | text                        |           | not null |
 temperature   | double precision            |           | not null |
 created_at    | timestamp without time zone |           | not null | CURRENT_TIMESTAMP
 updated_at    | timestamp without time zone |           | not null | CURRENT_TIMESTAMP
 max_steps     | integer                     |           | not null | 5
```

`created_at`이 `timestamp without time zone`(시간대 없음)인 걸 기억해 두세요. 6번에서 바꿔요.

#### 0번의 잘못된 값을 PostgreSQL에도 넣어 보기

```powershell
docker compose exec db psql -U agentlab -d agentlab -c "INSERT INTO agents (name, model, system_prompt, temperature) VALUES (repeat('x', 150), 'mock', 'p', 0.7);"
```

```text
ERROR:  value too long for type character varying(100)
```

SQLite는 그냥 저장했던 값을 PostgreSQL은 막아요.

### 4-5. 서버로 확인하기

```powershell
uv run fastapi dev app/main.py
```

http://localhost:8000/docs 에서 `POST /api/agents`로 에이전트를 하나 만들어요. 그다음 **다른 터미널**에서 확인해요.

```powershell
docker compose exec db psql -U agentlab -d agentlab -c "SELECT id, name, max_steps, created_at FROM agents;"
```

```text
 id | name  | max_steps |         created_at
----+-------+-----------+----------------------------
  1 | alpha |         5 | 2026-11-07 00:54:49.334043
(1 row)
```

방금 만든 에이전트가 PostgreSQL에 들어 있으면 성공이에요.

> 이제 `backend/agentlab.db`(SQLite 파일)는 안 써요. 지워도 돼요. `.gitignore`에 있어서 Git과는 상관없어요.

**커밋**: `feat: 개발 DB를 PostgreSQL로 전환`
(`pyproject.toml`, `uv.lock`, `app/config.py`, `.env.example`)

---

## 5. 테스트도 PostgreSQL에서 돌리기

지금 테스트는 SQLite 메모리 DB에서 돌아요. 0번에서 본 것처럼 SQLite는 규칙이 느슨해서, 테스트가 통과해도 PostgreSQL에서는 실패할 수 있어요.
그래서 테스트도 PostgreSQL로 바꿔요. 단, **개발용 DB(`agentlab`)는 건드리지 않아요.** 3-2에서 만든 테스트 전용 DB(`agentlab_test`)를 써요.

### 이렇게 바뀌어요

| | 지금 (SQLite) | 바뀐 뒤 (PostgreSQL) |
|---|---|---|
| DB | 테스트마다 새 메모리 DB | `agentlab_test` 하나를 같이 써요 |
| 테이블 만들기 | 테스트마다 `create_all` | 테스트를 시작할 때 **한 번**, 마이그레이션(`upgrade head`)으로 |
| 테스트끼리 섞이지 않게 | DB를 매번 새로 만들어요 | 테스트 하나가 끝날 때마다 `TRUNCATE`로 테이블을 비워요 |

테이블을 `create_all`이 아니라 **마이그레이션으로** 만드는 게 중요해요. 운영 DB를 만드는 방법과 똑같아지거든요.

### 5-1. 테스트 DB 주소 추가하기

**파일**: `backend/app/config.py`

`[2단계 5-1]`의 주석을 풀고 `____`를 채워요.

<details>
<summary>정답 보기</summary>

```python
    # 테스트 전용 DB 주소예요. 테스트는 이 DB를 매번 비우고 다시 만들어요.
    test_database_url: str = (
        "postgresql+psycopg://agentlab:agentlab@127.0.0.1:5432/agentlab_test?connect_timeout=5"
    )
```

</details>

### 5-2. conftest.py 바꾸기

**파일**: `backend/tests/conftest.py`

파일이 두 부분으로 나뉘어 있어요.

1. **위쪽**: 지금 쓰는 SQLite 버전이에요. `[2단계 5-2] 이 줄부터` 줄부터 `[2단계 5-2] 여기까지 지워요.` 줄까지 **전부 지워요.**
2. **아래쪽**: 새 버전이에요. 주석을 **모두 풀고** `____` 네 군데를 채워요.
   (아래쪽 첫 줄을 클릭 → `Ctrl+Shift+End`로 끝까지 선택 → `Ctrl+/`)

#### 새로 나온 것

| 코드 | 뜻 |
|---|---|
| `@pytest.fixture(scope="session")` | 테스트 전체에서 **한 번만** 실행해요. 아무것도 안 쓰면 테스트마다 한 번이에요 |
| `autouse=True` | 테스트 함수가 인자로 안 받아도 자동으로 실행해요 |
| `db_engine(alembic_config: Config)` | fixture도 다른 fixture를 인자로 받아요 (Spring의 생성자 주입처럼) |
| `make_url(주소).database` | 주소에서 DB 이름만 꺼내요. 예: `agentlab_test` |
| `DROP SCHEMA public CASCADE` | public 스키마(테이블이 들어 있는 기본 폴더)를 안에 든 것까지 전부 지워요 |
| `engine.begin()` | 블록이 끝나면 자동으로 commit해요 (`@Transactional`처럼) |
| `TRUNCATE agents RESTART IDENTITY` | 테이블을 비우고, id 번호도 1부터 다시 시작해요 |

> **`_test` 검사는 왜 있어요?**
> 이 fixture는 DB를 통째로 비워요. 누가 실수로 테스트 DB 주소를 개발용 DB로 바꾸면, 개발 데이터가 다 사라져요.
> 그래서 이름이 `_test`로 끝나는 DB가 아니면 바로 멈추게 했어요.

<details>
<summary>정답 보기</summary>

```python
@pytest.fixture(scope="session")
def alembic_config() -> Config:
```

```python
@pytest.fixture(scope="session", autouse=True)
def db_engine(alembic_config: Config) -> Iterator[Engine]:
```

```python
    command.upgrade(alembic_config, "head")
```

```python
        connection.execute(text("TRUNCATE agents RESTART IDENTITY"))
```

</details>

**확인**: `uv run pytest` → **30 passed**. 마이그레이션 테스트(`test_migrations.py`)는 아직 임시 SQLite 파일을 써요. 5-3에서 바꿔요.

### 5-3. test_migrations.py 바꾸기

**파일**: `backend/tests/test_migrations.py`

5-2와 같은 방법이에요. 위쪽(`이 줄부터` ~ `여기까지 지워요.`)을 지우고, 아래쪽 주석을 풀어서 `____` 두 군데를 채워요.

이제 `make_config(tmp_path)` 대신 conftest.py의 `alembic_config` fixture를 받아서 써요. 검사는 테스트 DB(`agentlab_test`)에서 해요.
`ALEMBIC_INI` 줄은 conftest.py로 옮겨 갔어요.

<details>
<summary>정답 보기</summary>

```python
def test_migrations_match_models(alembic_config: Config) -> None:
```

```python
def test_migrations_can_downgrade_and_upgrade_again(alembic_config: Config) -> None:
```

</details>

### 5-4. 돌려 보기

```powershell
uv run pytest
```

→ **30 passed** (1초쯤 걸려요). 한 번 더 쳐도 **30 passed**예요. 시작할 때마다 테스트 DB를 비우고 다시 만들기 때문이에요.

테스트 DB를 직접 들여다볼 수도 있어요.

```powershell
docker compose exec db psql -U agentlab -d agentlab_test -c "SELECT version_num FROM alembic_version;"
```

→ `087b239f2c96`. 테스트 DB도 마이그레이션으로 만들어져서 책갈피가 있어요.

> **Docker를 안 켜고 테스트를 돌리면** 10초쯤 뒤에 `30 errors`와 `connection timeout expired`가 나와요.
> 그럴 땐 Docker Desktop을 켜고 `docker compose up -d`를 먼저 쳐요.

**커밋**: `test: 테스트를 PostgreSQL 테스트 DB에서 실행`
(`app/config.py`, `tests/conftest.py`, `tests/test_migrations.py`)

---

## 6. 시간에 시간대 넣기

### 왜 필요해요?

지금 `created_at`에는 `2026-11-07 00:54:49`처럼 **시간대 없이** 저장돼요.
이게 한국 시간 0시 54분인지, 세계 표준시(UTC) 0시 54분인지 값만 봐서는 알 수 없어요.
(실제로는 UTC예요. Docker의 PostgreSQL은 기본 시간대가 UTC예요.)

PostgreSQL의 `timestamptz`(timestamp with time zone)는 **정확히 어느 순간인지**를 저장해요. 꺼낼 때 시간대도 같이 붙여 줘요.

이번엔 **테스트부터** 써요. 1단계에서 해 본 TDD예요.

### 6-1. 테스트 먼저 쓰기

**파일**: `backend/tests/test_agents.py`

`[2단계 6-1]`이 두 군데예요.

- 맨 위: `from datetime import datetime` 주석을 풀어요.
- 맨 아래: 테스트 주석을 풀고 `____`를 채워요.

| 코드 | 뜻 |
|---|---|
| `datetime.fromisoformat("2026-...Z")` | 글자로 된 시간을 `datetime` 객체로 바꿔요 (Java의 `OffsetDateTime.parse`) |
| `created_at.tzinfo` | 시간대 정보예요. 시간대가 없으면 `None`이에요 |

<details>
<summary>정답 보기</summary>

```python
    assert created_at.tzinfo is not None
```

</details>

```powershell
uv run pytest
```

→ **1 failed, 30 passed**가 정상이에요.

```text
E       assert None is not None
E        +  where None = datetime.datetime(2026, 11, 7, 0, 55, 7, 233233).tzinfo
```

지금은 시간대가 없어서(`tzinfo`가 `None`) 실패해요.

### 6-2. 모델 바꾸기

**파일**: `backend/app/models/agent.py`

`[2단계 6-2]`가 두 군데예요.

- import 아래: `from sqlalchemy import DateTime` 주석을 풀고 저장해요.
  VS Code가 위의 import와 합쳐서 `from sqlalchemy import DateTime, String, Text, func`로 만들어 줘요.
- 맨 아래: 지금 있는 `created_at`, `updated_at` 두 줄을 지우고, 그 밑의 주석을 풀어서 `____` 두 군데를 채워요.

<details>
<summary>정답 보기</summary>

```python
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
```

</details>

```powershell
uv run pytest
```

→ **2 failed, 29 passed**가 정상이에요. 실패가 하나 늘었죠?

```text
E   alembic.util.exc.AutogenerateDiffsDetected: New upgrade operations detected: [[('modify_type', None, 'agents', 'created_at', ...
```

마이그레이션 검사 테스트가 "모델은 바뀌었는데 마이그레이션 파일이 없어요"라고 알려 줘요.

> **SQLite였다면 이 실패가 안 나와요.**
> SQLite에는 시간대 타입이 없어서, 모델을 바꿔도 DB 쪽은 똑같아 보여요.
> 같은 모델로 SQLite에서 `alembic check`를 돌려 보니 `No new upgrade operations detected.`가 나왔어요.
> 테스트를 PostgreSQL로 바꾼 덕분에 잡은 거예요.

### 6-3. 마이그레이션 만들기

```powershell
uv run alembic revision --autogenerate -m "use timezone aware timestamps"
```

```text
INFO  [alembic.autogenerate.compare.types] Detected type change from TIMESTAMP() to DateTime(timezone=True) on 'agents.created_at'
INFO  [alembic.autogenerate.compare.types] Detected type change from TIMESTAMP() to DateTime(timezone=True) on 'agents.updated_at'
  Generating ...\alembic\versions\xxxx_use_timezone_aware_timestamps.py ...  done
```

생긴 파일을 열어 보세요. `xxxx`는 만들 때마다 달라지는 번호예요.

```python
def upgrade() -> None:
    with op.batch_alter_table('agents', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=postgresql.TIMESTAMP(),   # 지금 타입: 시간대 없음
               type_=sa.DateTime(timezone=True),        # 바꿀 타입: 시간대 있음
               existing_nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
        batch_op.alter_column('updated_at', ...)        # updated_at도 똑같아요
```

`downgrade()`는 반대로 `DateTime(timezone=True)`를 `TIMESTAMP()`로 되돌려요. 실제로 실행되는 SQL은 이거예요.

```sql
ALTER TABLE agents ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE;
ALTER TABLE agents ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE;
```

```powershell
uv run pytest
```

→ **31 passed**

> **개발용 DB에는 아직 적용 안 했는데 왜 통과해요?**
> 테스트는 시작할 때 **마이그레이션 파일로** 테스트 DB를 새로 만들어요. 새 파일이 생겼으니 테스트 DB에는 벌써 반영된 거예요.

### 6-4. 개발용 DB에도 적용하기

```powershell
uv run alembic upgrade head
```

→ `Running upgrade 087b239f2c96 -> xxxx, use timezone aware timestamps`

이미 있던 행의 시간은 UTC로 읽어서 바꿔요. Docker의 PostgreSQL이 원래 UTC로 저장했으니 값은 그대로예요.

서버를 켜고 /docs에서 `GET /api/agents`를 실행해 보면 시간 끝에 `Z`가 붙어 있어요.

```text
"created_at": "2026-11-07T00:54:49.334043Z"
```

`Z`는 UTC라는 뜻이에요. 한국 시간은 여기에 9시간을 더하면 돼요 (오전 9시 54분). 3단계 화면에서 한국 시간으로 바꿔 보여 줄 거예요.

**커밋**: `feat: 시간 컬럼에 시간대 저장`
(`app/models/agent.py`, `alembic/versions/xxxx_use_timezone_aware_timestamps.py`, `tests/test_agents.py`)

---

## 7. DB가 꺼지면 헬스체크가 503 주기

지금 `GET /api/health`는 DB가 꺼져 있으면 **500**(서버 내부 에러)이 나요.
하지만 서버 코드가 고장 난 게 아니라, DB에 연결이 안 되는 거예요. 이럴 때 쓰는 상태 코드가 **503 Service Unavailable**("지금은 서비스를 못 해요")이에요.
서버를 지켜보는 프로그램(7단계의 Docker, 클라우드 등)은 이 응답을 보고 "DB 문제구나"를 알아요.

이번에도 테스트부터 써요.

### 7-1. 테스트 먼저 쓰기

**파일**: `backend/tests/test_health.py`

`[2단계 7-1]`이 두 군데예요.

- import 아래: 주석 4줄을 풀고 저장해요. VS Code가 import 순서를 정리해 줘요.
- 맨 아래: 주석을 풀고 `____`를 채워요.

테스트하려고 진짜 DB를 끌 수는 없어요. 그래서 **무조건 "연결 안 됨" 예외를 던지는 가짜 세션**(`BrokenSession`)을 만들어 끼워요.
conftest.py에서 `get_session`을 테스트 DB 세션으로 바꿔 끼운 것과 같은 방법이에요 (Spring의 `@MockBean`).

<details>
<summary>정답 보기</summary>

```python
    assert response.status_code == 503
```

</details>

```powershell
uv run pytest
```

→ **1 failed, 31 passed**가 정상이에요.

```text
E       sqlalchemy.exc.OperationalError: (builtins.Exception) DB is down
```

지금은 아무도 예외를 잡지 않아서, 503 대신 예외가 그대로 터져요.

### 7-2. 에러 클래스 만들기

**파일**: `backend/app/errors.py`

`[2단계 7-2]`의 주석을 풀고 `____`를 채워요.

`NotFoundError`(404), `ConflictError`(409)와 같은 모양이에요. `AppError`를 상속하면 `register_error_handlers`가 알아서 `{"detail": "메시지"}` 응답으로 바꿔 줘요.

<details>
<summary>정답 보기</summary>

```python
class ServiceUnavailableError(AppError):
    status_code = 503
```

</details>

### 7-3. 헬스체크 고치기

**파일**: `backend/app/api/health.py`

`[2단계 7-3]`이 두 군데예요.

- import 아래: 주석 2줄을 풀고 저장해요.
- 함수 안: 지금 있는 `session.execute(...)` 줄을 지우고, 그 밑의 주석을 풀어서 `____` 두 군데를 채워요.

`agent_service.py`의 `_commit_or_conflict`와 같은 모양이에요.

```python
    except IntegrityError as e:  # agent_service.py
        raise ConflictError(f"Agent name already exists: {name}") from e
```

<details>
<summary>정답 보기</summary>

```python
    try:
        session.execute(text("SELECT 1"))
    # OperationalError: DB에 연결이 안 될 때 나는 예외예요. (DB가 꺼져 있을 때 등)
    except OperationalError as e:
        raise ServiceUnavailableError("Database is unavailable") from e
```

</details>

```powershell
uv run pytest
```

→ **32 passed**

### 7-4. 진짜로 DB를 꺼 보기

서버를 켜 둔 채로(`uv run fastapi dev app/main.py`), **다른 터미널**에서 해요.

1. /docs에서 `GET /api/health` → **200**
2. DB를 꺼요.

   ```powershell
   docker compose stop
   ```

3. `GET /api/health` → **503** `{"detail": "Database is unavailable"}`
4. DB를 다시 켜요.

   ```powershell
   docker compose start
   ```

5. `GET /api/health` → 다시 **200**

이번엔 **꺼진 동안 요청을 하나도 안 보내고** 다시 켜는 경우예요.

1. `GET /api/agents` → **200**
2. DB를 재시작해요.

   ```powershell
   docker compose restart
   ```

3. `docker compose ps`에 `(healthy)`가 보이면 `GET /api/agents` → **500**이 나와요!
4. 한 번 더 → **200**

왜 그럴까요? 서버는 DB 연결을 미리 만들어 두고 **다시 써요**(커넥션 풀). Spring의 DataSource가 연결을 모아 두고 다시 쓰는 것과 같아요.
DB가 재시작하면 모아 둔 연결은 끊어져요. 그런데 서버는 그걸 모르고 썼다가 실패하고, 그다음에야 새로 연결해요.

### 7-5. pool_pre_ping 켜기

**파일**: `backend/app/db.py`

`[2단계 7-5]` 바로 아래 `engine` 줄을 지우고, 그 밑의 주석을 풀어서 `____`를 채워요.

`pool_pre_ping=True`로 하면, 모아 둔 연결을 쓰기 전에 가벼운 확인 신호를 먼저 보내 봐요. 끊긴 연결이면 버리고 새로 만들어요.

<details>
<summary>정답 보기</summary>

```python
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
```

</details>

```powershell
uv run pytest
```

→ **32 passed**

저장하면 `fastapi dev`가 서버를 알아서 다시 켜요. 7-4의 두 번째 실험(`docker compose restart`)을 다시 해 보세요. 이번엔 재시작 직후 첫 요청도 **200**이에요.

> 이제 DB가 꺼진 상태에서 `GET /api/health`를 부르면 **5초쯤 뒤에** 503이 나와요.
> 끊긴 연결을 버리고 새로 연결해 보다가, `connect_timeout=5`만큼 기다리고 포기하기 때문이에요. 정상이에요.

**커밋**: `feat: DB에 연결이 안 되면 헬스체크 503`
(`app/errors.py`, `app/api/health.py`, `app/db.py`, `tests/test_health.py`)

---

## 8. README 업데이트

`README.md`를 이렇게 바꿔요.

1. 5번째 줄: `현재 상태: **2단계 완료** (PostgreSQL + Alembic + 테스트)`
2. 기술 스택 표
   - DB 줄: `| DB | PostgreSQL 18 (Docker) |`
   - Tooling 줄: `| Tooling | uv, pytest, Ruff, Oxlint, Docker, Git / GitHub |`
3. "로컬에서 실행하기"
   - 필요한 도구에 `[Docker Desktop](https://www.docker.com/products/docker-desktop/)`을 추가해요.
   - "백엔드" 명령 맨 앞에 DB를 띄우는 줄을 넣어요.

     ```bash
     docker compose up -d   # 프로젝트 맨 위 폴더에서. PostgreSQL을 띄워요
     cd backend
     uv sync
     uv run alembic upgrade head
     uv run fastapi dev app/main.py
     ```

4. "테스트" 섹션 코드 블록 위에 한 줄을 넣어요.
   `테스트는 PostgreSQL의 테스트 전용 DB(agentlab_test)에서 돌아요. docker compose up -d로 DB를 먼저 띄워요.`
5. 로드맵: `- [x] 2. PostgreSQL + 마이그레이션(Alembic) + 테스트`

**커밋**: `docs: README에 Docker 실행 방법 추가`

---

## 9. PR 만들고 merge하기

전반과 같아요.

1. `git push -u origin feat/postgresql`
2. GitHub에서 PR을 만들어요. 제목은 `feat: PostgreSQL 전환과 테스트 DB 분리 (2단계 후반)`이에요.
3. **merge하기 전에 저에게 리뷰를 요청하세요.**
4. 리뷰 반영 → **Create a merge commit** → 로컬 정리 (`git switch main`, `git pull`, `git branch -d feat/postgresql`)

---

## 10. 자주 만나는 에러

| 증상 | 원인 | 해결 |
|---|---|---|
| `failed to resolve reference "docker.io/library/postgres:____"` | 3-1의 이미지 빈칸을 안 채웠어요 | `image: postgres:18` |
| `invalid hostPort: ____` | 3-1의 포트 빈칸을 안 채웠어요 | `"127.0.0.1:5432:5432"` |
| `port is already allocated`처럼 포트 이야기가 나와요 | 5432번 포트를 다른 프로그램이 쓰고 있어요 (예: PC에 직접 설치한 PostgreSQL) | 그 프로그램을 꺼요 |
| `agentlab_test`가 DB 목록에 없어요 | 볼륨이 이미 있어서 SQL 파일이 실행되지 않았어요 (처음 만들 때만 실행돼요) | `docker compose exec db createdb -U agentlab agentlab_test` |
| `ModuleNotFoundError: No module named 'psycopg'` | 4-1을 안 했어요 | `uv add "psycopg[binary]"` |
| `connection timeout expired` | Docker Desktop이나 DB 컨테이너가 꺼져 있어요 | Docker Desktop을 켜고 `docker compose up -d` |
| `uv run pytest`가 `30 errors`로 끝나요 | 위와 같아요. 테스트 DB에 접속을 못 했어요 | 위와 같아요 |
| 접속이 10초 넘게 멈췄다가 돼요 | DB 주소에 `localhost`를 썼어요 | `127.0.0.1`로 바꿔요 |
| conftest의 `assert make_url(...)` 줄에서 `AssertionError` | 테스트 DB 주소가 `_test`로 끝나는 DB가 아니에요 | `.env`를 만들었다면 `TEST_DATABASE_URL`을 확인해요 |
| 6-3에서 `Target database is not up to date.` | 개발용 DB에 아직 적용 안 한 마이그레이션이 있어요 (4-3을 건너뛰었어요) | `uv run alembic upgrade head` 먼저 |
| 6-3에서 만든 파일의 `upgrade()`가 `pass`뿐이에요 | 6-2를 저장하지 않았거나, 같은 명령을 두 번 쳤어요 | `alembic/versions/`의 그 빈 파일을 지우고, 6-2를 확인한 뒤 다시 만들어요 |

## 11. 완료 체크리스트

- [ ] `docker compose ps` → `(healthy)`
- [ ] `uv run pytest` → **32 passed**
- [ ] `uv run ruff check .` → `All checks passed!`
- [ ] `uv run alembic check` → `No new upgrade operations detected.`
- [ ] `uv run alembic history` → 마이그레이션 3개
- [ ] DB를 끄면 `GET /api/health`가 503, 다시 켜면 200
- [ ] `[2단계` 안내 줄을 모두 지웠고, `____`가 남아 있지 않아요 (`Ctrl+Shift+F`로 검색)
- [ ] 커밋 6개 정도 (Docker, PostgreSQL 전환, 테스트, 시간대, 503, README)
- [ ] PR → 리뷰 → merge
