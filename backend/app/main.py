from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

# models를 import해야 엔티티가 Base에 등록되고, create_all이 만들 테이블을 알 수 있어요.
from app import models  # noqa: F401
from app.api import agents, health
from app.db import Base, engine
from app.errors import register_error_handlers


# 서버가 시작될 때 한 번 실행돼요. 지금은 없는 테이블을 만들어요 (JPA ddl-auto=update와 비슷).
# 2단계에서 Alembic 마이그레이션(Flyway 같은 도구)으로 바꿀 거예요.
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(engine)
    yield


# Spring Boot의 @SpringBootApplication처럼 애플리케이션의 진입점이에요.
app = FastAPI(title="AgentLab API", version="0.1.0", lifespan=lifespan)
register_error_handlers(app)
app.include_router(agents.router)
app.include_router(health.router)


# @GetMapping("/")과 같아요. 반환한 dict는 자동으로 JSON 응답이 돼요.
@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, LUNA!"}
