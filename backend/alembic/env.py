# Alembic 명령(upgrade, revision 등)을 실행할 때마다 Alembic이 이 파일을 먼저 실행해요.
# 대부분 Alembic이 만들어 준 기본 코드예요.

# fileConfig: 설정 파일(alembic.ini)에 적힌 대로 로그 출력을 켜 주는 함수예요.
from logging.config import fileConfig

# context: 지금 실행 중인 Alembic의 상태와 설정을 담고 있어요. Alembic이 넣어 줘요.
from alembic import context

# engine_from_config: 설정을 보고 DB 연결(엔진)을 만들어요.
#   app/db.py의 create_engine과 같은 역할이에요.
# pool: DB 연결을 재사용하는 방식을 정해요.
from sqlalchemy import engine_from_config, pool

# 모델을 import해야 Base에 테이블이 등록돼요.
from app import models  # noqa: F401
from app.config import settings
from app.db import Base

# alembic.ini 내용을 담고 있는 설정 객체예요. 아래에서 config.~ 로 꺼내 써요.
config = context.config

# alembic.ini의 [loggers] 설정대로 로그를 보여줘요. (터미널에 나오는 INFO 줄들이 이거예요)
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# DB 주소가 따로 정해지지 않았으면(테스트가 아닐 때) 앱 설정(.env)의 주소를 써요.
# get_main_option: alembic.ini에서 값을 읽어요. 비어 있으면 빈 문자열이 와요.
if not config.get_main_option("sqlalchemy.url"):
    # set_main_option: 설정 값을 넣어요. 여기서는 DB 주소를 넣어요.
    config.set_main_option("sqlalchemy.url", settings.database_url)

# autogenerate가 DB와 비교할 "모델 쪽 테이블 정보"예요.
target_metadata = Base.metadata


# "오프라인 모드": DB에 접속하지 않고, 실행할 SQL 문만 화면에 보여줘요.
# (uv run alembic upgrade head --sql 처럼 --sql을 붙였을 때만 써요. 평소엔 안 써요)
def run_migrations_offline() -> None:
    # 설정에서 DB 주소를 꺼내요.
    url = config.get_main_option("sqlalchemy.url")
    # Alembic에게 "이 주소, 이 모델 정보로 SQL을 만들어"라고 알려줘요.
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,  # SQL 안의 값(?)을 실제 값으로 채워서 보여줘요.
        dialect_opts={"paramstyle": "named"},  # SQL 문법 세부 설정이에요. 그대로 둬요.
        render_as_batch=True,  # SQLite용 batch 방식이에요. (아래 온라인 모드 설명 참고)
    )

    # 마이그레이션들을 순서대로 실행해요. 오프라인이라 SQL을 보여주기만 해요.
    with context.begin_transaction():
        context.run_migrations()


# "온라인 모드": DB에 직접 접속해서 마이그레이션을 실행해요. 평소에는 이쪽이 쓰여요.
def run_migrations_online() -> None:
    # alembic.ini에서 sqlalchemy.로 시작하는 설정(DB 주소 등)을 모아 DB 엔진을 만들어요.
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # 연결을 재사용하지 않아요 (한 번 쓰고 끝이라서).
    )

    # DB에 접속해요. with 블록이 끝나면 연결이 자동으로 닫혀요 (try-with-resources).
    with connectable.connect() as connection:
        # Alembic에게 "이 연결, 이 모델 정보로 마이그레이션해"라고 알려줘요.
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite는 컬럼 수정·삭제를 바로 못 해요.
            # 그래서 테이블을 새로 만들어 옮기는 batch 방식을 써요.
            render_as_batch=True,
        )

        # 마이그레이션들을 순서대로 실행해요.
        with context.begin_transaction():
            context.run_migrations()


# alembic 명령에 --sql을 붙였으면 오프라인 모드, 아니면 온라인 모드로 실행해요.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
