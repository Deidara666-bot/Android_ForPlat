import json
from datetime import UTC, datetime
from pathlib import Path

AUDIT_LOG = Path(__file__).resolve().parents[2] / "var" / "audit.log"


def audit(
    event: str, reason: str | None = None, *, log_file: Path | None = None, **fields: object
) -> None:
    """Append one JSON line (UTC time, event, reason, extra fields). Never pass secrets."""
    target = log_file or AUDIT_LOG
    target.parent.mkdir(parents=True, exist_ok=True)
    record = {"time": datetime.now(UTC).isoformat(), "event": event, "reason": reason, **fields}
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
