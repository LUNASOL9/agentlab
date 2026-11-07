# command: 터미널의 alembic 명령(upgrade, downgrade, check)을 코드에서 부르게 해 줘요.
from alembic import command

# Config: alembic.ini 설정 파일을 읽어서 담아 두는 객체예요.
from alembic.config import Config


# 테스트 1: 마이그레이션 파일들로 만든 DB가 모델(app/models)과 똑같은지 확인해요.
# alembic_config: conftest.py의 fixture가 넣어 줘요. 테스트 DB(agentlab_test)를 써요.
def test_migrations_match_models(alembic_config: Config) -> None:
    # 아직 실행 안 한 마이그레이션 파일을 순서대로 실행해요. (`alembic upgrade head`)
    # conftest가 테스트를 시작할 때 이미 head까지 올려 둬서, 보통은 할 일이 없어요.
    command.upgrade(alembic_config, "head")

    # 모델과 DB를 비교해요. 다르면 에러가 나서 테스트가 실패해요. (`alembic check`)
    # 예: 모델은 바꿨는데, 마이그레이션 파일을 안 만들었을 때
    command.check(alembic_config)


# 테스트 2: 마이그레이션을 끝까지 되돌렸다가 다시 적용할 수 있는지 확인해요.
def test_migrations_can_downgrade_and_upgrade_again(alembic_config: Config) -> None:
    # 끝까지 적용해요. (`alembic upgrade head`)
    command.upgrade(alembic_config, "head")
    # 맨 처음(테이블이 하나도 없는 상태)까지 되돌려요. (`alembic downgrade base`)
    command.downgrade(alembic_config, "base")
    # 다시 끝까지 적용해요. 여기까지 에러 없이 오면 통과예요.
    command.upgrade(alembic_config, "head")
