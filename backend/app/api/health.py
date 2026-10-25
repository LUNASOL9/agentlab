from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import SessionDep

# @RestController + @RequestMapping("/api/health") 역할
router = APIRouter(prefix="/api/health", tags=["health"])


@router.get("")
def health_check(session: SessionDep) -> dict[str, str]:
    session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}
