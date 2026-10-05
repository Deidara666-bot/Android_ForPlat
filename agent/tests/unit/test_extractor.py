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


# --- string, native library and code-loading scan ---------------------------------------------


def _urls(apk: Path) -> list[str]:
    return extractor._scan_archives([(apk.name, apk)])[0]


def test_urls_come_from_every_entry_unique_and_sorted(tmp_path: Path) -> None:
    apk = _apk(
        tmp_path / "a.apk",
        {
            "classes.dex": b"\x00 http://b.example.test/x?y=1 + https://a.example.test/ \x00",
            "classes2.dex": b"ftp://c.example.test/file and 10.1.2.3 here",
            "res/xml/net.xml": b"wss://d.example.test/socket\x00",
            "assets/data.txt": b"http://asset.example.test/",
            "lib/x86_64/liba.so": b"\x7fELF http://native.example.test/",
            "AndroidManifest.xml": b"http://manifest.example.test/",
        },
    )
    assert _urls(apk) == [
        "10.1.2.3",
        "ftp://c.example.test/file",
        "http://asset.example.test/",
        "http://b.example.test/x?y=1",
        "http://manifest.example.test/",
        "http://native.example.test/",
        "https://a.example.test/",
        "wss://d.example.test/socket",
    ]


def test_every_apk_of_the_set_is_scanned(tmp_path: Path) -> None:
    base = _apk(tmp_path / "base.apk", {"classes.dex": b"http://one.example.test/"})
    split = _apk(tmp_path / "split.apk", {"assets/x": b"http://two.example.test/"})
    urls, *_ = extractor._scan_archives([("base.apk", base), ("split.apk", split)])
    assert urls == ["http://one.example.test/", "http://two.example.test/"]


def test_utf16_text_in_resources_is_read_without_gluing_neighbours(tmp_path: Path) -> None:
    one = "http://one.example.test/a".encode("utf-16le") + b"\x00\x00"
    two = "http://two.example.test/b".encode("utf-16le") + b"\x00\x00"
    apk = _apk(tmp_path / "a.apk", {"res/layout/x.xml": b"\x19\x00" + one + b"\x19\x00" + two})
    assert _urls(apk) == ["http://one.example.test/a", "http://two.example.test/b"]


def test_a_utf16_string_at_an_odd_byte_offset_is_found_too(tmp_path: Path) -> None:
    text = "https://odd.example.test/p".encode("utf-16le") + b"\x00\x00"
    apk = _apk(tmp_path / "a.apk", {"res/raw/x.bin": b"\x07" + text})
    assert "https://odd.example.test/p" in _urls(apk)


@pytest.mark.parametrize(
    "noise",
    [b"http://", b"https:// ", b"version 1.2.3", b"300.1.1.1", b"1.2.3.4.5", b"httpx://a.test"],
)
def test_text_that_only_looks_like_a_url_or_an_address_is_not_extracted(
    tmp_path: Path, noise: bytes
) -> None:
    apk = _apk(tmp_path / "a.apk", {"classes.dex": noise})
    assert _urls(apk) == []


def test_trailing_punctuation_is_not_part_of_the_url(tmp_path: Path) -> None:
    apk = _apk(tmp_path / "a.apk", {"classes.dex": b"(see http://p.example.test/a). Next"})
    assert _urls(apk) == ["http://p.example.test/a"]


def test_the_url_list_is_capped_to_the_smallest_strings(tmp_path: Path) -> None:
    body = "\n".join(f"http://h{n:05d}.example.test/" for n in range(MAX_URL_LINES + 50))
    apk = _apk(tmp_path / "a.apk", {"classes.dex": body.encode()})
    found = _urls(apk)
    assert len(found) == MAX_URL_LINES and found == sorted(found)
    assert found[0] == "http://h00000.example.test/"


