import re

from app.core.constants import ParseStatus
from app.parsing.base import ParsedArtifact
from app.parsing.package_state._text import decode_failure, numbered_lines

_PROPERTY = re.compile(r"\[(?P<key>[^\]]+)\]: \[(?P<value>.*)\]")
_KEYS = (
    "ro.build.version.release",
    "ro.build.version.sdk",
    "ro.build.fingerprint",
    "persist.sys.timezone",
)


class DeviceMetadataParser:
    operation_id = "collect_device_metadata"
    parser_name = "package_state.device_metadata"
    parser_version = "1"
    artifact_type = "device_build_property"

    def parse(self, raw: bytes) -> list[ParsedArtifact]:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            return [
                decode_failure(self.artifact_type, self.parser_name, self.parser_version, error)
            ]

        found: dict[str, tuple[str, str]] = {}
        for _, line in numbered_lines(text):
            match = _PROPERTY.fullmatch(line)
            if match is not None and match["key"] in _KEYS:
                found.setdefault(match["key"], (line, match["value"]))

        artifacts: list[ParsedArtifact] = []
        for key in _KEYS:
            if key in found:
                line, value = found[key]
                artifacts.append(
                    self._artifact(key, line, {"key": key, "value": value}, ParseStatus.parsed, "")
                )
            else:
                artifacts.append(
                    self._artifact(
                        key,
                        "",
                        {"key": key},
                        ParseStatus.empty,
                        f"kunci {key} tidak ada dalam keluaran",
                    )
                )
        return artifacts

    def _artifact(
        self,
        subject_key: str,
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
