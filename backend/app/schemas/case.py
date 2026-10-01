import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CaseCreate(BaseModel):
    case_number: str = Field(min_length=1)
    title: str = Field(min_length=1)


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    case_number: str
    title: str
    created_by: uuid.UUID
    created_at: datetime
