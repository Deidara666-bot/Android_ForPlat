import uuid
from types import SimpleNamespace

import pytest

from app.core.constants import ALLOWED_OPERATIONS, MAPPED_OPERATIONS
from app.services.acquisition_service import (
    AcquisitionService,
    InvalidParametersError,
    OperationNotAllowedError,
    OperationNotMappedError,
)

_SESSION = SimpleNamespace(id=uuid.uuid4(), case_id=uuid.uuid4(), device_id=uuid.uuid4())
_EIGHT_KEYS = {
    "type",
    "session_id",
    "sequence",
    "operation",
    "case_id",
    "device_id",
    "serial",
    "parameters",
}


_PARAMS = {"collect_package_detail": {"package_name": "com.android.settings"}}


def _row(operation: str, sequence: int = 1) -> SimpleNamespace:
    return SimpleNamespace(operation_id=operation, sequence=sequence)


def test_eight_allowed_and_three_mapped_operations() -> None:
    assert len(ALLOWED_OPERATIONS) == 8
    assert MAPPED_OPERATIONS == {
        "collect_device_metadata",
        "collect_package_inventory",
        "collect_package_detail",
    }
    assert MAPPED_OPERATIONS <= ALLOWED_OPERATIONS


@pytest.mark.parametrize("operation", sorted(MAPPED_OPERATIONS))
def test_payload_has_exactly_the_eight_keys(operation: str) -> None:
    parameters = _PARAMS.get(operation, {})
    payload = AcquisitionService().build_job(
        _SESSION, _row(operation, 2), "emulator-5554", parameters
    )
    assert set(payload) == _EIGHT_KEYS
    assert payload["parameters"] == parameters
    assert payload["type"] == "job"
    assert payload["operation"] == operation
    assert payload["session_id"] == str(_SESSION.id)
    assert payload["sequence"] == 2
    assert payload["serial"] == "emulator-5554"


@pytest.mark.parametrize("operation", ["collect_everything", "", "adb shell id", "shell"])
def test_unknown_operation_is_rejected_as_not_allowed(operation: str) -> None:
    with pytest.raises(OperationNotAllowedError):
        AcquisitionService().build_job(_SESSION, _row(operation), "emulator-5554", {})


@pytest.mark.parametrize("operation", sorted(ALLOWED_OPERATIONS - MAPPED_OPERATIONS))
def test_allowlisted_but_unmapped_operation_is_rejected_as_not_mapped(operation: str) -> None:
    with pytest.raises(OperationNotMappedError):
        AcquisitionService().build_job(_SESSION, _row(operation), "emulator-5554", {})


def test_the_two_rejections_are_distinct_types() -> None:
    assert not issubclass(OperationNotAllowedError, OperationNotMappedError)
    assert not issubclass(OperationNotMappedError, OperationNotAllowedError)


@pytest.mark.parametrize(
    ("operation", "parameters"),
    [
        ("collect_package_detail", {}),
        ("collect_package_detail", {"package_name": "com.x; rm -rf /"}),
        ("collect_package_detail", {"package_name": "-h"}),
        ("collect_package_detail", {"package_name": ""}),
        ("collect_package_detail", {"package_name": "a" * 201}),
        ("collect_package_detail", {"package_name": "com.x", "extra": "y"}),
        ("collect_package_detail", {"path": "/sdcard/evil.apk"}),
        ("collect_device_metadata", {"package_name": "com.android.settings"}),
        ("collect_package_inventory", {"anything": "x"}),
    ],
)
def test_parameters_that_do_not_match_the_operation_are_rejected(
    operation: str, parameters: dict[str, str]
) -> None:
    with pytest.raises(InvalidParametersError):
        AcquisitionService.validate_parameters(operation, parameters)
    with pytest.raises(InvalidParametersError):
        AcquisitionService().build_job(_SESSION, _row(operation), "emulator-5554", parameters)


@pytest.mark.parametrize("name", ["com.android.settings", "a", "com.Example_app.v2", "a" * 200])
def test_valid_package_names_are_accepted(name: str) -> None:
    AcquisitionService.validate_parameters("collect_package_detail", {"package_name": name})
