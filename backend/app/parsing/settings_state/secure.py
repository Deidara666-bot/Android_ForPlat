"""Parser for a secure-settings list of components (`pkg/Class` joined by `:`).

One parser object per evidence part: the enabled accessibility services and the enabled
notification listeners share a format, so the same class serves both. The value `null` means the
setting is unset: it parses, as an empty list, and is never read as "failed" or as a component.

Every parsed output starts with one `settings_secure_list` artifact (the proof that the whole
value was read, also for `null`), followed by one `enabled_special_access_component` artifact
per component, in the order the device printed them.
"""

import re

from app.core.constants import ParseStatus
from app.parsing.base import ParsedArtifact
from app.parsing.package_state._text import decode_failure, numbered_lines

LIST_ARTIFACT_TYPE = "settings_secure_list"
COMPONENT_ARTIFACT_TYPE = "enabled_special_access_component"
_COMPONENT = re.compile(r"(?P<package>[A-Za-z0-9_.]+)/(?P<class>[A-Za-z0-9_.$]+)")
_NULL = "null"


class SecureListParser:
    operation_id = "collect_accessibility_state"
    parser_name = "settings_state.secure"
    parser_version = "1"

    def __init__(self, raw_source: str, special_access: str) -> None:
        self.raw_source = raw_source
        self._special_access = special_access

    def parse(self, raw: bytes) -> list[ParsedArtifact]:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            return [
                decode_failure(LIST_ARTIFACT_TYPE, self.parser_name, self.parser_version, error)
            ]
        lines = [(no, line) for no, line in numbered_lines(text) if line != ""]
        if not lines:
            return [
                self._artifact(
                    LIST_ARTIFACT_TYPE,
                    None,
                    "",
                    {},
                    ParseStatus.empty,
                    "bukti tidak memuat nilai pengaturan",
                )
            ]
        if len(lines) != 1:
            return [
                self._artifact(
                    LIST_ARTIFACT_TYPE,
                    None,
                    lines[0][1],
                    {"line_count": len(lines)},
                    ParseStatus.failed,
                    "nilai pengaturan harus satu baris",
                )
            ]
        value = lines[0][1]
        if value == _NULL:
            return [self._list_artifact(value, 0, True)]

        rows: list[ParsedArtifact] = []
        components = 0
        for token in value.split(":"):
            match = _COMPONENT.fullmatch(token)
            if match is None:
                rows.append(
                    self._artifact(
                        COMPONENT_ARTIFACT_TYPE,
                        None,
                        token,
                        {},
                        ParseStatus.failed,
                        "token tidak sesuai bentuk <paket>/<kelas>",
                    )
                )
                continue
            components += 1
            rows.append(
                self._artifact(
                    COMPONENT_ARTIFACT_TYPE,
                    match["package"],
                    token,
                    {
                        "special_access": self._special_access,
                        "component": token,
                        "package": match["package"],
                        "index": components,
                    },
                    ParseStatus.parsed,
                    "",
                )
            )
        return [self._list_artifact(value, components, False), *rows]

    def _list_artifact(self, raw: str, count: int, is_null: bool) -> ParsedArtifact:
        return self._artifact(
            LIST_ARTIFACT_TYPE,
            None,
            raw,
            {"special_access": self._special_access, "count": count, "is_null": is_null},
            ParseStatus.parsed,
            "",
        )

    def _artifact(
        self,
        artifact_type: str,
        subject_key: str | None,
        raw_value: str,
        parsed_value_json: dict[str, object],
        status: ParseStatus,
        note: str,
    ) -> ParsedArtifact:
        return ParsedArtifact(
            artifact_type=artifact_type,
            parser_name=self.parser_name,
            parser_version=self.parser_version,
            subject_key=subject_key,
            raw_value=raw_value,
            parsed_value_json=parsed_value_json,
            parse_status=status,
            parse_note=note,
        )
