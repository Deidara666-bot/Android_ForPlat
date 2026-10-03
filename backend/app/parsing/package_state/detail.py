"""Parser for `dumpsys package <pkg>` (operation `collect_package_detail`).

Strict by design: if the output does not have the structure this parser knows, the result is one
`failed` artifact and nothing is read partially. Inside a recognised section, a line that does not
fit its expected shape becomes a `failed` artifact that keeps the original line.

Only these parts of the output become artifacts; the rest stays in the raw evidence file:
identity keys of the `Package [<name>]` block, its requested/install/runtime permissions (plus the
permissions of its shared user), and the components that appear in the four resolver tables.
A component with no intent filter is not printed by dumpsys, so `component_declared` is a list of
the components that dumpsys shows, not a complete manifest.
"""

import re
from dataclasses import dataclass, field

from app.core.constants import ParseStatus
from app.parsing.base import ParsedArtifact
from app.parsing.package_state._text import decode_failure, numbered_lines

_PACKAGE_HEADER = re.compile(r"  Package \[(?P<name>[^\]]+)\] \((?P<hash>[0-9a-f]+)\):")
_SHARED_HEADER = re.compile(r"  SharedUser \[(?P<label>[^\]]+)\] \((?P<hash>[0-9a-f]+)\):")
_SHARED_REF = re.compile(r"SharedUserSetting\{\S+ (?P<label>\S+)/\d+\}")
_KEY_VALUE = re.compile(r"    (?P<key>[A-Za-z][A-Za-z0-9]*)=(?P<value>.*)")
_SIGNATURES = re.compile(r"signatures:\[(?P<items>[^\]]*)\]")
_PERMISSION_NAME = re.compile(r"      (?P<name>[A-Za-z0-9_.$]+)")
_INSTALL_PERMISSION = re.compile(
    r"      (?P<name>[A-Za-z0-9_.$]+): granted=(?P<granted>true|false)(?:, flags=\[.*\])?"
)
_RUNTIME_PERMISSION = re.compile(
    r"        (?P<name>[A-Za-z0-9_.$]+): granted=(?P<granted>true|false)(?:, flags=\[.*\])?"
)
_ENTRY = re.compile(
    r"        (?P<hash>[0-9a-f]+) (?P<name>[A-Za-z0-9_.$]+/\S+) filter (?P<filter>[0-9a-f]+)"
    r"(?: permission (?P<permission>[A-Za-z0-9_.$]+))?"
)
_ACTION = re.compile(r'          Action: "(?P<action>[^"]+)"')
_GROUPS = frozenset(
    {
        "Schemes:",
        "Full MIME Types:",
        "Base MIME Types:",
        "Wild MIME Types:",
        "Non-Data Actions:",
        "MIME Typed Actions:",
    }
)
# Detail lines of an intent filter that carry no field this parser keeps.
_FILTER_DETAIL_PREFIXES = (
    "Category:",
    "Scheme:",
    "Authority:",
    "Path:",
    "Type:",
    "StaticType:",
    "mPriority=",
    "AutoVerify=",
)
_TABLES = {
    "Activity Resolver Table:": "activity",
    "Receiver Resolver Table:": "receiver",
    "Service Resolver Table:": "service",
    "Provider Resolver Table:": "provider",
}
_IDENTITY_TYPE = "package_identity"
_REQUIRED_KEYS = ("versionCode", "versionName")


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


@dataclass
class _Context:
    package: str
    rows: list[ParsedArtifact] = field(default_factory=list)

    def add(
        self,
        artifact_type: str,
        raw: str,
        value: dict[str, object],
        status: ParseStatus = ParseStatus.parsed,
        note: str = "",
    ) -> None:
        self.rows.append(
            ParsedArtifact(
                artifact_type=artifact_type,
                parser_name=PackageDetailParser.parser_name,
                parser_version=PackageDetailParser.parser_version,
                subject_key=self.package,
                raw_value=raw,
                parsed_value_json=value,
                parse_status=status,
                parse_note=note,
            )
        )

    def failed_line(self, artifact_type: str, number: int, line: str, note: str) -> None:
        self.add(artifact_type, line, {"line_no": number}, ParseStatus.failed, note)


