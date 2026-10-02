from typing import Protocol, Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

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

    @field_validator("parser_name", "parser_version")
    @classmethod
    def _provenance_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("parser_name and parser_version must not be blank")
        return value

    @model_validator(mode="after")
    def _status_rules(self) -> Self:
        if self.parse_status != ParseStatus.parsed and not self.parse_note.strip():
            raise ValueError("parse_note is required when parse_status is not parsed")
        if self.raw_value == "" and self.parse_status == ParseStatus.parsed:
            raise ValueError("raw_value is required when parse_status is parsed")
        return self


class Parser(Protocol):
    operation_id: str
    parser_name: str
    parser_version: str

    def parse(self, raw: bytes) -> list[ParsedArtifact]: ...
