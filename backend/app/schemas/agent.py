from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


# 요청·응답에 쓰는 DTO예요. Field(...)가 Bean Validation(@Size, @Min, @Max) 역할을 해요.
class AgentBase(BaseModel):
    # 문자열 앞뒤 공백을 자동으로 지워요. " alpha " → "alpha", "   " → "" (그래서 422)
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    model: str = Field(default="mock", max_length=100)
    system_prompt: str = "You are a helpful assistant."
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


class AgentCreate(AgentBase):
    pass


# PATCH용이에요. 보낸 필드만 바꾸니까 모든 필드가 선택 항목이에요.
class AgentUpdate(BaseModel):
    # 문자열 앞뒤 공백을 자동으로 지워요. " alpha " → "alpha", "   " → "" (그래서 422)
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    model: str | None = Field(default=None, max_length=100)
    system_prompt: str | None = None
    temperature: float | None = Field(default=None, ge=0.0, le=1.0)

    # 안 보내는 건 괜찮지만, DB에서 NOT NULL인 필드에 null을 보내면 422로 막아요.
    @field_validator(  # 이 네 필드에 값이 들어오면 아래 함수로 한 번 더 검사해요.
        "name", "model", "system_prompt", "temperature"
    )
    @classmethod
    def reject_null(cls, value: object) -> object:
        if value is None:
            # ValueError 값이 잘못됐어요"를 뜻하는 Python 기본 예외
            # `ValueError`를 던지면 Pydantic이 422 응답으로 바꿔줘요.
            raise ValueError("null is not allowed")
        return value


class AgentRead(AgentBase):
    # SQLAlchemy 엔티티 객체에서 값을 읽어 DTO를 만들 수 있게 해줘요.
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
