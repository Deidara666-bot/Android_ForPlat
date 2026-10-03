"""Parsers of the small bundle files: identity hash, badging, permissions, URL list, bundle.json."""

import json
import re
from datetime import datetime

from app.core import raw_sources
from app.parsing.apk_static._common import BundleParser
from app.parsing.base import ParsedArtifact

_SHA256 = re.compile(r"[0-9a-f]{64}")


class ApkIdentityParser(BundleParser):
    """`apk.sha256`: one line, the lowercase hex SHA-256 of the APK."""

    parser_name = "apk_static.identity"
    raw_source = raw_sources.STATIC_APK_SHA256
    artifact_type = "apk_identity"

    def parse_text(
        self, text: str, lines: list[tuple[int, str]], package: str
    ) -> list[ParsedArtifact]:
        if len(lines) != 1 or _SHA256.fullmatch(lines[0][1].strip()) is None:
            return self.whole_failure(
                package, lines[0][1], "isi bukan satu baris SHA-256 heksadesimal"
            )
        digest = lines[0][1].strip()
        return [
            self.artifact(
                self.artifact_type, package, digest, {"package_name": package, "sha256": digest}
            )
        ]


_BADGING_PACKAGE = re.compile(r"package: (?P<attrs>name='[^']*'.*)")
_ATTRIBUTE = re.compile(r"(?P<key>[A-Za-z]+)='(?P<value>[^']*)'")
_SDK = re.compile(r"(?P<key>minSdkVersion|targetSdkVersion):'(?P<value>[^']*)'")


class ApkBadgingParser(BundleParser):
    """`badging.txt`: identity and SDK levels from the first lines; the rest (labels, locales,
    densities) stays in the raw evidence."""

    parser_name = "apk_static.badging"
    raw_source = raw_sources.STATIC_BADGING
    artifact_type = "apk_badging"

    def parse_text(
        self, text: str, lines: list[tuple[int, str]], package: str
    ) -> list[ParsedArtifact]:
        first = _BADGING_PACKAGE.fullmatch(lines[0][1])
        if first is None:
            return self.whole_failure(
                package, lines[0][1], "baris pertama bukan 'package: name=...'"
            )
        attributes = {m["key"]: m["value"] for m in _ATTRIBUTE.finditer(first["attrs"])}
        if attributes.get("name") != package:
            return self.whole_failure(
                package,
                lines[0][1],
                f"paket pada badging ({attributes.get('name')}) tidak sama dengan parameter",
            )
        sdk = {m["key"]: m["value"] for _, line in lines[1:] if (m := _SDK.fullmatch(line))}
        code = attributes.get("versionCode", "")
        value: dict[str, object] = {
            "package_name": package,
            "version_code": int(code) if code.isdigit() else None,
            "version_name": attributes.get("versionName"),
            "min_sdk": int(sdk["minSdkVersion"])
            if sdk.get("minSdkVersion", "").isdigit()
            else None,
            "target_sdk": (
                int(sdk["targetSdkVersion"]) if sdk.get("targetSdkVersion", "").isdigit() else None
            ),
        }
        return [self.artifact(self.artifact_type, package, lines[0][1], value)]


_PERMISSIONS_PACKAGE = re.compile(r"package: (?P<name>[A-Za-z0-9_.]+)")
_USES = re.compile(
    r"uses-permission(?P<variant>-sdk-\w+)?: name='(?P<name>[A-Za-z0-9_.$]+)'"
    r"(?: maxSdkVersion='(?P<max>\d+)')?"
)
_DECLARED = re.compile(r"permission: (?P<name>[A-Za-z0-9_.$]+)")


