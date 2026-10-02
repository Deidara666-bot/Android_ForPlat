from app.parsing.base import Parser


class UnknownOperationError(LookupError):
    pass


_REGISTRY: dict[str, Parser] = {}


def register(parser: Parser) -> None:
    if parser.operation_id in _REGISTRY:
        raise ValueError(f"parser already registered for {parser.operation_id}")
    _REGISTRY[parser.operation_id] = parser


def get_parser(operation_id: str) -> Parser:
    try:
        return _REGISTRY[operation_id]
    except KeyError:
        raise UnknownOperationError(operation_id) from None


def registered_operations() -> frozenset[str]:
    return frozenset(_REGISTRY)
