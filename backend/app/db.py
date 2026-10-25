from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings

# SQLite는 연결을 만든 스레드에서만 쓰도록 막아요.
# FastAPI는 요청을 여러 스레드에서 처리하니 이 제한을 풀어줘요.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)


# 모든 엔티티(@Entity)의 부모 클래스예요.
class Base(DeclarativeBase):
    pass


# 요청마다 세션을 열고 응답이 끝나면 닫아요. JPA의 요청 단위 EntityManager와 비슷해요.
def get_session() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