class ApkPermissionsParser(BundleParser):
    """`permissions.txt`: requested (`uses-permission`) and declared (`permission`) names."""

    parser_name = "apk_static.permissions"
    raw_source = raw_sources.STATIC_PERMISSIONS
    artifact_type = "apk_permission"

    def parse_text(
        self, text: str, lines: list[tuple[int, str]], package: str
    ) -> list[ParsedArtifact]:
        head = _PERMISSIONS_PACKAGE.fullmatch(lines[0][1])
        if head is None:
            return self.whole_failure(package, lines[0][1], "baris pertama bukan 'package: <nama>'")
        if head["name"] != package:
            return self.whole_failure(
                package,
                lines[0][1],
                f"paket pada berkas ({head['name']}) tidak sama dengan parameter",
            )
        rows: list[ParsedArtifact] = []
        seen: set[tuple[str, str, str | None]] = set()
        for number, line in lines[1:]:
            used, declared = _USES.fullmatch(line), _DECLARED.fullmatch(line)
            if used:
                role, name, variant = "requested", used["name"], used["variant"]
                extra: dict[str, object] = {
                    "max_sdk": int(used["max"]) if used["max"] else None,
                    "variant": variant,
                }
            elif declared:
                role, name, variant = "declared", declared["name"], None
                extra = {"max_sdk": None, "variant": None}
            else:
                rows.append(
                    self.failed_line(
                        self.artifact_type, package, number, line, "baris izin tidak dikenal"
                    )
                )
                continue
            key = (role, name, variant)
            if key in seen:
                continue  # the tool prints some permissions twice; one artifact per permission
            seen.add(key)
            rows.append(
                self.artifact(
                    self.artifact_type,
                    package,
                    line,
                    {"name": name, "role": role, "line_no": number, **extra},
                )
            )
        return rows


_URL_LINE = re.compile(r"(?:https?|wss?|ftp)://\S+")
_IPV4_LINE = re.compile(
    r"(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
)


class ApkEndpointReferenceParser(BundleParser):
    """`strings_urls.txt`: one URL or IPv4 string per line. A string in an APK is a reference,
    never evidence that anything was contacted."""

    parser_name = "apk_static.strings"
    raw_source = raw_sources.STATIC_STRINGS_URLS
    artifact_type = "apk_endpoint_reference"

    def parse_text(
        self, text: str, lines: list[tuple[int, str]], package: str
    ) -> list[ParsedArtifact]:
        rows: list[ParsedArtifact] = []
        for number, line in lines:
            value = line.strip()
            if _URL_LINE.fullmatch(value):
                kind = "url"
            elif _IPV4_LINE.fullmatch(value):
                kind = "ip"
            else:
                rows.append(
                    self.failed_line(
                        self.artifact_type,
                        package,
                        number,
                        line,
                        "baris bukan URL atau alamat IPv4",
                    )
                )
                continue
            rows.append(
                self.artifact(
                    self.artifact_type,
                    package,
                    line,
                    {"value": value, "kind": kind, "line_no": number},
                )
            )
        return rows


_MANIFEST_KEYS = {"apk_sha256", "extractor_version", "tool_versions", "created_at", "files"}


class ApkBundleManifestParser(BundleParser):
    """`bundle.json`: the extractor's own record; strict keys and value shapes."""

    parser_name = "apk_static.bundle"
    raw_source = raw_sources.STATIC_BUNDLE_JSON
    artifact_type = "apk_bundle_manifest"

    def parse_text(
        self, text: str, lines: list[tuple[int, str]], package: str
    ) -> list[ParsedArtifact]:
        first = lines[0][1]
        try:
            data = json.loads(text)
        except ValueError:
            return self.whole_failure(package, first, "bukan JSON yang valid")
        problem = self._problem(data)
        if problem is not None:
            return self.whole_failure(package, first, problem)
        return [self.artifact(self.artifact_type, package, text.strip(), dict(data))]

    @staticmethod
    def _problem(data: object) -> str | None:
        if not isinstance(data, dict) or set(data) != _MANIFEST_KEYS:
            return "kunci bundle.json tidak sama dengan yang diharapkan"
        if not isinstance(data["apk_sha256"], str) or not _SHA256.fullmatch(data["apk_sha256"]):
            return "apk_sha256 bukan SHA-256 heksadesimal"
        if not isinstance(data["extractor_version"], str) or not data["extractor_version"]:
            return "extractor_version kosong"
        versions = data["tool_versions"]
        if not isinstance(versions, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in versions.items()
        ):
            return "tool_versions bukan peta teks"
        try:
            stamp = datetime.fromisoformat(str(data["created_at"]))
        except ValueError:
            return "created_at bukan waktu ISO"
        if stamp.tzinfo is None:
            return "created_at tanpa zona waktu"
        files = data["files"]
        if not isinstance(files, dict) or not all(
            isinstance(v, str) and _SHA256.fullmatch(v) for v in files.values()
        ):
            return "files bukan peta nama ke SHA-256"
        return None
