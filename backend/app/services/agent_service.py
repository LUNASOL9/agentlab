from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.errors import ConflictError, NotFoundError
from app.models import Agent
from app.schemas.agent import AgentCreate, AgentUpdate


# @Service 계층이에요. HTTP는 모르고, 비즈니스 로직과 DB 작업만 해요.
def create_agent(session: Session, data: AgentCreate) -> Agent:
    agent = Agent(**data.model_dump())
    session.add(agent)

    _commit_or_conflict(session, agent.name)

    session.refresh(agent)  # DB가 채운 id, created_at 등을 다시 읽어와요.
    return agent


def get_agent(session: Session, agent_id: int) -> Agent:
    agent = session.get(Agent, agent_id)  # em.find(Agent.class, id)와 같아요.
    if agent is None:
        raise NotFoundError(f"Agent not found: id={agent_id}")
    return agent


def list_agents(session: Session, offset: int, limit: int) -> list[Agent]:
    stmt = select(Agent).order_by(Agent.id).offset(offset).limit(limit)
    return list(session.scalars(stmt))


def update_agent(session: Session, agent_id: int, data: AgentUpdate) -> Agent:
    agent = get_agent(session, agent_id)  # 없는 id면 여기서 NotFoundError가 나요.
    changes = data.model_dump(exclude_unset=True)  # 요청에 들어온 필드만 꺼내요.
    for field, value in changes.items():
        setattr(agent, field, value)  # agent.<field> = value 와 같아요.

    _commit_or_conflict(session, agent.name)
    session.refresh(agent)
    return agent


def delete_agent(session: Session, agent_id: int) -> None:
    agent = get_agent(session, agent_id)
    session.delete(agent)
    session.commit()


# create_agent와 update_agent가 같이 써요. 이름이 겹쳐 저장에 실패하면 409로 바꿔요.
# 이름 앞의 _는 "이 파일 안에서만 쓰는 함수"라는 약속이에요 (Java의 private).
def _commit_or_conflict(session: Session, name: str) -> None:
    try:
        session.commit()  # 엔티티 값만 바꾸고 `commit()`하면 INSERT UPDATE가 실행
    except IntegrityError as e:  # 이름이 겹칠 때 나는 예외`IntegrityError`
        session.rollback()  # 실패한 작업을 되돌려요.
        raise ConflictError(f"Agent name already exists: {name}") from e
