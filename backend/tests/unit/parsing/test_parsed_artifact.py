from typing import Any

import pytest
from pydantic import ValidationError

from app.core.constants import ParseStatus
from app.parsing.base import ParsedArtifact


def _build(**overrides: Any) -> ParsedArtifact:
    values: dict[str, Any] = {
        "artifact_type": "package_inventory_entry",
        "parser_name": "package_state.inventory",
        "parser_version": "1",
        "subject_key": "com.synthetic.alpha",
        "raw_value": "package:com.synthetic.alpha uid:10101",
        "parsed_value_json": {"line_no": 1},
        "parse_status": ParseStatus.parsed,
        "parse_note": "",
    }
    values.update(overrides)
    return ParsedArtifact(**values)


def test_valid_parsed_artifact_accepted() -> None:
    assert _build().parse_status == ParseStatus.parsed


@pytest.mark.parametrize("field", ["parser_name", "parser_version"])
@pytest.mark.parametrize("blank", ["", "   "])
def test_blank_parser_provenance_rejected(field: str, blank: str) -> None:
    with pytest.raises(ValidationError) as raised:
        _build(**{field: blank})
    assert field in str(raised.value)


@pytest.mark.parametrize("status", [ParseStatus.failed, ParseStatus.empty])
def test_parse_note_required_when_not_parsed(status: ParseStatus) -> None:
    with pytest.raises(ValidationError) as raised:
        _build(parse_status=status, parse_note="", raw_value="x")
    assert "parse_note" in str(raised.value)


def test_failed_with_note_accepted() -> None:
    assert _build(parse_status=ParseStatus.failed, parse_note="baris rusak").parse_note


def test_empty_raw_value_only_for_empty_status() -> None:
    with pytest.raises(ValidationError) as raised:
        _build(raw_value="")
    assert "raw_value" in str(raised.value)
    assert _build(raw_value="", parse_status=ParseStatus.empty, parse_note="kosong")


def test_extra_field_and_mutation_rejected() -> None:
    with pytest.raises(ValidationError):
        _build(unexpected=1)
    artifact = _build()
    with pytest.raises(ValidationError):
        artifact.raw_value = "lain"  # type: ignore[misc]
