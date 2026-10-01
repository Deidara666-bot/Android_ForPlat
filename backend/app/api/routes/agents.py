from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_agent, get_current_user, get_db
from app.models.agent import Agent
from app.schemas.agent import AgentMeOut, AgentOut, AgentRegisterIn, AgentRegisterOut
from app.services.agent_service import AgentService, is_connected

router = APIRouter(prefix="/agents", tags=["agents"])
_examiner = [Depends(get_current_user)]


@router.post(
    "/register",
    dependencies=_examiner,
    response_model=AgentRegisterOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register an agent and issue its token (shown once)",
)
def register_agent(
    body: AgentRegisterIn, db: Annotated[Session, Depends(get_db)]
) -> AgentRegisterOut:
    token = AgentService(db).register(body.agent_id, body.version)
    return AgentRegisterOut(agent_id=body.agent_id, token=token)


@router.get("", response_model=list[AgentOut], dependencies=_examiner, summary="List agents")
def list_agents(db: Annotated[Session, Depends(get_db)]) -> list[AgentOut]:
    return [
        AgentOut(
            id=agent.id,
            agent_id=agent.agent_id,
            version=agent.version,
            last_seen_at=agent.last_seen_at,
            connected=is_connected(agent),
        )
        for agent in AgentService(db).list()
    ]


@router.get("/me", response_model=AgentMeOut, summary="Identity of the calling agent (agent token)")
def agent_me(
    agent: Annotated[Agent, Depends(get_current_agent)], db: Annotated[Session, Depends(get_db)]
) -> Agent:
    AgentService(db).touch(agent)
    return agent
