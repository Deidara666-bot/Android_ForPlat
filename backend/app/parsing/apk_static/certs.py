"""Parser for the signer-certificate listing (`certs.txt`).

One `apk_certificate` artifact per signer. When the extractor recorded a failed verification
(a `# apksigner exit code: N` marker and the tool's error lines after it), that is kept as
`verification_ok: false` with the text, not as a parse failure: the file was read completely.
"""

import re

from app.core import raw_sources
from app.core.constants import ParseStatus
from app.parsing.apk_static._common import BundleParser
from app.parsing.base import ParsedArtifact

_SIGNER = re.compile(
    r"Signer #(?P<n>\d+) certificate (?P<what>DN|SHA-256 digest|SHA-1 digest|MD5 digest): "
    r"(?P<value>.+)"
)
_MARKER = re.compile(r"# apksigner exit code: (?P<code>-?\d+)")
_FIELDS = {"DN": "dn", "SHA-256 digest": "sha256", "SHA-1 digest": "sha1", "MD5 digest": "md5"}
_DIGEST = {"sha256": 64, "sha1": 40, "md5": 32}


class ApkCertificateParser(BundleParser):
    parser_name = "apk_static.certs"
    raw_source = raw_sources.STATIC_CERTS
    artifact_type = "apk_certificate"

    def parse_text(
        self, text: str, lines: list[tuple[int, str]], package: str
    ) -> list[ParsedArtifact]:
        signers: dict[int, dict[str, object]] = {}
        raws: dict[int, list[str]] = {}
        rows: list[ParsedArtifact] = []
        failure_code: int | None = None
        failure_text: list[str] = []
        for number, line in lines:
            if failure_code is not None:
                failure_text.append(line.strip())  # everything after the marker is the tool's text
                continue
            marker = _MARKER.fullmatch(line.strip())
            if marker:
                failure_code = int(marker["code"])
                continue
            match = _SIGNER.fullmatch(line.strip())
            if match is None:
                rows.append(
                    self.failed_line(
                        self.artifact_type, package, number, line, "baris sertifikat tidak dikenal"
                    )
                )
                continue
            signer = int(match["n"])
            field_name = _FIELDS[match["what"]]
            value = match["value"].strip()
            if field_name in _DIGEST and not re.fullmatch(
                rf"[0-9a-f]{{{_DIGEST[field_name]}}}", value
            ):
                rows.append(
                    self.failed_line(
                        self.artifact_type,
                        package,
                        number,
                        line,
                        f"{field_name} bukan heksadesimal",
                    )
                )
                continue
            signers.setdefault(signer, {})[field_name] = value
            raws.setdefault(signer, []).append(line.strip())

        verification: dict[str, object] = {"verification_ok": failure_code is None}
        if failure_code is not None:
            verification |= {
                "verification_exit_code": failure_code,
                "verification_note": "\n".join(failure_text),
            }
        result: list[ParsedArtifact] = []
        for signer, fields in sorted(signers.items()):
            if "sha256" not in fields:
                rows.append(
                    self.artifact(
                        self.artifact_type,
                        package,
                        "\n".join(raws[signer]),
                        {"signer": signer},
                        ParseStatus.failed,
                        "tanda tangan tanpa SHA-256",
                    )
                )
                continue
            result.append(
                self.artifact(
                    self.artifact_type,
                    package,
                    "\n".join(raws[signer]),
                    {"signer": signer, **fields, **verification},
                )
            )
        if not result and not rows and failure_code is not None:
            result.append(
                self.artifact(
                    self.artifact_type,
                    package,
                    f"# apksigner exit code: {failure_code}",
                    {"signer": None, **verification},
                )
            )
        return result + rows
