from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


# JPA의 @Entity @Table(name = "agents")와 같아요.
class Agent(Base):
    __tablename__ = "agents"

    # Mapped[str]은 NOT NULL, Mapped[str | None]은 NULL 허용 컬럼이 돼요.
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    description: Mapped[str | None] = mapped_column(String(500))
    model: Mapped[str] = mapped_column(String(100))
    system_prompt: Mapped[str] = mapped_column(Text)
    temperature: Mapped[float]
    # [2단계 2-1] 주석을 풀고 ____를 채워요.
    # # LLM과 도구 사이를 최대 몇 번 오갈지예요 (무한 반복 방지).
    # # server_default는 DB가 채우는 기본값이라, 이미 있던 행에도 이 값이 들어가요.
    # max_steps: Mapped[int] = mapped_column(server_default=____)

    # 값은 DB가 채워요 (@CreationTimestamp, @UpdateTimestamp 역할).
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