def _sections(lines: list[tuple[int, str]]) -> list[tuple[str, list[tuple[int, str]]]]:
    """Top-level sections (indent 0 header, body until the next header), blank lines dropped."""
    result: list[tuple[str, list[tuple[int, str]]]] = []
    for number, line in lines:
        if line.strip() == "":
            continue
        if _indent(line) == 0:
            result.append((line, []))
        elif result:
            result[-1][1].append((number, line))
    return result


def _blocks(
    body: list[tuple[int, str]], header: re.Pattern[str]
) -> list[tuple[re.Match[str] | None, list[tuple[int, str]]]]:
    """Indent-2 blocks of a section; the match is None for an indent-2 line of another shape."""
    blocks: list[tuple[re.Match[str] | None, list[tuple[int, str]]]] = []
    for number, line in body:
        if _indent(line) == 2:
            blocks.append((header.fullmatch(line), []))
        elif blocks:
            blocks[-1][1].append((number, line))
    return blocks


class PackageDetailParser:
    operation_id = "collect_package_detail"
    parser_name = "package_state.detail"
    parser_version = "1"

    def parse(self, raw: bytes) -> list[ParsedArtifact]:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as error:
            return [decode_failure(_IDENTITY_TYPE, self.parser_name, self.parser_version, error)]
        lines = numbered_lines(text)
        if all(line.strip() == "" for _, line in lines):
            return [self._whole("", ParseStatus.empty, "bukti tidak memuat keluaran dumpsys")]
        if lines[0][1].startswith("Unable to find package:"):
            return [
                self._whole(
                    lines[0][1], ParseStatus.failed, "dumpsys melaporkan paket tidak ditemukan"
                )
            ]

        sections = _sections(lines)
        packages = [body for header, body in sections if header == "Packages:"]
        if len(packages) != 1:
            return [self._whole(lines[0][1], ParseStatus.failed, "bagian Packages tidak ditemukan")]
        blocks = _blocks(packages[0], _PACKAGE_HEADER)
        if len(blocks) != 1 or blocks[0][0] is None:
            return [
                self._whole(
                    lines[0][1],
                    ParseStatus.failed,
                    f"bagian Packages tidak memuat tepat satu blok Package ({len(blocks)})",
                )
            ]
        header, body = blocks[0]
        assert header is not None
        package = header["name"]
        keys = self._keys(body)
        missing = [k for k in _REQUIRED_KEYS if k not in keys]
        if "appId" not in keys and "userId" not in keys:
            missing.insert(0, "appId")
        if missing:
            return [
                self._whole(
                    packages[0][0][1],
                    ParseStatus.failed,
                    "kunci identitas tidak ada: " + ", ".join(missing),
                    package,
                )
            ]
        user_key = "appId" if "appId" in keys else "userId"
        try:
            int(keys["versionCode"][0].split()[0])
            int(keys[user_key][0].split()[0])
        except (ValueError, IndexError):
            return [
                self._whole(
                    packages[0][0][1],
                    ParseStatus.failed,
                    "versionCode atau appId bukan angka",
                    package,
                )
            ]

        ctx = _Context(package)
        self._identity(ctx, header.group(0), keys, body)
        self._permissions(ctx, body, sections, keys)
        tables = {head: tbody for head, tbody in sections if head in _TABLES}
        self._components(ctx, tables)
        return ctx.rows

    def _whole(
        self, raw: str, status: ParseStatus, note: str, package: str | None = None
    ) -> ParsedArtifact:
        return ParsedArtifact(
            artifact_type=_IDENTITY_TYPE,
            parser_name=self.parser_name,
            parser_version=self.parser_version,
            subject_key=package,
            raw_value=raw,
            parsed_value_json={},
            parse_status=status,
            parse_note=note,
        )

    @staticmethod
    def _keys(body: list[tuple[int, str]]) -> dict[str, tuple[str, str]]:
        """First `key=value` line per key at the block's own level (indent 4): value, raw line."""
        keys: dict[str, tuple[str, str]] = {}
        for _, line in body:
            match = _KEY_VALUE.fullmatch(line)
            if match and match["key"] not in keys:
                keys[match["key"]] = (match["value"], line)
        return keys

    def _identity(
        self,
        ctx: _Context,
        header_line: str,
        keys: dict[str, tuple[str, str]],
        body: list[tuple[int, str]],
    ) -> None:
        user_key = "appId" if "appId" in keys else "userId"
        first_install = next(
            (line for _, line in self._user0(body) if line.startswith("      firstInstallTime=")),
            None,
        )
        raw_lines = [header_line] + [
            keys[k][1]
            for k in (user_key, "versionCode", "versionName", "lastUpdateTime", "signatures")
            if k in keys
        ]
        if "installerPackageName" in keys:
            raw_lines.append(keys["installerPackageName"][1])
        if first_install is not None:
            raw_lines.append(first_install)

        signatures: list[str] = []
        if "signatures" in keys:
            found = _SIGNATURES.search(keys["signatures"][0])
            if found:
                signatures = [s.strip() for s in found["items"].split(",") if s.strip()]

        def text_or_none(key: str) -> str | None:
            value = keys[key][0].strip() if key in keys else None
            return None if value in (None, "", "null") else value

        ctx.add(
            _IDENTITY_TYPE,
            "\n".join(raw_lines),
            {
                "package_name": ctx.package,
                "version_name": keys["versionName"][0],
                "version_code": int(keys["versionCode"][0].split()[0]),
                "user_id": int(keys[user_key][0].split()[0]),
                # Device-local wall-clock text exactly as printed; never converted to UTC.
                "first_install_time": (
                    first_install.split("=", 1)[1].strip() if first_install else None
                ),
                "last_update_time": text_or_none("lastUpdateTime"),
                "installer_package_name": text_or_none("installerPackageName"),
                "signatures": signatures,
            },
        )

    @staticmethod
    def _user0(body: list[tuple[int, str]]) -> list[tuple[int, str]]:
        """Lines of the `    User 0:` sub-block (indent > 4 until the next indent-4 line)."""
        inside = False
        result: list[tuple[int, str]] = []
        for number, line in body:
            if _indent(line) == 4:
                inside = line.startswith("    User 0:")
            elif inside:
                result.append((number, line))
        return result

    def _permissions(
        self,
        ctx: _Context,
        body: list[tuple[int, str]],
        sections: list[tuple[str, list[tuple[int, str]]]],
        keys: dict[str, tuple[str, str]],
    ) -> None:
        context = "requested"
        for number, line in body:
            if _indent(line) == 4:
                context = "requested" if line == "    requested permissions:" else ""
                continue
            if context == "requested" and _indent(line) >= 6:
                match = _PERMISSION_NAME.fullmatch(line)
                if match is None:
                    ctx.failed_line(
                        "requested_permission",
                        number,
                        line,
                        "baris tidak sesuai bentuk <nama izin>",
                    )
                else:
                    ctx.add(
                        "requested_permission",
                        line,
                        {"name": match["name"], "line_no": number},
                    )

        seen: set[tuple[str, str]] = set()
        self._granted(ctx, body, "package", seen)
        if "sharedUser" in keys:
            ref = _SHARED_REF.search(keys["sharedUser"][0])
            shared = None
            if ref is not None:
                for head, section_body in sections:
                    if head != "Shared users:":
                        continue
                    for match, block in _blocks(section_body, _SHARED_HEADER):
                        if match is not None and match["label"] == ref["label"]:
                            shared = block
            if shared is None:
                ctx.add(
                    "granted_permission",
                    keys["sharedUser"][1],
                    {},
                    ParseStatus.failed,
                    "paket memakai shared user tetapi blok SharedUser-nya tidak ditemukan",
                )
            else:
                self._granted(ctx, shared, "shared_user", seen)

    def _granted(
        self,
        ctx: _Context,
        body: list[tuple[int, str]],
        scope: str,
        seen: set[tuple[str, str]],
    ) -> None:
        """Install and runtime permissions of one block. The package's own entry wins over the
        same permission listed again for its shared user."""
        context = ""
        for number, line in body:
            indent = _indent(line)
            if indent == 4:
                context = "install" if line == "    install permissions:" else ""
                if line.startswith("    User 0:"):
                    context = "user0"
                continue
            if context.startswith("user0") and indent == 6:
                context = "user0-runtime" if line == "      runtime permissions:" else "user0"
                continue
            if context == "install" and indent >= 6:
                pattern, kind = _INSTALL_PERMISSION, "install"
            elif context == "user0-runtime" and indent >= 8:
                pattern, kind = _RUNTIME_PERMISSION, "runtime"
            else:
                continue
            match = pattern.fullmatch(line)
            if match is None:
                ctx.failed_line(
                    "granted_permission",
                    number,
                    line,
                    "baris tidak sesuai bentuk <nama izin>: granted=<true|false>",
                )
                continue
            key = (match["name"], kind)
            if key in seen:
                continue
            seen.add(key)
            ctx.add(
                "granted_permission",
                line,
                {
                    "name": match["name"],
                    "granted": match["granted"] == "true",
                    "kind": kind,
                    "scope": scope,
                    "line_no": number,
                },
            )

    def _components(self, ctx: _Context, tables: dict[str, list[tuple[int, str]]]) -> None:
        seen_components: set[tuple[str, str, str | None]] = set()
        seen_actions: set[tuple[str, str]] = set()
        for header, kind in _TABLES.items():
            current: str | None = None
            for number, line in tables.get(header, []):
                indent = _indent(line)
                if indent == 2:
                    if line.strip() not in _GROUPS:
                        ctx.failed_line("component_declared", number, line, "grup tidak dikenal")
                    continue
                if indent == 6:
                    if not line.rstrip().endswith(":"):
                        ctx.failed_line(
                            "component_declared", number, line, "baris kunci tidak berakhir ':'"
                        )
                    continue
                if indent == 8:
                    match = _ENTRY.fullmatch(line)
                    if match is None:
                        current = None
                        ctx.failed_line(
                            "component_declared",
                            number,
                            line,
                            "baris komponen tidak sesuai bentuk <hash> <paket>/<kelas> filter",
                        )
                        continue
                    current = match["name"]
                    key = (kind, current, match["permission"])
                    if key not in seen_components:
                        seen_components.add(key)
                        ctx.add(
                            "component_declared",
                            line,
                            {
                                "kind": kind,
                                "name": current,
                                "permission": match["permission"],
                                "line_no": number,
                            },
                        )
                    continue
                if indent == 10 and current is not None:
                    stripped = line.strip()
                    action = _ACTION.fullmatch(line)
                    if action is not None:
                        pair = (current, action["action"])
                        if pair not in seen_actions:
                            seen_actions.add(pair)
                            ctx.add(
                                "intent_filter_action",
                                line,
                                {
                                    "component": current,
                                    "action": action["action"],
                                    "line_no": number,
                                },
                            )
                    elif not stripped.startswith(_FILTER_DETAIL_PREFIXES):
                        ctx.failed_line(
                            "intent_filter_action", number, line, "baris filter tidak dikenal"
                        )
                    continue
                ctx.failed_line(
                    "component_declared",
                    number,
                    line,
                    "baris di luar bentuk entri komponen yang dikenal",
                )
