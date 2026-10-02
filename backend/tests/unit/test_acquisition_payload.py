import uuid
from types import SimpleNamespace

import pytest

from app.core.constants import ALLOWED_OPERATIONS, MAPPED_OPERATIONS
from app.services.acquisition_service import (
    AcquisitionService,
    OperationNotAllowedError,
    OperationNotMappedError,
)

_SESSION = SimpleNamespace(id=uuid.uuid4(), case_id=uuid.uuid4(), device_id=uuid.uuid4())


def test_eight_allowed_and_two_mapped_operations() -> None:
    assert len(ALLOWED_OPERATIONS) == 8
    assert MAPPED_OPERATIONS == {"collect_device_metadata", "collect_package_inventory"}
    assert MAPPED_OPERATIONS <= ALLOWED_OPERATIONS


@pytest.mark.parametrize("operation", sorted(MAPPED_OPERATIONS))
def test_payload_has_exactly_the_six_keys(operation: str) -> None:
    payload = AcquisitionService().build_job(_SESSION, operation, {})
    assert set(payload) == {"type", "session_id", "operation", "case_id", "device_id", "parameters"}
    assert payload["type"] == "job"
    assert payload["operation"] == operation
    assert payload["session_id"] == str(_SESSION.id)


@pytest.mark.parametrize("operation", ["collect_everything", "", "adb shell id", "shell"])
def test_unknown_operation_is_rejected_as_not_allowed(operation: str) -> None:
    with pytest.raises(OperationNotAllowedError):
        AcquisitionService().build_job(_SESSION, operation, {})


@pytest.mark.parametrize("operation", sorted(ALLOWED_OPERATIONS - MAPPED_OPERATIONS))
def test_allowlisted_but_unmapped_operation_is_rejected_as_not_mapped(operation: str) -> None:
    with pytest.raises(OperationNotMappedError):
        AcquisitionService().build_job(_SESSION, operation, {})


def test_the_two_rejections_are_distinct_types() -> None:
    assert not issubclass(OperationNotAllowedError, OperationNotMappedError)
    assert not issubclass(OperationNotMappedError, OperationNotAllowedError)
