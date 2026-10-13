"""`sources.yaml` validation at load time (v0.50.1)."""

import copy
from typing import Any

import pytest
import yaml

from app.core.constants import ReferenceRole
from app.research.knowledge_base.loader import SOURCES_PATH, KnowledgeBaseLoader
from app.research.knowledge_base.validator import KnowledgeBaseError, validate_sources

# the 11 ids of 01_BREAKDOWN section 12.1
_REGISTRY_IDS = [
    "KB-AND-PACKAGE",
    "KB-AND-PERMISSION",
    "KB-AND-ACCESSIBILITY",
    "KB-AND-OVERLAY",
    "KB-AND-NOTIFICATION",
    "KB-AND-BROADCAST",
    "KB-AND-USAGE",
    "KB-AND-NETWORK",
    "KB-MITRE-T1624",
    "KB-MITRE-T1417-002",
    "KB-MITRE-T1644",
]


def _data() -> dict[str, Any]:
    loaded = yaml.safe_load(SOURCES_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return copy.deepcopy(loaded)


def _fails(data: dict[str, Any], *words: str) -> None:
    with pytest.raises(KnowledgeBaseError) as caught:
        validate_sources(data)
    for word in words:
        assert word in str(caught.value)


def test_the_shipped_file_has_the_eleven_registry_entries_in_order() -> None:
    entries = validate_sources(_data())
    assert [e.id for e in entries] == _REGISTRY_IDS


def test_roles_follow_the_registry_label() -> None:
    roles = {e.id: e.reference_role for e in validate_sources(_data())}
    assert {r for i, r in roles.items() if i.startswith("KB-AND-")} == {
        ReferenceRole.artifact_semantics
    }
    assert {r for i, r in roles.items() if i.startswith("KB-MITRE-")} == {
        ReferenceRole.technique_mapping
    }


def test_open_data_stays_null_and_nothing_is_invented() -> None:
    entries = validate_sources(_data())
    assert all(e.version_scope is None and e.quality_note is None for e in entries)
    assert all(e.verification_status == "verified_design" for e in entries)
    assert {e.accessed_at.isoformat() for e in entries} == {"2026-09-05"}


def test_loader_reads_the_same_entries_from_the_file() -> None:
    assert KnowledgeBaseLoader().read() == validate_sources(_data())


def test_duplicate_id_is_rejected() -> None:
    data = _data()
    data["sources"][1]["id"] = data["sources"][0]["id"]
    _fails(data, "id", "KB-AND-PACKAGE")


def test_unknown_reference_role_is_rejected_and_named() -> None:
    data = _data()
    data["sources"][0]["reference_role"] = "evidence_score"
    _fails(data, "reference_role")


def test_unknown_verification_status_is_rejected() -> None:
    data = _data()
    data["sources"][0]["verification_status"] = "trusted"
    _fails(data, "verification_status")


@pytest.mark.parametrize("bad_id", ["AND-PACKAGE", "kb-and-package", "KB-", ""])
def test_id_without_the_kb_prefix_is_rejected(bad_id: str) -> None:
    data = _data()
    data["sources"][0]["id"] = bad_id
    _fails(data, "id")


@pytest.mark.parametrize("bad_url", ["http://developer.android.com/x", "ftp://x", "https://", ""])
def test_url_must_be_https(bad_url: str) -> None:
    data = _data()
    data["sources"][0]["url"] = bad_url
    _fails(data, "url")


@pytest.mark.parametrize("key", ["version_scope", "quality_note"])
def test_a_missing_open_data_key_is_rejected_but_null_is_accepted(key: str) -> None:
    data = _data()
    del data["sources"][0][key]
    _fails(data, key)
    data["sources"][0][key] = None
    assert validate_sources(data)[0].id == "KB-AND-PACKAGE"


def test_open_data_may_carry_a_value_once_the_examiner_has_checked_it() -> None:
    data = _data()
    data["sources"][0]["version_scope"] = "API 36"
    assert validate_sources(data)[0].version_scope == "API 36"


@pytest.mark.parametrize("key", ["title", "publisher", "url", "accessed_at", "extracted_claim"])
def test_a_missing_required_key_is_rejected(key: str) -> None:
    data = _data()
    del data["sources"][0][key]
    _fails(data, key)


def test_an_unknown_key_is_rejected() -> None:
    data = _data()
    data["sources"][0]["score"] = 0.9
    _fails(data, "score")


def test_wrong_schema_version_is_rejected() -> None:
    data = _data()
    data["schema_version"] = "3.2"
    _fails(data, "schema_version")


@pytest.mark.parametrize("raw", [None, [], "text", {"sources": []}])
def test_a_malformed_file_is_rejected(raw: object) -> None:
    with pytest.raises(KnowledgeBaseError):
        validate_sources(raw)
