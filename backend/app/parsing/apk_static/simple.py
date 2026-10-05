"""Parsers of the small bundle files: identity hash, badging, permissions, URL list, bundle.json."""

import json
import re
from datetime import datetime

from app.core import raw_sources
from app.parsing.apk_static._common import BundleParser
from app.parsing.base import ParsedArtifact

_SHA256 = re.compile(r"[0-9a-f]{64}")
_APK_NAME = re.compile(r"[A-Za-z0-9_.\-]{1,100}\.apk")
_SHA_LINE = re.compile(r"(?P<sha>[0-9a-f]{64})(?:  (?P<name>\S+))?")


class ApkIdentityParser(BundleParser):
    """`apk.sha256`: one `<sha256>  <file name>` line per APK, the base APK first (extractor 2);
    a single bare `<sha256>` line is the extractor 1 form. The identity is the first line's hash,
    the other lines are the splits."""

    parser_name = "apk_static.identity"
    parser_version = "2"
    raw_source = raw_sources.STATIC_APK_SHA256
    artifact_type = "apk_identity"

    def parse_text(
        self, text: str, lines: list[tuple[int, str]], package: str
    ) -> list[ParsedArtifact]:
        rows = [_SHA_LINE.fullmatch(line.strip()) for _, line in lines]
        if any(row is None for row in rows):
            return self.whole_failure(
                package, lines[0][1], "linha bukan '<sha256>  <nama berkas apk>'"
            )
        parsed = [(row["sha"], row["name"]) for row in rows if row is not None]
        if len(parsed) > 1 and any(name is None for _, name in parsed):
            return self.whole_failure(
                package, lines[0][1], "beberapa APK tetapi ada baris tanpa nama"
            )
        names = [name for _, name in parsed if name is not None]
        if any(_APK_NAME.fullmatch(name) is None for name in names) or len(set(names)) != len(
            names
        ):
            return self.whole_failure(
                package, lines[0][1], "nama berkas APK tidak valid atau ganda"
            )
        digest, base_name = parsed[0]
        splits = [{"name": name, "sha256": sha} for sha, name in parsed[1:]]
        return [
            self.artifact(
                self.artifact_type,
                package,
                digest,
                {
                    "package_name": package,
                    "sha256": digest,
                    "apk_name": base_name,
                    "splits": splits,
                },
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


_MANIFEST_KEYS_V1 = {"apk_sha256", "extractor_version", "tool_versions", "created_at", "files"}
_MANIFEST_KEYS_V2 = _MANIFEST_KEYS_V1 | {"apks", "scan"}


class ApkBundleManifestParser(BundleParser):
    """`bundle.json`: the extractor's own record; strict keys and value shapes."""

    parser_name = "apk_static.bundle"
    parser_version = "2"
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
        if not isinstance(data, dict) or set(data) not in (_MANIFEST_KEYS_V1, _MANIFEST_KEYS_V2):
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
        if "apks" in data:
            apks = data["apks"]
            if (
                not isinstance(apks, dict)
                or not apks
                or not all(isinstance(v, str) and _SHA256.fullmatch(v) for v in apks.values())
            ):
                return "apks bukan peta nama APK ke SHA-256"
            if data["apk_sha256"] != next(iter(apks.values())):
                return "apk_sha256 bukan hash APK pertama (base)"
            scan = data["scan"]
            if (
                not isinstance(scan, dict)
                or set(scan) != {"entri_terpotong"}
                or not isinstance(scan["entri_terpotong"], list)
                or not all(isinstance(item, dict) for item in scan["entri_terpotong"])
            ):
                return "scan bukan {entri_terpotong: [..]}"
        return None


_NATIVE_ENTRY = re.compile(r"lib/(?P<abi>[^/\s]+)/[^/\s]+\.so")
_DEX_ENTRY = re.compile(r"classes[0-9]*\.dex")
_DESCRIPTORS = frozenset(
    {
        "Ldalvik/system/DexClassLoader;",
        "Ldalvik/system/InMemoryDexClassLoader;",
        "Ldalvik/system/PathClassLoader;",
        "Ldalvik/system/DelegateLastClassLoader;",
    }
)


class ApkNativeLibraryParser(BundleParser):
    """`native_libs.txt`: `<apk>\t<lib/abi/name.so>\t<size>\t<sha256>` per native library. Context
    for the examiner: the APK contains the library, nothing about what it does or whether it ran."""

    parser_name = "apk_static.native_libs"
    raw_source = raw_sources.STATIC_NATIVE_LIBS
    artifact_type = "apk_native_library"

    def parse_text(
        self, text: str, lines: list[tuple[int, str]], package: str
    ) -> list[ParsedArtifact]:
        rows: list[ParsedArtifact] = []
        for number, line in lines:
            fields = line.rstrip("\r").split("\t")
            entry = _NATIVE_ENTRY.fullmatch(fields[1]) if len(fields) == 4 else None
            if (
                entry is None
                or _APK_NAME.fullmatch(fields[0]) is None
                or not fields[2].isdecimal()
                or _SHA256.fullmatch(fields[3]) is None
            ):
                rows.append(
                    self.failed_line(
                        self.artifact_type,
                        package,
                        number,
                        line,
                        "baris bukan '<apk>\\t<lib/abi/nama.so>\\t<ukuran>\\t<sha256>'",
                    )
                )
                continue
            value: dict[str, object] = {
                "apk": fields[0],
                "entry": fields[1],
                "abi": entry["abi"],
                "size": int(fields[2]),
                "sha256": fields[3],
                "line_no": number,
            }
            rows.append(self.artifact(self.artifact_type, package, line, value))
        return rows


class ApkCodeLoadingReferenceParser(BundleParser):
    """`api_refs.txt`: `<apk>\t<classes*.dex>\t<descriptor>` for the closed set of class-loader
    descriptors. A reference in a dex file is not evidence that code was loaded or run."""

    parser_name = "apk_static.api_refs"
    raw_source = raw_sources.STATIC_API_REFS
    artifact_type = "apk_code_loading_reference"

    def parse_text(
        self, text: str, lines: list[tuple[int, str]], package: str
    ) -> list[ParsedArtifact]:
        rows: list[ParsedArtifact] = []
        for number, line in lines:
            fields = line.rstrip("\r").split("\t")
            if (
                len(fields) != 3
                or _APK_NAME.fullmatch(fields[0]) is None
                or _DEX_ENTRY.fullmatch(fields[1]) is None
                or fields[2] not in _DESCRIPTORS
            ):
                rows.append(
                    self.failed_line(
                        self.artifact_type,
                        package,
                        number,
                        line,
                        "baris bukan '<apk>\\t<classes.dex>\\t<descriptor tertutup>'",
                    )
                )
                continue
            value: dict[str, object] = {
                "apk": fields[0],
                "entry": fields[1],
                "descriptor": fields[2],
                "line_no": number,
            }
            rows.append(self.artifact(self.artifact_type, package, line, value))
        return rows
