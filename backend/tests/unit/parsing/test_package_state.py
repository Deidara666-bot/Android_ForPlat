from pathlib import Path

import pytest

from app.core.constants import ParseStatus
from app.parsing.package_state.device_metadata import DeviceMetadataParser
from app.parsing.package_state.inventory import InventoryParser

_FIXTURES = Path(__file__).parents[2] / "fixtures" / "parsing"
_BAD_UTF8 = b"package:com.a uid:1\n\xff\xfe\n"


def _fixture(name: str) -> bytes:
    return (_FIXTURES / name).read_bytes()


def test_package_import_fills_registry() -> None:
    # test_registry isolates the registry per test, so check the import-time wiring via a reload.
    import importlib

    from app.parsing import registry

    saved = dict(registry._REGISTRY)
    registry._REGISTRY.clear()
    try:
        import app.parsing

        importlib.reload(app.parsing)
        assert registry.registered_operations() == {
            "collect_package_inventory",
            "collect_device_metadata",
            "collect_package_detail",
        }
        assert isinstance(registry.get_parser("collect_package_inventory"), InventoryParser)
        assert isinstance(registry.get_parser("collect_device_metadata"), DeviceMetadataParser)
    finally:
        registry._REGISTRY.clear()
        registry._REGISTRY.update(saved)


def test_inventory_fixture_parses_all_lines() -> None:
    result = InventoryParser().parse(_fixture("package_inventory_synthetic.txt"))
    assert [(a.parse_status, a.subject_key, a.parsed_value_json["uid"]) for a in result] == [
        (ParseStatus.parsed, "com.synthetic.alpha", 10101),
        (ParseStatus.parsed, "com.synthetic.beta", 10102),
        (ParseStatus.parsed, "android", 1000),
    ]
    first = result[0]
    assert first.raw_value == "package:com.synthetic.alpha uid:10101"
    assert first.parsed_value_json == {
        "package_name": "com.synthetic.alpha",
        "uid": 10101,
        "line_no": 1,
    }
    assert first.parse_note == ""
    assert first.artifact_type == "package_inventory_entry"


def test_inventory_malformed_line_is_kept_with_original_text() -> None:
    result = InventoryParser().parse(_fixture("package_inventory_malformed_synthetic.txt"))
    assert len(result) == 2
    assert result[0].parse_status == ParseStatus.parsed
    bad = result[1]
    assert bad.parse_status == ParseStatus.failed
    assert bad.subject_key is None
    assert bad.raw_value == "paket-rusak-tanpa-uid"
    assert bad.parsed_value_json == {"line_no": 2}
    assert bad.parse_note == "baris tidak sesuai bentuk package:<nama> uid:<angka>"


def test_inventory_blank_lines_skipped_but_counted() -> None:
    result = InventoryParser().parse(b"\npackage:a uid:1\r\n\npackage:b uid:2\n")
    assert [a.parsed_value_json["line_no"] for a in result] == [2, 4]
    assert result[0].raw_value == "package:a uid:1"


@pytest.mark.parametrize("raw", [b"", b"\n\n"])
def test_inventory_without_lines_is_one_empty_artifact(raw: bytes) -> None:
    result = InventoryParser().parse(raw)
    assert len(result) == 1
    assert result[0].parse_status == ParseStatus.empty
    assert result[0].parse_note == "bukti tidak memuat baris package"


@pytest.mark.parametrize("parser", [InventoryParser(), DeviceMetadataParser()])
def test_decode_failure_is_one_failed_artifact_with_offset(
    parser: InventoryParser | DeviceMetadataParser,
) -> None:
    result = parser.parse(_BAD_UTF8)
    assert len(result) == 1
    only = result[0]
    assert only.parse_status == ParseStatus.failed
    assert only.raw_value == ""
    assert "decode" in only.parse_note
    assert str(_BAD_UTF8.index(b"\xff")) in only.parse_note


def test_metadata_fixture_gives_four_artifacts_in_fixed_order() -> None:
    result = DeviceMetadataParser().parse(_fixture("device_metadata_synthetic.txt"))
    assert [a.subject_key for a in result] == [
        "ro.build.version.release",
        "ro.build.version.sdk",
        "ro.build.fingerprint",
        "persist.sys.timezone",
    ]
    assert all(a.parse_status == ParseStatus.parsed for a in result)
    assert result[0].parsed_value_json == {"key": "ro.build.version.release", "value": "16"}
    assert result[0].raw_value == "[ro.build.version.release]: [16]"
    assert result[3].parsed_value_json["value"] == "Etc/UTC"


def test_metadata_missing_key_is_empty_with_note() -> None:
    raw = b"[ro.build.version.release]: [16]\n[ro.build.version.sdk]: [36]\n"
    result = DeviceMetadataParser().parse(raw)
    assert len(result) == 4
    missing = result[3]
    assert missing.parse_status == ParseStatus.empty
    assert missing.raw_value == ""
    assert missing.parse_note == "kunci persist.sys.timezone tidak ada dalam keluaran"


def test_metadata_empty_input_is_four_empty_artifacts() -> None:
    result = DeviceMetadataParser().parse(b"")
    assert len(result) == 4
    assert all(a.parse_status == ParseStatus.empty for a in result)
