"""Parser for the activity-manager dump (operation `collect_usage_state`, part 2).

Only the activity that is resumed at the moment of acquisition is read: the `topResumedActivity`
line of each display, or, when no such line exists, the `ResumedActivity:` line (older output
spells it `mResumedActivity:`). The result is a snapshot, a current state, never a history.
`topResumedActivity=null` is a parsed answer ("no resumed activity"), not a failure.
"""

import re

from app.core.constants import ParseStatus
from app.parsing.base import ParsedArtifact
from app.parsing.package_state._text import decode_failure, numbered_lines

ARTIFACT_TYPE = "resumed_activity"
_HEADER = "ACTIVITY MANAGER ACTIVITIES"
_DISPLAY = re.compile(r"Display #(?P<display>\d+)\b.*")
_RECORD = (
    r"ActivityRecord\{(?P<hash>[0-9a-f]+) u(?P<user>\d+) "
    r"(?P<component>[A-Za-z0-9_.]+/\S+) t(?P<task>\d+)\}"
)
_TOP = re.compile(rf"\s*topResumedActivity=(?:(?P<null>null)|{_RECORD})")
_FALLBACK = re.compile(rf"\s*m?ResumedActivity: {_RECORD}")


class ResumedActivityParser:
    operation_id = "collect_usage_state"
    parser_name = "usage_stats.activity"
    parser_version = "1"
    raw_source = "dumpsys activity"

    def parse(self, raw: bytes) -> list[ParsedArtifact]:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            return [decode_failure(ARTIFACT_TYPE, self.parser_name, self.parser_version, error)]
        lines = [(no, line) for no, line in numbered_lines(text) if line.strip() != ""]
        if not lines:
            return [self._artifact(None, "", {}, ParseStatus.empty, "bukti tidak memuat keluaran")]
        if not lines[0][1].startswith(_HEADER):
            return [
                self._artifact(
                    None,
                    lines[0][1],
                    {},
                    ParseStatus.failed,
                    "baris pertama bukan kepala keluaran activity manager",
                )
            ]

        display: int | None = None
        top: list[ParsedArtifact] = []
        fallback: list[ParsedArtifact] = []
        for number, line in lines[1:]:
            shown = _DISPLAY.fullmatch(line)
            if shown:
                display = int(shown["display"])
                continue
            stripped = line.strip()
            if stripped.startswith("topResumedActivity="):
                top.append(self._from_match(_TOP.fullmatch(line), line, number, display, "top"))
            elif stripped.startswith(("ResumedActivity:", "mResumedActivity:")):
                match = _FALLBACK.fullmatch(line)
                fallback.append(self._from_match(match, line, number, display, "resumed"))

        rows = top or fallback
        if not rows:
            return [
                self._artifact(
                    None,
                    lines[0][1],
                    {},
                    ParseStatus.failed,
                    "tidak ada baris topResumedActivity atau ResumedActivity",
                )
            ]
        return rows

    def _from_match(
        self, match: re.Match[str] | None, line: str, number: int, display: int | None, source: str
    ) -> ParsedArtifact:
        if match is None:
            return self._artifact(
                None,
                line,
                {"line_no": number},
                ParseStatus.failed,
                "baris tidak sesuai bentuk ActivityRecord{<hash> u<user> <paket>/<kelas> t<task>}",
            )
        if "null" in match.groupdict() and match["null"]:
            return self._artifact(
                None,
                line,
                {"has_resumed_activity": False, "display": display, "line_no": number},
                ParseStatus.parsed,
                "",
            )
        component = match["component"]
        package = component.split("/", 1)[0]
        return self._artifact(
            package,
            line,
            {
                "has_resumed_activity": True,
                "package": package,
                "component": component,
                "user": int(match["user"]),
                "task": int(match["task"]),
                "display": display,
                "source": source,
                "line_no": number,
            },
            ParseStatus.parsed,
            "",
        )

    def _artifact(
        self,
        subject_key: str | None,
        raw_value: str,
        parsed_value_json: dict[str, object],
        status: ParseStatus,
        note: str,
    ) -> ParsedArtifact:
        return ParsedArtifact(
            artifact_type=ARTIFACT_TYPE,
            parser_name=self.parser_name,
            parser_version=self.parser_version,
            subject_key=subject_key,
            raw_value=raw_value,
            parsed_value_json=parsed_value_json,
            parse_status=status,
            parse_note=note,
        )
