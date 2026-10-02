import pytest

from app.parsing import registry
from app.parsing.base import ParsedArtifact
from app.parsing.registry import (
    UnknownOperationError,
    get_parser,
    register,
    registered_operations,
)


class _FakeParser:
    parser_name = "fake"
    parser_version = "1"

    def __init__(self, operation_id: str) -> None:
        self.operation_id = operation_id

    def parse(self, raw: bytes) -> list[ParsedArtifact]:
        return []


@pytest.fixture(autouse=True)
def _isolated_registry():
    saved = dict(registry._REGISTRY)
    registry._REGISTRY.clear()
    yield
    registry._REGISTRY.clear()
    registry._REGISTRY.update(saved)


def test_register_then_get() -> None:
    parser = _FakeParser("op_a")
    register(parser)
    assert get_parser("op_a") is parser
    assert registered_operations() == frozenset({"op_a"})


def test_unregistered_operation_has_no_default() -> None:
    with pytest.raises(UnknownOperationError):
        get_parser("collect_network_stats")


def test_unknown_operation_is_a_lookup_error() -> None:
    assert issubclass(UnknownOperationError, LookupError)


def test_duplicate_registration_rejected() -> None:
    register(_FakeParser("op_a"))
    with pytest.raises(ValueError):
        register(_FakeParser("op_a"))
