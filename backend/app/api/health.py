from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.api.deps import SessionDep
from app.errors import ServiceUnavailableError

# @RestController + @RequestMapping("/api/health") 역할
router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def health_check(session: SessionDep) -> dict[str, str]:
    try:
        session.execute(text("SELECT 1"))
    # OperationalError: DB에 연결이 안 될 때 나는 예외예요. (DB가 꺼져 있을 때 등)
    except OperationalError as e:
        raise ServiceUnavailableError("Database is unavailable") from e
    return {"status": "ok", "database": "ok"}
