"""Static extractor for the APK files of one package (REF §STATIC). Reads them; never installs
or runs anything.

`extract(apks, out_dir)` takes `(name, path)` pairs, the base APK first, writes the nine bundle
files and returns their paths in bundle order. Identity, badging, permissions, manifest and
certificates come from the base APK; strings, native libraries and code-loading references are
read from every entry of every APK, block by block (never a whole entry in memory).
It uses only the standard library and the Android SDK tools `aapt2` and `apksigner` (the latter
through `java -jar`), always as argument lists, never through a shell. Raw tool output is kept
byte-exact in the bundle files; the backend parses them.
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import zipfile
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import IO

from src.exceptions import AgentError

EXTRACTOR_VERSION = "2"
BUILD_TOOLS_MAJOR = "36"
BUNDLE_FILES: tuple[str, ...] = (
    "apk.sha256",
    "badging.txt",
    "permissions.txt",
    "manifest.txt",
    "certs.txt",
    "strings_urls.txt",
    "native_libs.txt",
    "api_refs.txt",
    "bundle.json",
)
MAX_URL_LINES = 5000
_TOOL_TIMEOUT_SECONDS = 1800  # aapt2 / apksigner on a large APK (REF §STATIC)
ENTRY_SCAN_LIMIT = 256 * 1024 * 1024  # first bytes of one entry that are scanned for strings
_BLOCK_SIZE = 1024 * 1024
_OVERLAP = 4096  # tail carried between blocks so a string cut by a block edge is still found
_TRIM_AT = 4 * MAX_URL_LINES  # the unique set is cut back to the smallest 5000 past this size
_NATIVE_LIB = re.compile(r"lib/[^/]+/[^/]+\.so")
_CODE_LOADING_DESCRIPTORS: tuple[bytes, ...] = (
    b"Ldalvik/system/DexClassLoader;",
    b"Ldalvik/system/InMemoryDexClassLoader;",
    b"Ldalvik/system/PathClassLoader;",
    b"Ldalvik/system/DelegateLastClassLoader;",
)

_URL = re.compile(r"(?:https?|wss?|ftp)://[A-Za-z0-9\[][A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]*")
_IPV4 = re.compile(
    r"(?<![\d.])(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
    r"(?![\d.])"
)
_URL_TRAILING = ".,;:)'\"]"


class ExtractorError(AgentError):
    """The APK cannot be extracted (tool missing, tool failed, unreadable archive)."""


def find_build_tools(environ: dict[str, str] | None = None) -> Path:
    """Highest `36.x` build-tools folder under ANDROID_SDK_ROOT, ANDROID_HOME or the default
    per-user SDK location (`%LOCALAPPDATA%/Android/Sdk`)."""
    env = os.environ if environ is None else environ
    roots: list[Path] = []
    for name in ("ANDROID_SDK_ROOT", "ANDROID_HOME"):
        if env.get(name):
            roots.append(Path(env[name]))
    if env.get("LOCALAPPDATA"):
        roots.append(Path(env["LOCALAPPDATA"]) / "Android" / "Sdk")
    for root in roots:
        folder = root / "build-tools"
        if not folder.is_dir():
            continue
        candidates = sorted(
            (p for p in folder.iterdir() if p.is_dir() and p.name.startswith(BUILD_TOOLS_MAJOR)),
            key=lambda p: tuple(int(x) if x.isdigit() else 0 for x in re.split(r"[.\-]", p.name)),
            reverse=True,
        )
        if candidates:
            return candidates[0]
    raise ExtractorError(f"Android build-tools {BUILD_TOOLS_MAJOR}.x not found in the SDK")


def find_java(environ: dict[str, str] | None = None) -> str:
    """`java` from JAVA_HOME, the JDK bundled with Android Studio, or PATH."""
    env = os.environ if environ is None else environ
    executable = "java.exe" if os.name == "nt" else "java"
    candidates: list[Path] = []
    if env.get("JAVA_HOME"):
        candidates.append(Path(env["JAVA_HOME"]) / "bin" / executable)
    for base in (env.get("ProgramFiles"), env.get("ProgramW6432")):
        if base:
            candidates.append(
                Path(base) / "Android" / "Android Studio" / "jbr" / "bin" / executable
            )
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    found = shutil.which("java")
    if found:
        return found
    raise ExtractorError("java not found (set JAVA_HOME); apksigner needs it")


def _run(command: list[str]) -> subprocess.CompletedProcess[bytes]:
    try:
        return subprocess.run(  # noqa: S603
            command,
            shell=False,
            capture_output=True,
            timeout=_TOOL_TIMEOUT_SECONDS,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ExtractorError(f"cannot run {Path(command[0]).name}: {type(exc).__name__}") from exc


def _both(result: subprocess.CompletedProcess[bytes]) -> tuple[bytes, bytes]:
    return result.stdout, result.stderr


def _first_line(*streams: bytes) -> str:
    """First non-empty line of the first stream that has one (tools differ in stdout/stderr)."""
    for data in streams:
        lines = data.decode("utf-8", errors="replace").strip().splitlines()
        if lines:
            return lines[0].strip()
    return ""


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(_BLOCK_SIZE):
            digest.update(block)
    return digest.hexdigest()


class _UrlCollector:
    """The 5000 smallest unique URL/IPv4 strings seen so far, in bounded memory."""

    def __init__(self) -> None:
        self._found: set[str] = set()
        self._ceiling: str | None = None  # a string above this can no longer be in the top 5000

    def add(self, value: str) -> None:
        if self._ceiling is not None and value > self._ceiling:
            return
        self._found.add(value)
        if len(self._found) > _TRIM_AT:
            kept = sorted(self._found)[:MAX_URL_LINES]
            self._found = set(kept)
            self._ceiling = kept[-1]

    def lines(self) -> list[str]:
        return sorted(self._found)[:MAX_URL_LINES]


def _scan_text(text: str, found: _UrlCollector, limit: int | None) -> None:
    """Add the matches that end at or before `limit` (None = all). A match closer to the end of
    the buffer is met again, whole, in the next block thanks to the carried tail."""
    for match in _URL.finditer(text):
        if limit is not None and match.end() > limit:
            continue
        url = match.group(0).rstrip(_URL_TRAILING)
        if len(url.split("://", 1)[1]) > 0:
            found.add(url)
    for match in _IPV4.finditer(text):
        if limit is None or match.end() <= limit:
            found.add(match.group(0))


def _scan(data: bytes, found: _UrlCollector, *, utf16: bool, final: bool) -> None:
    """Add the URL and IPv4 strings in `data`. Dex strings are single-byte text; binary XML
    resources may keep text as UTF-16, so those are also read as UTF-16LE at both byte
    alignments (a string ends at its NUL, so nothing is glued together). Unless `final`,
    matches in the last `_OVERLAP` bytes are left for the next block."""
    _scan_text(data.decode("latin-1"), found, None if final else len(data) - _OVERLAP)
    if utf16:
        for offset in (0, 1):
            chunk = data[offset:]
            chunk = chunk[: len(chunk) - (len(chunk) % 2)]
            limit = None if final else len(chunk) // 2 - _OVERLAP // 2
            _scan_text(chunk.decode("utf-16le", errors="ignore"), found, limit)


def _scan_entry(
    handle: IO[bytes],
    found: _UrlCollector,
    *,
    utf16: bool,
    descriptors: set[bytes] | None,
    hasher: "hashlib._Hash | None",
) -> int:
    """Stream one archive entry: strings from its first `ENTRY_SCAN_LIMIT` bytes, optionally the
    code-loading descriptors it contains and a SHA-256 of the whole entry. Returns the number of
    bytes scanned for strings."""
    carry = b""
    scanned = 0
    while block := handle.read(_BLOCK_SIZE):
        if hasher is not None:
            hasher.update(block)
        if scanned >= ENTRY_SCAN_LIMIT:
            continue  # past the scan limit only the hash (if any) still needs the bytes
        block = block[: ENTRY_SCAN_LIMIT - scanned]
        scanned += len(block)
        data = carry + block
        if descriptors is not None:
            descriptors.update(d for d in _CODE_LOADING_DESCRIPTORS if d in data)
        _scan(data, found, utf16=utf16, final=False)
        carry = data[-_OVERLAP:]
    if carry:
        _scan(carry, found, utf16=utf16, final=True)
    return scanned


def _is_dex(entry: str) -> bool:
    return "/" not in entry and entry.startswith("classes") and entry.endswith(".dex")


def _scan_archives(
    apks: Sequence[tuple[str, Path]],
) -> tuple[list[str], list[str], list[str], list[dict[str, object]]]:
    """(URL lines, native library lines, code-loading reference lines, truncated entries) over
    every entry of every APK."""
    found = _UrlCollector()
    natives: list[str] = []
    references: list[str] = []
    truncated: list[dict[str, object]] = []
    for name, path in apks:
        try:
            with zipfile.ZipFile(path) as archive:
                for info in sorted(archive.infolist(), key=lambda item: item.filename):
                    entry = info.filename
                    if info.is_dir():
                        continue
                    dex = _is_dex(entry)
                    native = _NATIVE_LIB.fullmatch(entry) is not None
                    descriptors: set[bytes] | None = set() if dex else None
                    hasher = hashlib.sha256() if native else None
                    with archive.open(info) as handle:
                        scanned = _scan_entry(
                            handle, found, utf16=not dex, descriptors=descriptors, hasher=hasher
                        )
                    if info.file_size > scanned:
                        truncated.append(
                            {
                                "apk": name,
                                "entry": entry,
                                "size": info.file_size,
                                "scanned": scanned,
                            }
                        )
                    if hasher is not None:
                        natives.append(f"{name}\t{entry}\t{info.file_size}\t{hasher.hexdigest()}")
                    for descriptor in sorted(descriptors or ()):
                        references.append(f"{name}\t{entry}\t{descriptor.decode('ascii')}")
        except (zipfile.BadZipFile, OSError) as exc:
            raise ExtractorError(f"cannot read the APK archive: {type(exc).__name__}") from exc
    return found.lines(), natives, references, truncated


def _lines_file(lines: list[str]) -> bytes:
    return ("\n".join(lines) + "\n").encode("utf-8") if lines else b""


def extract(
    apks: Sequence[tuple[str, Path]],
    out_dir: Path,
    *,
    build_tools: Path | None = None,
    java: str | None = None,
) -> list[Path]:
    """Write the bundle of the APK set into `out_dir` and return the file paths in bundle order.

    `apks` = `(file name, path)` pairs, base APK first (its name is what `apk.sha256` and the
    native-library / reference lines show). `out_dir` must not already contain a bundle file:
    nothing is overwritten.
    """
    if not apks:
        raise ExtractorError("no APK given")
    names = [name for name, _ in apks]
    if len(set(names)) != len(names):
        raise ExtractorError("APK file names are not unique")
    if any(not path.is_file() for _, path in apks):
        raise ExtractorError("APK file not found")
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {name: out_dir / name for name in BUNDLE_FILES}
    for path in paths.values():
        if path.exists():
            raise ExtractorError(f"{path.name} already exists in the output folder")

    tools = build_tools or find_build_tools()
    java_path = java or find_java()
    aapt2 = str(tools / ("aapt2.exe" if os.name == "nt" else "aapt2"))
    signer = ["-jar", str(tools / "lib" / "apksigner.jar")]
    base_arg = str(apks[0][1])

    def write(name: str, data: bytes) -> None:
        with paths[name].open("xb") as handle:
            handle.write(data)

    digests = {name: _sha256_file(path) for name, path in apks}
    write("apk.sha256", "".join(f"{digests[name]}  {name}\n" for name in names).encode("utf-8"))
    for name, args in (
        ("badging.txt", ["dump", "badging", base_arg]),
        ("permissions.txt", ["dump", "permissions", base_arg]),
        ("manifest.txt", ["dump", "xmltree", "--file", "AndroidManifest.xml", base_arg]),
    ):
        result = _run([aapt2, *args])
        if result.returncode != 0:
            raise ExtractorError(f"aapt2 {args[1]} failed with exit code {result.returncode}")
        write(name, result.stdout)

    # A failed verification is a finding, not an error: its text is kept in certs.txt.
    signed = _run([java_path, *signer, "verify", "--print-certs", base_arg])
    certs = signed.stdout
    if signed.returncode != 0:
        errors = [
            line
            for line in signed.stderr.decode("utf-8", errors="replace").splitlines()
            if line.strip() and not line.startswith("WARNING:")
        ]
        certs += f"\n# apksigner exit code: {signed.returncode}\n".encode()
        certs += ("\n".join(errors) + "\n").encode("utf-8") if errors else b""
    write("certs.txt", certs)

    urls, natives, references, truncated = _scan_archives(apks)
    write("strings_urls.txt", _lines_file(urls))
    write("native_libs.txt", _lines_file(natives))
    write("api_refs.txt", _lines_file(references))

    versions = {
        "aapt2": _first_line(*_both(_run([aapt2, "version"]))),
        "apksigner": _first_line(*_both(_run([java_path, *signer, "--version"]))),
        "java": _first_line(*_both(_run([java_path, "-version"]))[::-1]),
        "build_tools": tools.name,
    }
    manifest = {
        "apk_sha256": digests[names[0]],
        "apks": digests,
        "extractor_version": EXTRACTOR_VERSION,
        "tool_versions": versions,
        "created_at": datetime.now(UTC).isoformat(),
        "files": {
            name: _sha256_file(paths[name]) for name in BUNDLE_FILES if name != "bundle.json"
        },
        "scan": {"entri_terpotong": truncated},
    }
    write("bundle.json", (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return [paths[name] for name in BUNDLE_FILES]
