"""One operation, several evidence parts: the registry also keys on `raw_source`."""

import pytest

from app.parsing import registry
from app.parsing.base import ParsedArtifact
from app.parsing.registry import UnknownOperationError, get_parser, register, registered_operations


class _Parser:
    parser_name = "fake"
    parser_version = "1"

    def __init__(self, operation_id: str, raw_source: str | None = None) -> None:
        self.operation_id = operation_id
        if raw_source is not None:
            self.raw_source = raw_source

    def parse(self, raw: bytes) -> list[ParsedArtifact]:
        return []


@pytest.fixture(autouse=True)
def _isolated_registry():
    saved = dict(registry._REGISTRY)
    registry._REGISTRY.clear()
    yield
    registry._REGISTRY.clear()
    registry._REGISTRY.update(saved)


def test_each_raw_source_gets_its_own_parser_and_the_operation_is_listed_once() -> None:
    first, second = _Parser("op", "part one"), _Parser("op", "part two")
    register(first)
    register(second)
    assert get_parser("op", "part one") is first
    assert get_parser("op", "part two") is second
    assert registered_operations() == frozenset({"op"})


def test_an_unlabelled_parser_serves_every_raw_source_of_its_operation() -> None:
    generic = _Parser("op")
    register(generic)
    assert get_parser("op") is generic
    assert get_parser("op", "anything") is generic


def test_a_labelled_parser_wins_over_the_unlabelled_one() -> None:
    generic, specific = _Parser("op"), _Parser("op", "part one")
    register(generic)
    register(specific)
    assert get_parser("op", "part one") is specific
    assert get_parser("op", "part two") is generic


def test_an_unknown_raw_source_without_a_fallback_is_unknown_not_guessed() -> None:
    register(_Parser("op", "part one"))
    with pytest.raises(UnknownOperationError):
        get_parser("op", "part two")
    with pytest.raises(UnknownOperationError):
        get_parser("op")


def test_the_same_operation_and_raw_source_cannot_be_registered_twice() -> None:
    register(_Parser("op", "part one"))
    with pytest.raises(ValueError):
        register(_Parser("op", "part one"))
