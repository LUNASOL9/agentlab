# Path: 파일과 폴더 경로를 다루는 도구예요. Java의 java.nio.file.Path와 같아요.
from pathlib import Path

# command: 터미널에서 치던 alembic 명령(upgrade, downgrade, check)을 코드에서 부를 수 있게 해 줘요.
from alembic import command

# Config: alembic.ini 설정 파일을 읽어서 담아 두는 객체예요.
from alembic.config import Config

# alembic.ini 파일의 위치를 찾는 한 줄이에요. 앞에서부터 차례로 읽으면 돼요.
#   __file__        → 지금 이 파일(test_migrations.py)의 경로
#   .resolve()      → 전체 경로로 바꿔요. 예: C:/agentlab/backend/tests/test_migrations.py
#   .parents[1]     → 두 단계 위 폴더예요. [0]은 tests 폴더, [1]은 backend 폴더예요.
#   / "alembic.ini" → 그 폴더 안의 alembic.ini 파일 (Path에서 / 는 나누기가 아니라 "폴더 안"이에요)
# 결과: C:/agentlab/backend/alembic.ini
ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


# 테스트용 Alembic 설정을 만드는 도우미 함수예요. 아래 두 테스트가 같이 써요.
# tmp_path: pytest가 테스트마다 새로 만들어 주는 빈 임시 폴더예요.
#           인자 이름을 tmp_path라고 쓰기만 하면 pytest가 알아서 넣어 줘요 (conftest의 client처럼).
def make_config(tmp_path: Path) -> Config:
    # alembic.ini를 읽어서 설정 객체를 만들어요. str(...)은 Path를 문자열로 바꿔요.
    config = Config(str(ALEMBIC_INI))
    # 임시 폴더 안에 만들 DB 파일 경로예요. 예: C:/Users/.../pytest-123/test.db
    db_file = tmp_path / "test.db"
    # DB 주소 형식은 "sqlite:///파일경로"예요. as_posix()는 경로의 \ 를 / 로 바꿔요.
    db_url = f"sqlite:///{db_file.as_posix()}"
    # 이 테스트에서는 개발용 DB(agentlab.db) 대신 이 임시 DB를 쓰라고 설정해요.
    config.set_main_option("sqlalchemy.url", db_url)
    return config


# 테스트 1: 마이그레이션 파일들로 만든 DB가 모델(app/models)과 똑같은지 확인해요.
def test_migrations_match_models(tmp_path: Path) -> None:
    # 임시 DB를 쓰는 설정을 준비해요.
    config = make_config(tmp_path)

    # upgrade: 아직 실행 안 한 마이그레이션 파일을 순서대로 실행해서 DB를 바꿔요.
    # "head": 가장 최신 파일까지 전부요. 빈 DB라서 모든 파일이 처음부터 실행돼요.
    # (터미널에서 `uv run alembic upgrade head`를 친 것과 같아요. 1-4에서 직접 쳐 봐요)
    command.upgrade(config, "head")

    # 모델과 DB를 비교해요. 터미널의 `uv run alembic check`와 같아요.
    # 다른 점이 있으면 에러가 나서 테스트가 실패해요.
    # 예: 모델에 컬럼을 추가했는데, 마이그레이션 파일을 안 만들었을 때
    command.check(config)


# 테스트 2: 마이그레이션을 끝까지 되돌렸다가 다시 적용할 수 있는지 확인해요.
def test_migrations_can_downgrade_and_upgrade_again(tmp_path: Path) -> None:
    # 임시 DB를 쓰는 설정을 준비해요.
    config = make_config(tmp_path)

    # 끝까지 적용해요. (`alembic upgrade head`)
    command.upgrade(config, "head")
    # 맨 처음(테이블이 하나도 없는 상태)까지 되돌려요. (`alembic downgrade base`)
    command.downgrade(config, "base")
    # 다시 끝까지 적용해요. 여기까지 에러 없이 오면 통과예요.
    command.upgrade(config, "head")
