from app.core.constants import ParseStatus
from app.parsing.base import ParsedArtifact


def decode_failure(
    artifact_type: str, parser_name: str, parser_version: str, error: UnicodeDecodeError
) -> ParsedArtifact:
    """One failed artifact for undecodable evidence; raw text is unavailable by definition."""
    return ParsedArtifact(
        artifact_type=artifact_type,
        parser_name=parser_name,
        parser_version=parser_version,
        subject_key=None,
        raw_value="",
        parsed_value_json={},
        parse_status=ParseStatus.failed,
        parse_note=f"decode utf-8 gagal pada offset byte {error.start}",
    )


def numbered_lines(text: str) -> list[tuple[int, str]]:
    """(line_no, line) for every line; numbering starts at 1 and counts blank lines.

    A newline ends a line and one carriage return directly before it belongs to the
    terminator. Nothing else is trimmed or repaired.
    """
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    return [(no, line.removesuffix("\r")) for no, line in enumerate(lines, start=1)]
