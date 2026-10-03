"""Static extractor: URL scan, tool discovery, bundle layout (the SDK tools are faked)."""

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

import pytest

from src.static_analysis import extractor
from src.static_analysis.extractor import (
    BUNDLE_FILES,
    MAX_URL_LINES,
    ExtractorError,
    extract,
    find_build_tools,
    find_java,
)


def _apk(path: Path, entries: dict[str, bytes]) -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return path


def _completed(stdout: bytes = b"", stderr: bytes = b"", code: int = 0):  # noqa: ANN202
    return subprocess.CompletedProcess([], code, stdout, stderr)


# --- URL scan ---------------------------------------------------------------------------------


def test_urls_come_from_dex_and_res_only_unique_and_sorted(tmp_path: Path) -> None:
    apk = _apk(
        tmp_path / "a.apk",
        {
            "classes.dex": b"\x00 http://b.example.test/x?y=1 + https://a.example.test/ \x00",
            "classes2.dex": b"ftp://c.example.test/file and 10.1.2.3 here",
            "res/xml/net.xml": b"wss://d.example.test/socket\x00",
            "assets/skipped.txt": b"http://not-scanned.example.test/",
            "lib/classes.dex": b"http://nested-dex.example.test/",
            "AndroidManifest.xml": b"http://manifest-not-scanned.example.test/",
        },
    )
    assert extractor._urls(apk) == [
        "10.1.2.3",
        "ftp://c.example.test/file",
        "http://b.example.test/x?y=1",
        "https://a.example.test/",
        "wss://d.example.test/socket",
    ]


def test_utf16_text_in_resources_is_read_without_gluing_neighbours(tmp_path: Path) -> None:
    one = "http://one.example.test/a".encode("utf-16le") + b"\x00\x00"
    two = "http://two.example.test/b".encode("utf-16le") + b"\x00\x00"
    apk = _apk(tmp_path / "a.apk", {"res/layout/x.xml": b"\x19\x00" + one + b"\x19\x00" + two})
    assert extractor._urls(apk) == ["http://one.example.test/a", "http://two.example.test/b"]


def test_a_utf16_string_at_an_odd_byte_offset_is_found_too(tmp_path: Path) -> None:
    text = "https://odd.example.test/p".encode("utf-16le") + b"\x00\x00"
    apk = _apk(tmp_path / "a.apk", {"res/raw/x.bin": b"\x07" + text})
    assert "https://odd.example.test/p" in extractor._urls(apk)


@pytest.mark.parametrize(
    "noise",
    [b"http://", b"https:// ", b"version 1.2.3", b"300.1.1.1", b"1.2.3.4.5", b"httpx://a.test"],
)
def test_text_that_only_looks_like_a_url_or_an_address_is_not_extracted(
    tmp_path: Path, noise: bytes
) -> None:
    apk = _apk(tmp_path / "a.apk", {"classes.dex": noise})
    assert extractor._urls(apk) == []


def test_trailing_punctuation_is_not_part_of_the_url(tmp_path: Path) -> None:
    apk = _apk(tmp_path / "a.apk", {"classes.dex": b"(see http://p.example.test/a). Next"})
    assert extractor._urls(apk) == ["http://p.example.test/a"]


def test_the_url_list_is_capped(tmp_path: Path) -> None:
    body = "\n".join(f"http://h{n:05d}.example.test/" for n in range(MAX_URL_LINES + 50))
    apk = _apk(tmp_path / "a.apk", {"classes.dex": body.encode()})
    found = extractor._urls(apk)
    assert len(found) == MAX_URL_LINES and found == sorted(found)


def test_a_file_that_is_not_a_zip_is_an_extractor_error(tmp_path: Path) -> None:
    bad = tmp_path / "bad.apk"
    bad.write_bytes(b"not a zip")
    with pytest.raises(ExtractorError, match="archive"):
        extractor._urls(bad)


# --- tool discovery ---------------------------------------------------------------------------


def test_the_highest_36_build_tools_wins_and_other_majors_are_ignored(tmp_path: Path) -> None:
    for name in ("35.0.1", "36.0.0", "36.1.0", "36.0.2", "37.0.0"):
        (tmp_path / "Sdk" / "build-tools" / name).mkdir(parents=True)
    found = find_build_tools({"ANDROID_SDK_ROOT": str(tmp_path / "Sdk")})
    assert found.name == "36.1.0"


def test_sdk_root_is_searched_in_the_documented_order(tmp_path: Path) -> None:
    for root, name in (("a", "36.0.0"), ("b", "36.0.1"), ("local/Android/Sdk", "36.0.2")):
        (tmp_path / root / "build-tools" / name).mkdir(parents=True)
    env = {
        "ANDROID_SDK_ROOT": str(tmp_path / "a"),
        "ANDROID_HOME": str(tmp_path / "b"),
        "LOCALAPPDATA": str(tmp_path / "local"),
    }
    assert find_build_tools(env).name == "36.0.0"
    del env["ANDROID_SDK_ROOT"]
    assert find_build_tools(env).name == "36.0.1"
    del env["ANDROID_HOME"]
    assert find_build_tools(env).name == "36.0.2"


def test_missing_build_tools_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ExtractorError, match="build-tools"):
        find_build_tools({"ANDROID_SDK_ROOT": str(tmp_path)})


def test_java_is_taken_from_java_home_first(tmp_path: Path) -> None:
    exe = tmp_path / "bin" / ("java.exe" if extractor.os.name == "nt" else "java")
    exe.parent.mkdir()
    exe.write_bytes(b"")
    assert find_java({"JAVA_HOME": str(tmp_path)}) == str(exe)


