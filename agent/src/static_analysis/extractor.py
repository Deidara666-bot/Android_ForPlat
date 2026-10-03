"""Static extractor for one APK file (REF §STATIC). Reads the APK; never installs or runs it.

`extract(apk, out_dir)` writes the seven bundle files and returns their paths in bundle order.
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
from datetime import UTC, datetime
from pathlib import Path

from src.exceptions import AgentError

EXTRACTOR_VERSION = "1"
BUILD_TOOLS_MAJOR = "36"
BUNDLE_FILES: tuple[str, ...] = (
    "apk.sha256",
    "badging.txt",
    "permissions.txt",
    "manifest.txt",
    "certs.txt",
    "strings_urls.txt",
    "bundle.json",
)
MAX_URL_LINES = 5000
_TOOL_TIMEOUT_SECONDS = 120
_ENTRY_READ_LIMIT = 256 * 1024 * 1024  # largest single dex/res entry that is scanned
_BLOCK_SIZE = 1024 * 1024

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


def _scan_text(text: str, found: set[str]) -> None:
    for match in _URL.finditer(text):
        url = match.group(0).rstrip(_URL_TRAILING)
        if len(url.split("://", 1)[1]) > 0:
            found.add(url)
    for match in _IPV4.finditer(text):
        found.add(match.group(0))


def _scan(data: bytes, found: set[str], *, utf16: bool) -> None:
    """Add the URL and IPv4 strings in `data`. Dex strings are single-byte text; binary XML
    resources may keep text as UTF-16, so those are also read as UTF-16LE at both byte
    alignments (a string ends at its NUL, so nothing is glued together)."""
    _scan_text(data.decode("latin-1"), found)
    if utf16:
        for offset in (0, 1):
            chunk = data[offset:]
            chunk = chunk[: len(chunk) - (len(chunk) % 2)]
            _scan_text(chunk.decode("utf-16le", errors="ignore"), found)


def _urls(apk: Path) -> list[str]:
    """URL and IPv4 strings of `classes*.dex` and `res/`, unique, sorted, at most 5000."""
    found: set[str] = set()
    try:
        with zipfile.ZipFile(apk) as archive:
            for info in archive.infolist():
                name = info.filename
                is_dex = "/" not in name and name.startswith("classes") and name.endswith(".dex")
                if not (is_dex or name.startswith("res/")) or info.is_dir():
                    continue
                if info.file_size > _ENTRY_READ_LIMIT:
                    continue
                with archive.open(info) as handle:
                    _scan(handle.read(), found, utf16=not is_dex)
    except (zipfile.BadZipFile, OSError) as exc:
        raise ExtractorError(f"cannot read the APK archive: {type(exc).__name__}") from exc
    return sorted(found)[:MAX_URL_LINES]


def extract(
    apk: Path,
    out_dir: Path,
    *,
    build_tools: Path | None = None,
    java: str | None = None,
) -> list[Path]:
    """Write the bundle of `apk` into `out_dir` and return the file paths in bundle order.

    `out_dir` must not already contain a bundle file: nothing is overwritten.
    """
    if not apk.is_file():
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
    apk_arg = str(apk)

    def write(name: str, data: bytes) -> None:
        with paths[name].open("xb") as handle:
            handle.write(data)

    digest = _sha256_file(apk)
    write("apk.sha256", (digest + "\n").encode("ascii"))
    for name, args in (
        ("badging.txt", ["dump", "badging", apk_arg]),
        ("permissions.txt", ["dump", "permissions", apk_arg]),
        ("manifest.txt", ["dump", "xmltree", "--file", "AndroidManifest.xml", apk_arg]),
    ):
        result = _run([aapt2, *args])
        if result.returncode != 0:
            raise ExtractorError(f"aapt2 {args[1]} failed with exit code {result.returncode}")
        write(name, result.stdout)

    # A failed verification is a finding, not an error: its text is kept in certs.txt.
    signed = _run([java_path, *signer, "verify", "--print-certs", apk_arg])
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

    lines = _urls(apk)
    write("strings_urls.txt", ("\n".join(lines) + "\n").encode("ascii") if lines else b"")

    versions = {
        "aapt2": _first_line(*_both(_run([aapt2, "version"]))),
        "apksigner": _first_line(*_both(_run([java_path, *signer, "--version"]))),
        "java": _first_line(*_both(_run([java_path, "-version"]))[::-1]),
        "build_tools": tools.name,
    }
    manifest = {
        "apk_sha256": digest,
        "extractor_version": EXTRACTOR_VERSION,
        "tool_versions": versions,
        "created_at": datetime.now(UTC).isoformat(),
        "files": {
            name: _sha256_file(paths[name]) for name in BUNDLE_FILES if name != "bundle.json"
        },
    }
    write("bundle.json", (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return [paths[name] for name in BUNDLE_FILES]
