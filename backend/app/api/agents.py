from typing import Annotated

from fastapi import APIRouter, Query, status

from app.api.deps import SessionDep
from app.schemas.agent import AgentCreate, AgentRead, AgentUpdate
from app.services import agent_service

# @RestController + @RequestMapping("/api/agents") 역할이에요.
router = APIRouter(prefix="/api/agents", tags=["agents"])


# @PostMapping이에요. JSON 본문이 AgentCreate로 변환·검증돼요 (@RequestBody @Valid).
@router.post("", status_code=status.HTTP_201_CREATED)
def create_agent(data: AgentCreate, session: SessionDep) -> AgentRead:
    agent = agent_service.create_agent(session, data)
    return AgentRead.model_validate(agent)  # Entity → DTO 변환


# 경로의 {agent_id}가 int로 변환돼서 들어와요 (@PathVariable).
@router.get("/{agent_id}")
def get_agent(agent_id: int, session: SessionDep) -> AgentRead:
    agent = agent_service.get_agent(session, agent_id)
    return AgentRead.model_validate(agent)


@router.get("")
def list_agents(
    session: SessionDep,
    offset: Annotated[int, Query(ge=1)] = 0,
    limit: Annotated[int, Query(le=100)] = 20,
) -> list[AgentRead]:
    agents = agent_service.list_agents(session, offset, limit)
    return [AgentRead.model_validate(agent) for agent in agents]


@router.patch("/{agent_id}")
def update_agent(agent_id: int, data: AgentUpdate, session: SessionDep) -> AgentRead:
    agent = agent_service.update_agent(session, agent_id, data)
    return AgentRead.model_validate(agent)


# [과제 4-2] 주석을 풀고 ____를 채워요.
# @router.delete("/{agent_id}", status_code=status.____)
# def delete_agent(agent_id: int, session: SessionDep) -> None:
#     agent_service.____(session, agent_id)
