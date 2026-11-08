from collections.abc import Iterator

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.db import get_session
from app.main import app


def test_health(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


# DB에 쿼리를 보내면 무조건 "연결 안 됨" 예외를 던지는 가짜 세션이에요.
class BrokenSession:
    def execute(self, *args: object, **kwargs: object) -> None:
        raise OperationalError("SELECT 1", {}, Exception("DB is down"))


def test_health_returns_503_when_database_is_down(client: TestClient) -> None:
    def broken_session() -> Iterator[BrokenSession]:
        yield BrokenSession()

    # client가 끼워 둔 테스트 DB 세션 대신, 가짜 세션을 끼워요 (@MockBean처럼).
    app.dependency_overrides[get_session] = broken_session

    response = client.get("/api/health")

    assert response.status_code == 503  # 503 Service Unavailable("지금은 서비스를 못 해요")
    assert response.json() == {"detail": "Database is unavailable"}
