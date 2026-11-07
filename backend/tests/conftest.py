from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, make_url, text
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.db import get_session
from app.main import app

# backend/alembic.ini 위치예요. (test_migrations.py에 있던 줄을 옮겨 왔어요)
ALEMBIC_INI = Path(__file__).resolve().parents[1] / "alembic.ini"


# 테스트용 Alembic 설정이에요. 개발용 DB 대신 테스트 DB(agentlab_test)를 써요.
# scope="session": 테스트 전체에서 딱 한 번만 만들어서 같이 써요.
@pytest.fixture(scope="session")
def alembic_config() -> Config:
    config = Config(str(ALEMBIC_INI))
    config.set_main_option("sqlalchemy.url", settings.test_database_url)
    return config


# 테스트를 시작할 때 테스트 DB를 깨끗하게 만들어요. 테스트 전체에서 한 번만 실행돼요.
# autouse=True: 테스트 함수 인자에 안 써도 자동으로 실행돼요.
@pytest.fixture(scope="session", autouse=True)
def db_engine(alembic_config: Config) -> Iterator[Engine]:

    # 실수로 개발용 DB를 지우지 않게, 이름이 _test로 끝나는 DB에서만 돌려요.
    # make_url(주소).database: 주소에서 DB 이름(agentlab_test)만 꺼내요.
    assert make_url(settings.test_database_url).database.endswith("_test")
    engine = create_engine(settings.test_database_url)

    # public은 DB 안의 기본 스키마(테이블이 들어 있는 폴더)예요.
    # 폴더째 지우고 다시 만들면, 지난번 테스트가 남긴 테이블이 모두 사라져요.
    # begin(): 블록이 끝나면 자동으로 commit해요 (@Transactional처럼).
    with engine.begin() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE"))
        connection.execute(text("CREATE SCHEMA public"))

    # 마이그레이션 파일로 테이블을 만들어요. 개발용 DB를 만들 때와 같은 방법이에요.
    command.upgrade(alembic_config, "head")
    yield engine
    engine.dispose()


# 테스트 함수 인자에 `client`라고 쓰면 pytest가 이 함수를 실행해서 넣어줘요.
@pytest.fixture
def client(db_engine: Engine) -> Iterator[TestClient]:
    testing_session = sessionmaker(bind=db_engine)

    def override_get_session() -> Iterator[Session]:
        with testing_session() as session:
            yield session

    # Spring 테스트에서 빈을 바꿔 끼우는 것(@TestConfiguration, @MockBean)과 같아요.
    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()

    # 테스트가 끝나면 테이블을 비워요. 다음 테스트는 빈 테이블에서 시작해요.
    # RESTART IDENTITY: id 번호도 1부터 다시 시작해요.
    with db_engine.begin() as connection:
        connection.execute(text("TRUNCATE agents RESTART IDENTITY"))
