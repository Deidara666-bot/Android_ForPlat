"""Shared base of the bundle-file parsers (operation `pull_subject_apk`, parts 3 and up).

Each bundle file has its own parser, registered under `(pull_subject_apk, static:<file>)`.
The subject of every artifact is the operation's `package_name` parameter: a bundle file never
decides which package it is about. Files that name their own package (badging, permissions,
manifest) must agree with the parameter, otherwise the whole file is `failed` and nothing in it
is used.
"""

import re
from collections.abc import Mapping

from app.core.constants import ParseStatus
from app.parsing.base import ParsedArtifact
from app.parsing.package_state._text import decode_failure, numbered_lines

OPERATION_ID = "pull_subject_apk"
_PACKAGE_NAME = re.compile(r"[A-Za-z0-9_.]{1,200}")


class BundleParser:
    """Subclasses set the class attributes and implement `parse_lines`."""

    operation_id = OPERATION_ID
    parser_version = "1"
    uses_parameters = True
    parser_name: str
    raw_source: str
    artifact_type: str  # type of the failure/empty artifacts of this file

    def parse(
        self, raw: bytes, parameters: Mapping[str, str] | None = None
    ) -> list[ParsedArtifact]:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            return [
                decode_failure(self.artifact_type, self.parser_name, self.parser_version, error)
            ]
        package = (parameters or {}).get("package_name")
        if package is None or _PACKAGE_NAME.fullmatch(package) is None:
            return [
                self.artifact(
                    self.artifact_type,
                    None,
                    "",
                    {},
                    ParseStatus.failed,
                    "paket subjek tidak diketahui: package_name tidak ada atau tidak valid",
                )
            ]
        lines = [(no, line) for no, line in numbered_lines(text) if line.strip() != ""]
        if not lines:
            return [
                self.artifact(
                    self.artifact_type,
                    package,
                    "",
                    {},
                    ParseStatus.empty,
                    "bukti tidak memuat isi",
                )
            ]
        return self.parse_text(text, lines, package)

    def parse_text(
        self, text: str, lines: list[tuple[int, str]], package: str
    ) -> list[ParsedArtifact]:
        raise NotImplementedError

    def artifact(
        self,
        artifact_type: str,
        subject_key: str | None,
        raw_value: str,
        parsed_value_json: dict[str, object],
        status: ParseStatus = ParseStatus.parsed,
        note: str = "",
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

    def failed_line(
        self, artifact_type: str, package: str | None, number: int, line: str, note: str
    ) -> ParsedArtifact:
        return self.artifact(
            artifact_type, package, line, {"line_no": number}, ParseStatus.failed, note
        )

    def whole_failure(self, package: str, first_line: str, note: str) -> list[ParsedArtifact]:
        """One failed artifact for a file whose structure or package is not the expected one."""
        return [
            self.artifact(self.artifact_type, package, first_line, {}, ParseStatus.failed, note)
        ]