def test_the_capped_set_stays_exact_even_when_it_is_trimmed_while_scanning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(extractor, "_TRIM_AT", 30)
    monkeypatch.setattr(extractor, "MAX_URL_LINES", 10)
    names = [f"http://h{n:03d}.test/" for n in (50, 3, 99, 7, 1, 60, 2, 80, 4, 5, 6, 8, 9, 0)]
    names += [f"http://h{n:03d}.test/" for n in range(100, 140)]  # forces a trim
    apk = _apk(tmp_path / "a.apk", {"classes.dex": "\n".join(names).encode()})
    assert _urls(apk) == sorted(set(names))[:10]


def test_a_string_cut_by_a_block_edge_is_found_whole(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(extractor, "_BLOCK_SIZE", 64)
    monkeypatch.setattr(extractor, "_OVERLAP", 32)
    data = b" " * 58 + b"http://edge.example.test/path" + b" " * 100 + b"http://next.test/a "
    apk = _apk(tmp_path / "a.apk", {"classes.dex": data})
    assert _urls(apk) == ["http://edge.example.test/path", "http://next.test/a"]


def test_an_entry_past_the_scan_limit_is_cut_and_recorded(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(extractor, "ENTRY_SCAN_LIMIT", 100)
    data = b"http://early.example.test/ " + b" " * 200 + b"http://late.example.test/"
    apk = _apk(tmp_path / "a.apk", {"assets/big.bin": data, "assets/small.txt": b"x"})
    urls, _natives, _refs, truncated = extractor._scan_archives([("a.apk", apk)])
    assert urls == ["http://early.example.test/"]
    assert truncated == [
        {"apk": "a.apk", "entry": "assets/big.bin", "size": len(data), "scanned": 100}
    ]


def test_native_libraries_are_listed_with_size_and_sha256_of_the_whole_entry(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(extractor, "ENTRY_SCAN_LIMIT", 10)  # the hash still covers every byte
    lib = b"\x7fELF" + bytes(range(200))
    apk = _apk(
        tmp_path / "a.apk",
        {"lib/x86_64/a.so": lib, "lib/x86_64/readme.txt": b"no", "assets/lib/x/b.so": b"no"},
    )
    _urls_, natives, _refs, _truncated = extractor._scan_archives([("base.apk", apk)])
    assert natives == [f"base.apk\tlib/x86_64/a.so\t{len(lib)}\t{hashlib.sha256(lib).hexdigest()}"]


def test_code_loading_descriptors_are_listed_per_dex_entry(tmp_path: Path) -> None:
    apk = _apk(
        tmp_path / "a.apk",
        {
            "classes.dex": b"dex\n035 xx Ldalvik/system/DexClassLoader; yy Lcom/x/Y;",
            "classes2.dex": (
                b"Ldalvik/system/PathClassLoader; Ldalvik/system/InMemoryDexClassLoader;"
            ),
            "classes3.dex": b"Ldalvik/system/DexClassLoaderX; Ldalvik/system/BaseDexClassLoader;",
            "assets/not-dex": b"Ldalvik/system/DexClassLoader;",
        },
    )
    _u, _n, refs, _t = extractor._scan_archives([("base.apk", apk)])
    assert refs == [
        "base.apk\tclasses.dex\tLdalvik/system/DexClassLoader;",
        "base.apk\tclasses2.dex\tLdalvik/system/InMemoryDexClassLoader;",
        "base.apk\tclasses2.dex\tLdalvik/system/PathClassLoader;",
    ]


def test_a_descriptor_cut_by_a_block_edge_is_still_found(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(extractor, "_BLOCK_SIZE", 64)
    monkeypatch.setattr(extractor, "_OVERLAP", 48)
    data = b"." * 50 + b"Ldalvik/system/DelegateLastClassLoader;" + b"." * 80
    apk = _apk(tmp_path / "a.apk", {"classes.dex": data})
    _u, _n, refs, _t = extractor._scan_archives([("a.apk", apk)])
    assert refs == ["a.apk\tclasses.dex\tLdalvik/system/DelegateLastClassLoader;"]


def test_nothing_in_the_archive_is_ever_read_whole(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sizes: list[int] = []
    original = zipfile.ZipExtFile.read

    def spy(self: zipfile.ZipExtFile, n: int | None = -1) -> bytes:
        sizes.append(-1 if n is None else n)
        return original(self, n)

    monkeypatch.setattr(zipfile.ZipExtFile, "read", spy)
    apk = _apk(tmp_path / "a.apk", {"classes.dex": b"x" * 3_000_000})
    _urls(apk)
    assert sizes and all(size > 0 for size in sizes)  # always a bounded block, never read()/-1


def test_a_file_that_is_not_a_zip_is_an_extractor_error(tmp_path: Path) -> None:
    bad = tmp_path / "bad.apk"
    bad.write_bytes(b"not a zip")
    with pytest.raises(ExtractorError, match="archive"):
        extractor._scan_archives([("bad.apk", bad)])


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


def _set(tmp_path: Path, **entries: dict[str, bytes]) -> list[tuple[str, Path]]:
    return [(name, _apk(tmp_path / name, files)) for name, files in entries.items()]


def test_the_bundle_has_the_nine_files_in_order_and_a_consistent_manifest(
    tmp_path: Path, faked_tools
) -> None:
    base = _apk(
        tmp_path / "base.apk",
        {"classes.dex": b"http://x.example.test/ Ldalvik/system/DexClassLoader;"},
    )
    split = _apk(tmp_path / "split_config.arm64_v8a.apk", {"lib/arm64-v8a/a.so": b"ELF"})
    apks = [("base.apk", base), ("split_config.arm64_v8a.apk", split)]
    written = extract(apks, tmp_path / "out", build_tools=_tools(tmp_path), java="java")
    assert [p.name for p in written] == list(BUNDLE_FILES)
    digest = hashlib.sha256(base.read_bytes()).hexdigest()
    split_digest = hashlib.sha256(split.read_bytes()).hexdigest()
    assert (tmp_path / "out" / "apk.sha256").read_text() == (
        f"{digest}  base.apk\n{split_digest}  split_config.arm64_v8a.apk\n"
    )
    assert (tmp_path / "out" / "badging.txt").read_bytes() == b"aapt2 dump badging\n"
    assert (tmp_path / "out" / "strings_urls.txt").read_text() == "http://x.example.test/\n"
    assert (
        (tmp_path / "out" / "native_libs.txt")
        .read_text()
        .startswith("split_config.arm64_v8a.apk\tlib/arm64-v8a/a.so\t3\t")
    )
    assert (tmp_path / "out" / "api_refs.txt").read_text() == (
        "base.apk\tclasses.dex\tLdalvik/system/DexClassLoader;\n"
    )
    manifest = json.loads((tmp_path / "out" / "bundle.json").read_text())
    assert manifest["apk_sha256"] == digest and manifest["extractor_version"] == "2"
    assert manifest["apks"] == {"base.apk": digest, "split_config.arm64_v8a.apk": split_digest}
    assert manifest["scan"] == {"entri_terpotong": []}
    assert set(manifest) == {
        "apk_sha256",
        "apks",
        "extractor_version",
        "tool_versions",
        "created_at",
        "files",
        "scan",
    }
    assert set(manifest["files"]) == set(BUNDLE_FILES) - {"bundle.json"}
    for name, expected in manifest["files"].items():
        assert hashlib.sha256((tmp_path / "out" / name).read_bytes()).hexdigest() == expected
    assert manifest["tool_versions"]["aapt2"].startswith("Android Asset Packaging Tool")
    assert manifest["tool_versions"]["java"] == 'openjdk version "25"'


def test_badging_permissions_manifest_and_certs_come_from_the_base_apk_only(
    tmp_path: Path, faked_tools
) -> None:
    apks = _set(tmp_path, **{"base.apk": {"a": b""}, "split.apk": {"b": b""}})
    extract(apks, tmp_path / "out", build_tools=_tools(tmp_path), java="java")
    tool_calls = [call for call in faked_tools.calls if call[-1].endswith(".apk")]
    assert tool_calls and all(call[-1] == str(apks[0][1]) for call in tool_calls)


def test_tools_run_without_a_shell_and_the_apk_is_only_ever_an_argument(
    tmp_path: Path, faked_tools, monkeypatch: pytest.MonkeyPatch
) -> None:
    apk = _apk(tmp_path / "evil; rm -rf x.apk", {"classes.dex": b""})
    extract([("base.apk", apk)], tmp_path / "out", build_tools=_tools(tmp_path), java="java")
    assert all(isinstance(arg, str) for call in faked_tools.calls for arg in call)
    assert any(str(apk) in call for call in faked_tools.calls)
    source = Path(extractor.__file__).read_text(encoding="utf-8")
    assert "shell=False" in source and "shell=True" not in source


def test_a_failed_verification_is_recorded_not_raised(tmp_path: Path, faked_tools) -> None:
    faked_tools.signer_code["value"] = 1
    apk = _apk(tmp_path / "a.apk", {"classes.dex": b""})
    extract([("a.apk", apk)], tmp_path / "out", build_tools=_tools(tmp_path), java="java")
    certs = (tmp_path / "out" / "certs.txt").read_text()
    assert "Signer #1 certificate SHA-256 digest:" in certs
    assert "# apksigner exit code: 1" in certs
    assert "DOES NOT VERIFY" in certs and "ERROR: broken" in certs
    assert "WARNING: noise" not in certs


def test_empty_scan_results_are_empty_files(tmp_path: Path, faked_tools) -> None:
    apk = _apk(tmp_path / "a.apk", {"classes.dex": b"nothing here"})
    extract([("a.apk", apk)], tmp_path / "out", build_tools=_tools(tmp_path), java="java")
    for name in ("strings_urls.txt", "native_libs.txt", "api_refs.txt"):
        assert (tmp_path / "out" / name).read_bytes() == b""


def test_a_truncated_entry_is_recorded_in_the_bundle_manifest(
    tmp_path: Path, faked_tools, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(extractor, "ENTRY_SCAN_LIMIT", 50)
    apk = _apk(tmp_path / "a.apk", {"assets/big": b"x" * 120})
    extract([("a.apk", apk)], tmp_path / "out", build_tools=_tools(tmp_path), java="java")
    manifest = json.loads((tmp_path / "out" / "bundle.json").read_text())
    assert manifest["scan"]["entri_terpotong"] == [
        {"apk": "a.apk", "entry": "assets/big", "size": 120, "scanned": 50}
    ]


def test_extract_never_overwrites_an_existing_bundle_file(tmp_path: Path, faked_tools) -> None:
    apk = _apk(tmp_path / "a.apk", {"classes.dex": b""})
    out = tmp_path / "out"
    out.mkdir()
    (out / "manifest.txt").write_bytes(b"old")
    with pytest.raises(ExtractorError, match="already exists"):
        extract([("a.apk", apk)], out, build_tools=_tools(tmp_path), java="java")
    assert (out / "manifest.txt").read_bytes() == b"old"


def test_a_failing_aapt2_is_an_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(extractor, "_run", lambda _cmd: _completed(b"", b"bad", 1))
    apk = _apk(tmp_path / "a.apk", {"classes.dex": b""})
    with pytest.raises(ExtractorError, match="aapt2 badging failed"):
        extract([("a.apk", apk)], tmp_path / "out", build_tools=_tools(tmp_path), java="java")


def test_a_missing_apk_is_an_error(tmp_path: Path) -> None:
    with pytest.raises(ExtractorError, match="not found"):
        extract(
            [("none.apk", tmp_path / "none.apk")],
            tmp_path / "out",
            build_tools=_tools(tmp_path),
            java="java",
        )


def test_an_empty_set_and_duplicate_names_are_errors(tmp_path: Path) -> None:
    apk = _apk(tmp_path / "a.apk", {"x": b""})
    tools = _tools(tmp_path)
    with pytest.raises(ExtractorError, match="no APK"):
        extract([], tmp_path / "out", build_tools=tools, java="java")
    with pytest.raises(ExtractorError, match="unique"):
        extract(
            [("a.apk", apk), ("a.apk", apk)],
            tmp_path / "out",
            build_tools=tools,
            java="java",
        )
