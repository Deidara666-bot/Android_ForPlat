from app.parsing.base import Parser


class UnknownOperationError(LookupError):
    pass


# Key: (operation_id, raw_source). `raw_source` None = the parser serves every part of the
# operation; a string = only the evidence part sent with that source label (an operation whose
# commands have different output formats registers one parser per label).
_REGISTRY: dict[tuple[str, str | None], Parser] = {}


def register(parser: Parser) -> None:
    key = (parser.operation_id, getattr(parser, "raw_source", None))
    if key in _REGISTRY:
        raise ValueError(f"parser already registered for {key[0]} ({key[1]})")
    _REGISTRY[key] = parser


def get_parser(operation_id: str, raw_source: str | None = None) -> Parser:
    """The parser for one evidence file: exact `(operation, raw_source)` first, then the
    operation-wide one. No default parser exists."""
    for key in ((operation_id, raw_source), (operation_id, None)):
        if key in _REGISTRY:
            return _REGISTRY[key]
    raise UnknownOperationError(operation_id)


def registered_operations() -> frozenset[str]:
    return frozenset(operation for operation, _ in _REGISTRY)
