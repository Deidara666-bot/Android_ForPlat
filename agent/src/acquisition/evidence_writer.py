from pathlib import Path


def write_evidence(path: Path, data: bytes) -> int:
    """Write raw evidence bytes exactly as given; never overwrites an existing file.

    Mode "xb" raises FileExistsError when `path` exists, leaving the old content intact.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as handle:
        handle.write(data)
    return len(data)
