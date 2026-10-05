"""Parser for the usage-stats event list (operation `collect_usage_state`, part 1).

Only the per-user `Last 24 hour events` list is read: one `usage_event` artifact per event line
(every event type is kept, none is dropped), plus one `usage_event_list` artifact per user block
as proof that the whole list was read. The aggregated sections (daily/weekly/monthly stats) are
not parsed here; they stay in the raw evidence file.

The `time="..."` text is the device's local wall-clock time without a zone. The parser keeps it
as printed (`local_time`); turning it into UTC needs the session timezone and is the
normalizer's job.
"""

import re
from datetime import datetime

from app.core.constants import ParseStatus
from app.core.raw_sources import DUMPSYS_USAGESTATS
from app.parsing.base import ParsedArtifact
from app.parsing.package_state._text import decode_failure, numbered_lines

EVENT_ARTIFACT_TYPE = "usage_event"
LIST_ARTIFACT_TYPE = "usage_event_list"
_USER = re.compile(r"user=(?P<user>\d+)\s*")
_SECTION = "  Last 24 hour events ("
_EVENT = re.compile(
    r'    time="(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})" '
    r"type=(?P<type>[A-Z][A-Z0-9_]*) package=(?P<package>[A-Za-z0-9_.]+)(?P<rest>(?: .*)?)"
)
_CLASS = re.compile(r"(?:^| )class=(?P<class>\S+)")


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


class UsageStatsParser:
    operation_id = "collect_usage_state"
    parser_name = "usage_stats.usagestats"
    parser_version = "1"
    raw_source = DUMPSYS_USAGESTATS

    def parse(self, raw: bytes) -> list[ParsedArtifact]:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            return [
                decode_failure(EVENT_ARTIFACT_TYPE, self.parser_name, self.parser_version, error)
            ]
        lines = numbered_lines(text)
        if all(line.strip() == "" for _, line in lines):
            note = "bukti tidak memuat keluaran usagestats"
            return [self._artifact(LIST_ARTIFACT_TYPE, None, "", {}, ParseStatus.empty, note)]

        blocks = [(user, events) for user, events in self._user_blocks(lines) if events is not None]
        if not blocks:
            return [
                self._artifact(
                    LIST_ARTIFACT_TYPE,
                    None,
                    lines[0][1],
                    {},
                    ParseStatus.failed,
                    "bagian 'Last 24 hour events' tidak ditemukan",
                )
            ]
        result: list[ParsedArtifact] = []
        for user, events in blocks:
            rows = [self._event(user, number, line) for number, line in events]
            count = sum(1 for row in rows if row.parse_status == ParseStatus.parsed)
            result.append(
                self._artifact(
                    LIST_ARTIFACT_TYPE,
                    None,
                    f"user={user}",
                    {"user": user, "count": count},
                    ParseStatus.parsed,
                    "",
                )
            )
            result.extend(rows)
        return result

    @staticmethod
    def _user_blocks(
        lines: list[tuple[int, str]],
    ) -> list[tuple[int, list[tuple[int, str]] | None]]:
        """Per `user=N` block: its event-list lines, or None when the block has no such list."""
        blocks: list[tuple[int, list[tuple[int, str]] | None]] = []
        in_events = False
        for number, line in lines:
            if line.strip() == "":
                continue
            indent = _indent(line)
            if indent == 0:
                match = _USER.fullmatch(line)
                in_events = False
                if match is None:
                    blocks.append((-1, None))  # another top-level section ends the user block
                    continue
                blocks.append((int(match["user"]), None))
                continue
            if not blocks or blocks[-1][0] < 0:
                continue
            if indent <= 2:
                in_events = line.startswith(_SECTION)
                if in_events:
                    blocks[-1] = (blocks[-1][0], [])
                continue
            events = blocks[-1][1]
            if in_events and events is not None:
                events.append((number, line))
        return [(user, events) for user, events in blocks if user >= 0]

    def _event(self, user: int, number: int, line: str) -> ParsedArtifact:
        match = _EVENT.fullmatch(line)
        if match is None:
            return self._artifact(
                EVENT_ARTIFACT_TYPE,
                None,
                line,
                {"line_no": number},
                ParseStatus.failed,
                "baris tidak sesuai bentuk event usagestats",
            )
        try:
            datetime.strptime(match["time"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return self._artifact(
                EVENT_ARTIFACT_TYPE,
                None,
                line,
                {"line_no": number},
                ParseStatus.failed,
                "waktu event bukan tanggal dan jam yang valid",
            )
        klass = _CLASS.search(match["rest"])
        return self._artifact(
            EVENT_ARTIFACT_TYPE,
            match["package"],
            line,
            {
                "user": user,
                "local_time": match["time"],
                "event": match["type"],
                "package": match["package"],
                "class": klass["class"] if klass else None,
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
