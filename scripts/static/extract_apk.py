"""Extract the static bundle of one APK: `extract_apk.py <apk> <output folder>`.

Wrapper around `agent/src/static_analysis/extractor.py` for machines that do not run the agent
(for example the isolated VM that analyzes real samples). It only reads the APK.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "agent"))

from src.static_analysis.extractor import ExtractorError, extract  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write the static bundle of an APK.")
    parser.add_argument("apk", type=Path)
    parser.add_argument("out_dir", type=Path)
    args = parser.parse_args(argv)
    try:
        written = extract(args.apk, args.out_dir)
    except ExtractorError as exc:
        sys.stderr.write(f"extract_apk: {exc}\n")
        return 2
    for path in written:
        sys.stdout.write(f"{path}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
