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
    # 값은 DB가 채워요 (@CreationTimestamp, @UpdateTimestamp 역할).
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
