from app.services.integrity_service import IntegrityService

_EMPTY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_sha256_of_empty_bytes_matches_known_digest() -> None:
    assert IntegrityService().sha256_bytes(b"") == _EMPTY_SHA256


def test_sha256_one_byte_difference_changes_digest() -> None:
    service = IntegrityService()
    assert service.sha256_bytes(b"uid:10001") != service.sha256_bytes(b"uid:10002")


def test_matches_is_case_insensitive() -> None:
    service = IntegrityService()
    assert service.matches(_EMPTY_SHA256, _EMPTY_SHA256.upper())


def test_matches_rejects_different_digests() -> None:
    service = IntegrityService()
    assert not service.matches(_EMPTY_SHA256, "0" * 64)


def test_server_digest_equals_block_wise_digest_of_same_bytes() -> None:
    import hashlib

    data = b"package:com.example uid:10001\n"
    # The agent hashes block-wise (sha256_file); the digest must equal the one-shot server digest.
    digest = hashlib.sha256()
    for start in range(0, len(data), 7):
        digest.update(data[start : start + 7])
    assert IntegrityService().sha256_bytes(data) == digest.hexdigest()
