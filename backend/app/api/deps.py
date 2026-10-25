from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_session

# 엔드포인트 인자에 `session: SessionDep`라고만 쓰면 FastAPI가 세션을 넣어줘요.
# 생성자 주입이나 @Autowired와 같은 역할이에요.
SessionDep = Annotated[Session, Depends(get_session)]
