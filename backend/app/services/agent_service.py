import hashlib
import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.agent import Agent

CONNECTED_WINDOW = timedelta(seconds=30)


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def is_connected(agent: Agent, now: datetime | None = None) -> bool:
    if agent.last_seen_at is None:
        return False
    return agent.last_seen_at > (now or datetime.now(UTC)) - CONNECTED_WINDOW


class AgentService:
    def __init__(self, db: Session) -> None:
        self._db = db

    def register(self, agent_id: str, version: str) -> str:
        """Issue a new token for `agent_id`; only its SHA-256 is stored. Raw token returned once."""
        token = secrets.token_urlsafe(32)
        agent = self._db.scalar(select(Agent).where(Agent.agent_id == agent_id))
        if agent is None:
            agent = Agent(agent_id=agent_id, version=version, token_hash=hash_token(token))
            self._db.add(agent)
        else:
            agent.token_hash = hash_token(token)
            agent.version = version
        self._db.commit()
        return token

    def find_by_token(self, token: str) -> Agent | None:
        return self._db.scalar(select(Agent).where(Agent.token_hash == hash_token(token)))

    def touch(self, agent: Agent) -> None:
        agent.last_seen_at = datetime.now(UTC)
        self._db.commit()

    def list(self) -> list[Agent]:
        return list(self._db.scalars(select(Agent).order_by(Agent.agent_id)))
