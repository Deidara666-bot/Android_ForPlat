import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AgentRegisterIn(BaseModel):
    agent_id: str = Field(min_length=1, max_length=128)
    version: str = Field(min_length=1, max_length=32)


class AgentRegisterOut(BaseModel):
    """The only response that carries the raw token; it is shown once."""

    agent_id: str
    token: str


class AgentOut(BaseModel):
    """Listing shape: never carries `token` or `token_hash`."""

    id: uuid.UUID
    agent_id: str
    version: str
    last_seen_at: datetime | None
    connected: bool


class AgentMeOut(BaseModel):
    id: uuid.UUID
    agent_id: str
    version: str
    last_seen_at: datetime | None
