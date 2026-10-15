import pytest
from sqlalchemy.orm import Session

from app.models.user import User
from app.research.knowledge_base.loader import KnowledgeBaseLoader
from tests.factories import Scene


@pytest.fixture
def scene(session: Session, user: User) -> Scene:
    KnowledgeBaseLoader().load_to_db(session)  # the rule loader resolves references against it
    return Scene(session, user)
