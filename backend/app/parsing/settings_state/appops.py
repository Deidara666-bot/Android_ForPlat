"""Parser for the overlay (draw over other apps) app-op of one package.

The output never names the package, so the subject comes from the operation's `package_name`
parameter (`uses_parameters`); without a valid one nothing is bound and the result is `failed`.

Two shapes are known: an entry line `SYSTEM_ALERT_WINDOW: <mode>[; ...]`, and the pair
`No operations.` + `Default mode: <mode>` (no per-package entry exists). Any other line, including
a uid-level override line, is a `failed` artifact that keeps the original text.
"""

import re
from collections.abc import Mapping

from app.core.constants import ParseStatus
from app.core.raw_sources import APPOPS_OVERLAY
from app.parsing.base import ParsedArtifact
from app.parsing.package_state._text import decode_failure, numbered_lines

ARTIFACT_TYPE = "overlay_app_op"
_PACKAGE_NAME = re.compile(r"[A-Za-z0-9_.]{1,200}")
_MODES = "allow|ignore|deny|default"
_ENTRY = re.compile(rf"SYSTEM_ALERT_WINDOW: (?P<mode>{_MODES})(?:;.*)?")
_NO_OPERATIONS = "No operations."
_DEFAULT_MODE = re.compile(rf"Default mode: (?P<mode>{_MODES})")


class AppOpsOverlayParser:
    operation_id = "collect_accessibility_state"
    parser_name = "settings_state.appops"
    parser_version = "1"
    raw_source = APPOPS_OVERLAY
    uses_parameters = True

    def parse(
        self, raw: bytes, parameters: Mapping[str, str] | None = None
    ) -> list[ParsedArtifact]:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            return [decode_failure(ARTIFACT_TYPE, self.parser_name, self.parser_version, error)]
        package = (parameters or {}).get("package_name")
        if package is None or _PACKAGE_NAME.fullmatch(package) is None:
            return [
                self._artifact(
                    None,
                    "",
                    {},
                    ParseStatus.failed,
                    "paket subjek tidak diketahui: package_name tidak ada atau tidak valid",
                )
            ]
        lines = [(no, line) for no, line in numbered_lines(text) if line != ""]
        if not lines:
            return [
                self._artifact(
                    package, "", {}, ParseStatus.empty, "bukti tidak memuat baris app-op"
                )
            ]

        texts = [line for _, line in lines]
        if len(lines) == 1 and (entry := _ENTRY.fullmatch(texts[0])):
            return [self._parsed(package, texts[0], entry["mode"], "package_mode")]
        if (
            len(lines) == 2
            and texts[0] == _NO_OPERATIONS
            and (default := _DEFAULT_MODE.fullmatch(texts[1]))
        ):
            return [self._parsed(package, "\n".join(texts), default["mode"], "default_mode")]
        return [
            self._artifact(
                package,
                line,
                {"line_no": no},
                ParseStatus.failed,
                "baris tidak sesuai bentuk app-op yang dikenal",
            )
            for no, line in lines
        ]

    def _parsed(self, package: str, raw: str, mode: str, source: str) -> ParsedArtifact:
        return self._artifact(
            package,
            raw,
            {"package": package, "mode": mode, "mode_source": source},
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
