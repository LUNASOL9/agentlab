from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# 요청·응답에 쓰는 DTO예요. Field(...)가 Bean Validation(@Size, @Min, @Max) 역할을 해요.
class AgentBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    model: str = Field(default="mock", max_length=100)
    system_prompt: str = "You are a helpful assistant."
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


class AgentCreate(AgentBase):
    pass


# PATCH용이에요. 보낸 필드만 바꾸니까 모든 필드가 선택 항목이에요.
class AgentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    model: str | None = Field(default=None, max_length=100)
    system_prompt: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=1.0)


class AgentRead(AgentBase):
    # SQLAlchemy 엔티티 객체에서 값을 읽어 DTO를 만들 수 있게 해줘요.
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
