import re

from app.core.constants import ParseStatus
from app.parsing.base import ParsedArtifact
from app.parsing.package_state._text import decode_failure, numbered_lines

_LINE = re.compile(r"package:(?P<package>[A-Za-z0-9._]+) uid:(?P<uid>[0-9]+)")


class InventoryParser:
    operation_id = "collect_package_inventory"
    parser_name = "package_state.inventory"
    parser_version = "1"
    artifact_type = "package_inventory_entry"

    def parse(self, raw: bytes) -> list[ParsedArtifact]:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            return [
                decode_failure(self.artifact_type, self.parser_name, self.parser_version, error)
            ]

        artifacts: list[ParsedArtifact] = []
        for line_no, line in numbered_lines(text):
            if line == "":
                continue
            match = _LINE.fullmatch(line)
            if match is None:
                artifacts.append(
                    self._artifact(
                        None,
                        line,
                        {"line_no": line_no},
                        ParseStatus.failed,
                        "baris tidak sesuai bentuk package:<nama> uid:<angka>",
                    )
                )
                continue
            package = match["package"]
            artifacts.append(
                self._artifact(
                    package,
                    line,
                    {"package_name": package, "uid": int(match["uid"]), "line_no": line_no},
                    ParseStatus.parsed,
                    "",
                )
            )
        if not artifacts:
            return [
                self._artifact(None, "", {}, ParseStatus.empty, "bukti tidak memuat baris package")
            ]
        return artifacts

    def _artifact(
        self,
        subject_key: str | None,
        raw_value: str,
        parsed_value_json: dict[str, object],
        status: ParseStatus,
        note: str,
    ) -> ParsedArtifact:
        return ParsedArtifact(
            artifact_type=self.artifact_type,
            parser_name=self.parser_name,
            parser_version=self.parser_version,
            subject_key=subject_key,
            raw_value=raw_value,
            parsed_value_json=parsed_value_json,
            parse_status=status,
            parse_note=note,
        )
