from typing import Protocol

INVENTORY_ARTIFACT_TYPE = "package_inventory_entry"


class ArtifactLike(Protocol):
    """What the normalizer reads from a parsed artifact (parser output or stored row)."""

    @property
    def artifact_type(self) -> str: ...
    @property
    def parser_name(self) -> str: ...
    @property
    def parser_version(self) -> str: ...
    @property
    def subject_key(self) -> str | None: ...
    @property
    def parsed_value_json(self) -> dict[str, object]: ...
    @property
    def parse_status(self) -> str: ...


def subject_from_inventory(parsed: ArtifactLike) -> tuple[str, int]:
    """(package, uid) of an inventory entry; anything else is a ValueError, never a guess."""
    if parsed.artifact_type != INVENTORY_ARTIFACT_TYPE:
        raise ValueError(f"artifact_type {parsed.artifact_type!r} is not an inventory entry")
    package = parsed.subject_key
    if not isinstance(package, str) or not package:
        raise ValueError("inventory entry has no subject_key")
    uid = parsed.parsed_value_json.get("uid")
    if isinstance(uid, bool) or not isinstance(uid, int):
        raise ValueError("inventory entry has no integer uid")
    return package, uid
