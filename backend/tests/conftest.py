from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.main import app


# 테스트 함수 인자에 `client`라고 쓰면 pytest가 이 함수를 실행해서 넣어줘요.
# 테스트마다 비어 있는 메모리 DB를 새로 만들어서, 실제 agentlab.db 파일은 건드리지 않아요.
@pytest.fixture
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # 메모리 DB를 모든 연결이 같이 쓰게 해요.
    )
    Base.metadata.create_all(engine)
    testing_session = sessionmaker(bind=engine)

    def override_get_session() -> Iterator[Session]:
        with testing_session() as session:
            yield session

    # Spring 테스트에서 빈을 바꿔 끼우는 것(@TestConfiguration, @MockBean)과 같아요.
    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()
    engine.dispose()