def test_missing_java_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extractor.shutil, "which", lambda _name: None)
    with pytest.raises(ExtractorError, match="java"):
        find_java({})


# --- extract() with the tools faked -----------------------------------------------------------


@pytest.fixture
def faked_tools(monkeypatch: pytest.MonkeyPatch):  # noqa: ANN201
    calls: list[list[str]] = []
    signer_code = {"value": 0}

    def fake(command: list[str]):  # noqa: ANN202
        calls.append(command)
        name = Path(command[0]).name
        if name.startswith("aapt2"):
            if command[1] == "version":
                return _completed(b"Android Asset Packaging Tool (aapt) 2.20\n")
            return _completed(f"aapt2 {' '.join(command[1:3])}\n".encode())
        if "verify" in command:
            return _completed(
                b"Signer #1 certificate SHA-256 digest: " + b"ab" * 32 + b"\n",
                b"WARNING: noise\nDOES NOT VERIFY\nERROR: broken\n",
                signer_code["value"],
            )
        if "--version" in command:
            return _completed(b"0.9\n")
        return _completed(b"", b'openjdk version "25"\n')

    monkeypatch.setattr(extractor, "_run", fake)
    fake.calls = calls  # type: ignore[attr-defined]
    fake.signer_code = signer_code  # type: ignore[attr-defined]
    return fake


def _tools(tmp_path: Path) -> Path:
    tools = tmp_path / "bt" / "36.0.0"
    (tools / "lib").mkdir(parents=True)
    return tools


def test_the_bundle_has_the_seven_files_in_order_and_a_consistent_manifest(
    tmp_path: Path, faked_tools
) -> None:
    apk = _apk(tmp_path / "a.apk", {"classes.dex": b"http://x.example.test/"})
    written = extract(apk, tmp_path / "out", build_tools=_tools(tmp_path), java="java")
    assert [p.name for p in written] == list(BUNDLE_FILES)
    digest = hashlib.sha256(apk.read_bytes()).hexdigest()
    assert (tmp_path / "out" / "apk.sha256").read_text() == digest + "\n"
    assert (tmp_path / "out" / "badging.txt").read_bytes() == b"aapt2 dump badging\n"
    assert (tmp_path / "out" / "strings_urls.txt").read_text() == "http://x.example.test/\n"
    manifest = json.loads((tmp_path / "out" / "bundle.json").read_text())
    assert manifest["apk_sha256"] == digest and manifest["extractor_version"] == "1"
    assert set(manifest) == {
        "apk_sha256",
        "extractor_version",
        "tool_versions",
        "created_at",
        "files",
    }
    assert set(manifest["files"]) == set(BUNDLE_FILES) - {"bundle.json"}
    for name, expected in manifest["files"].items():
        assert hashlib.sha256((tmp_path / "out" / name).read_bytes()).hexdigest() == expected
    assert manifest["tool_versions"]["aapt2"].startswith("Android Asset Packaging Tool")
    assert manifest["tool_versions"]["java"] == 'openjdk version "25"'


def test_tools_run_without_a_shell_and_the_apk_is_only_ever_an_argument(
    tmp_path: Path, faked_tools, monkeypatch: pytest.MonkeyPatch
) -> None:
    apk = _apk(tmp_path / "evil; rm -rf x.apk", {"classes.dex": b""})
    extract(apk, tmp_path / "out", build_tools=_tools(tmp_path), java="java")
    assert all(isinstance(arg, str) for call in faked_tools.calls for arg in call)
    assert any(str(apk) in call for call in faked_tools.calls)
    source = Path(extractor.__file__).read_text(encoding="utf-8")
    assert "shell=False" in source and "shell=True" not in source


def test_a_failed_verification_is_recorded_not_raised(tmp_path: Path, faked_tools) -> None:
    faked_tools.signer_code["value"] = 1
    apk = _apk(tmp_path / "a.apk", {"classes.dex": b""})
    extract(apk, tmp_path / "out", build_tools=_tools(tmp_path), java="java")
    certs = (tmp_path / "out" / "certs.txt").read_text()
    assert "Signer #1 certificate SHA-256 digest:" in certs
    assert "# apksigner exit code: 1" in certs
    assert "DOES NOT VERIFY" in certs and "ERROR: broken" in certs
    assert "WARNING: noise" not in certs


def test_an_empty_url_list_is_an_empty_file(tmp_path: Path, faked_tools) -> None:
    apk = _apk(tmp_path / "a.apk", {"classes.dex": b"nothing here"})
    extract(apk, tmp_path / "out", build_tools=_tools(tmp_path), java="java")
    assert (tmp_path / "out" / "strings_urls.txt").read_bytes() == b""


def test_extract_never_overwrites_an_existing_bundle_file(tmp_path: Path, faked_tools) -> None:
    apk = _apk(tmp_path / "a.apk", {"classes.dex": b""})
    out = tmp_path / "out"
    out.mkdir()
    (out / "manifest.txt").write_bytes(b"old")
    with pytest.raises(ExtractorError, match="already exists"):
        extract(apk, out, build_tools=_tools(tmp_path), java="java")
    assert (out / "manifest.txt").read_bytes() == b"old"


def test_a_failing_aapt2_is_an_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extractor, "_run", lambda _cmd: _completed(b"", b"bad", 1))
    apk = _apk(tmp_path / "a.apk", {"classes.dex": b""})
    with pytest.raises(ExtractorError, match="aapt2 badging failed"):
        extract(apk, tmp_path / "out", build_tools=_tools(tmp_path), java="java")


def test_a_missing_apk_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ExtractorError, match="not found"):
        extract(tmp_path / "none.apk", tmp_path / "out", build_tools=_tools(tmp_path), java="java")
