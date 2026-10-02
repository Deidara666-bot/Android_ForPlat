from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from src.exceptions import UploadError
from src.transport.uploader import EvidenceUploader

_BYTES = b"package:a uid:1\r\npackage:b uid:2\n"


def _upload(uploader: EvidenceUploader, path: Path) -> None:
    uploader.upload(
        path,
        session_id="0f8b3c9e-6a4d-4b53-9c1e-2d7a5e8b1f60",
        operation_id="collect_package_inventory",
        sequence=2,
        part=1,
        sha256_agent="a" * 64,
        size_bytes=len(_BYTES),
        acquired_at=datetime(2026, 10, 2, 10, 0, tzinfo=UTC),
        raw_source="pm list packages -U",
        tool_version="adb 1.0.41",
        android_version="16",
        device_build=None,
        privilege_state="non_root",
    )


@pytest.fixture
def evidence_file(tmp_path: Path) -> Path:
    path = tmp_path / "2-collect_package_inventory-1.bin"
    path.write_bytes(_BYTES)
    return path


def test_upload_sends_bearer_token_fields_and_exact_bytes(evidence_file: Path) -> None:
    seen: dict[str, httpx.Request] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["request"] = request
        return httpx.Response(201, json={})

    uploader = EvidenceUploader("http://backend", "tok", transport=httpx.MockTransport(handler))
    _upload(uploader, evidence_file)

    request = seen["request"]
    assert request.url.path == "/api/evidence/upload"
    assert request.headers["authorization"] == "Bearer tok"
    body = request.read()
    assert _BYTES in body  # file bytes travel unchanged, CRLF included
    for expected in (b'name="sequence"', b"collect_package_inventory", b'name="raw_source"'):
        assert expected in body
    assert b'name="device_build"' not in body  # None fields are omitted
    assert b"2026-10-02T10:00:00+00:00" in body


@pytest.mark.parametrize("status", [401, 404, 409, 413, 422, 500])
def test_any_answer_other_than_201_raises(evidence_file: Path, status: int) -> None:
    transport = httpx.MockTransport(lambda _request: httpx.Response(status))
    with pytest.raises(UploadError, match=str(status)):
        _upload(EvidenceUploader("http://backend", "tok", transport=transport), evidence_file)


def test_network_failure_raises_upload_error(evidence_file: Path) -> None:
    def boom(_request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("down")

    with pytest.raises(UploadError, match="ConnectError"):
        _upload(
            EvidenceUploader("http://backend", "tok", transport=httpx.MockTransport(boom)),
            evidence_file,
        )


def test_missing_file_raises_upload_error(tmp_path: Path) -> None:
    transport = httpx.MockTransport(lambda _request: httpx.Response(201))
    with pytest.raises(UploadError):
        _upload(
            EvidenceUploader("http://backend", "tok", transport=transport), tmp_path / "gone.bin"
        )
