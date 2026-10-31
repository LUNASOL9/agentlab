from fastapi import FastAPI

from app.api import agents, health
from app.errors import register_error_handlers

# Spring Boot의 @SpringBootApplication처럼 애플리케이션의 진입점이에요.
# 테이블은 이제 Alembic이 만들어요 (uv run alembic upgrade head).
app = FastAPI(title="AgentLab API", version="0.1.0")
register_error_handlers(app)
app.include_router(agents.router)
app.include_router(health.router)


# @GetMapping("/")과 같아요. 반환한 dict는 자동으로 JSON 응답이 돼요.
@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "Hello, LUNA!"}
