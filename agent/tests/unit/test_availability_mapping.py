import pytest

from src.acquisition.availability import REASON_MAX_CHARS, classify_failure, is_acquired
from src.device.adb_controller import AdbResult
from src.models import AvailabilityStatus

_UNSUPPORTED = [
    b"/system/bin/sh: dumpsys2: inaccessible or not found",
    b"sh: foo: not found",
    b"cmd: Unknown command: bar",
    b"Can't find service: nope",
]
_DENIED = [
    b"java.lang.SecurityException: Permission Denial: reading provider",
    b"Permission denial: opening provider",
    b"permission denied",
]


@pytest.mark.parametrize("stderr", _UNSUPPORTED)
def test_unknown_command_or_service_is_unsupported_not_failed(stderr: bytes) -> None:
    status, reason = classify_failure(AdbResult(b"", stderr, 127))
    assert status is AvailabilityStatus.unsupported
    assert reason


@pytest.mark.parametrize("stderr", _DENIED)
def test_permission_errors_are_denied_not_failed(stderr: bytes) -> None:
    status, reason = classify_failure(AdbResult(b"", stderr, 255))
    assert status is AvailabilityStatus.denied
    assert reason


def test_zero_exit_with_empty_output_is_unavailable() -> None:
    status, reason = classify_failure(AdbResult(b"", b"", 0))
    assert status is AvailabilityStatus.unavailable
    assert reason


@pytest.mark.parametrize(
    "stderr",
    [b"error: device offline", b"error: device 'emulator-5554' not found", b"error: closed", b""],
)
def test_everything_else_is_failed_and_adb_transport_errors_are_not_unsupported(
    stderr: bytes,
) -> None:
    status, _ = classify_failure(AdbResult(b"", stderr, 1))
    assert status is AvailabilityStatus.failed


def test_order_is_unsupported_then_denied_then_unavailable() -> None:
    both = b"sh: x: not found; Permission denied"
    assert classify_failure(AdbResult(b"", both, 1))[0] is AvailabilityStatus.unsupported
    assert classify_failure(AdbResult(b"", b"Permission denied", 0))[0] is AvailabilityStatus.denied


def test_reason_is_a_stderr_snippet_of_at_most_200_characters() -> None:
    status, reason = classify_failure(AdbResult(b"", b"error: " + b"x" * 500, 1))
    assert status is AvailabilityStatus.failed
    assert len(reason) == REASON_MAX_CHARS
    assert reason.startswith("error: xxx")


def test_stdout_content_never_leaks_into_the_reason() -> None:
    secret = b"sms body: my pin is 1234"
    _, reason = classify_failure(AdbResult(secret, b"", 1))
    assert "1234" not in reason


def test_successful_result_cannot_be_classified_as_a_failure() -> None:
    result = AdbResult(b"package:a uid:1\n", b"", 0)
    assert is_acquired(result)
    with pytest.raises(ValueError):
        classify_failure(result)


def test_nonzero_exit_with_output_is_not_acquired() -> None:
    assert not is_acquired(AdbResult(b"partial", b"", 1))
