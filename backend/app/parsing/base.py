from typing import Protocol

from pydantic import BaseModel, ConfigDict

from app.core.constants import ParseStatus


class ParsedArtifact(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    artifact_type: str
    parser_name: str
    parser_version: str
    subject_key: str | None
    raw_value: str
    parsed_value_json: dict[str, object]
    parse_status: ParseStatus
    parse_note: str


class Parser(Protocol):
    operation_id: str
    parser_name: str
    parser_version: str

    def parse(self, raw: bytes) -> list[ParsedArtifact]: ...
