"""Parser for the process table (operation `collect_usage_state`, part 3).

The table has the columns `PID UID USER NAME`. A row is a snapshot of one running process.
`package` is set only when `NAME` has the shape of a package name (dotted identifier). That is the
whole rule: nothing in this output proves the name *is* an installed package (a secondary
process of a package can be named `<package>.persistent`), so the artifact says what it saw and
the later subject binding decides.
"""

import re

from app.core.constants import ParseStatus
from app.core.raw_sources import PS
from app.parsing.base import ParsedArtifact
from app.parsing.package_state._text import decode_failure, numbered_lines

ROW_ARTIFACT_TYPE = "running_process"
LIST_ARTIFACT_TYPE = "process_list"
_HEADER = re.compile(r"\s*PID\s+UID\s+USER\s+NAME\s*")
_ROW = re.compile(r"\s*(?P<pid>\d+)\s+(?P<uid>\d+)\s+(?P<user>\S+)\s+(?P<name>\S.*?)\s*")
_PACKAGE_SHAPE = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z0-9_]+)+")


class ProcessTableParser:
    operation_id = "collect_usage_state"
    parser_name = "usage_stats.ps"
    parser_version = "1"
    raw_source = PS

    def parse(self, raw: bytes) -> list[ParsedArtifact]:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            return [decode_failure(ROW_ARTIFACT_TYPE, self.parser_name, self.parser_version, error)]
        lines = [(no, line) for no, line in numbered_lines(text) if line.strip() != ""]
        if not lines:
            return [
                self._artifact(
                    LIST_ARTIFACT_TYPE,
                    None,
                    "",
                    {},
                    ParseStatus.empty,
                    "bukti tidak memuat keluaran",
                )
            ]
        if _HEADER.fullmatch(lines[0][1]) is None:
            return [
                self._artifact(
                    LIST_ARTIFACT_TYPE,
                    None,
                    lines[0][1],
                    {},
                    ParseStatus.failed,
                    "kepala kolom bukan 'PID UID USER NAME'",
                )
            ]
        rows = [self._row(number, line) for number, line in lines[1:]]
        count = sum(1 for row in rows if row.parse_status == ParseStatus.parsed)
        return [
            self._artifact(
                LIST_ARTIFACT_TYPE,
                None,
                lines[0][1],
                {"count": count},
                ParseStatus.parsed,
                "",
            ),
            *rows,
        ]

    def _row(self, number: int, line: str) -> ParsedArtifact:
        match = _ROW.fullmatch(line)
        if match is None:
            return self._artifact(
                ROW_ARTIFACT_TYPE,
                None,
                line,
                {"line_no": number},
                ParseStatus.failed,
                "baris tidak sesuai bentuk <PID> <UID> <USER> <NAME>",
            )
        name = match["name"]
        package = name if _PACKAGE_SHAPE.fullmatch(name) else None
        return self._artifact(
            ROW_ARTIFACT_TYPE,
            package,
            line,
            {
                "pid": int(match["pid"]),
                "uid": int(match["uid"]),
                "user": match["user"],
                "name": name,
                "package": package,
                "line_no": number,
            },
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
