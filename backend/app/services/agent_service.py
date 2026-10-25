# [과제 2-1] 아래 한 줄의 주석을 풀어요.
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.errors import NotFoundError
from app.models import Agent
from app.schemas.agent import AgentCreate, AgentUpdate

# [과제 5-3] 아래 두 줄의 주석을 풀어요.
# from sqlalchemy.exc import IntegrityError
# from app.errors import ConflictError


# @Service 계층이에요. HTTP는 모르고, 비즈니스 로직과 DB 작업만 해요.
def create_agent(session: Session, data: AgentCreate) -> Agent:
    agent = Agent(**data.model_dump())
    session.add(agent)
    session.commit()
    # [과제 5-3] 바로 위의 session.commit() 줄을 지우고, 아래 주석을 풀어서 ____를 채워요.
    # try:
    #     session.commit()
    # except ____ as e:
    #     session.____()  # 실패한 작업을 되돌려요. 안 하면 세션이 오류 상태로 남아요.
    #     raise ____(f"Agent name already exists: {data.name}") from e
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
    session.commit()  # PA의 변경 감지(dirty checking)처럼, 엔티티 값만 바꾸고 `commit()`하면 UPDATE가 실행
    session.refresh(agent)
    return agent


# [과제 4-1] 주석을 풀고 ____를 채워요.
# def delete_agent(session: Session, agent_id: int) -> None:
#     agent = get_agent(session, agent_id)
#     session.____(agent)
#     session.commit()
