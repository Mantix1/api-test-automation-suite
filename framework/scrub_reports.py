"""Replace the API key with *** in every file under reports/ before they are shared.

The tests send the key as the appid query parameter. Assert messages never
include URLs, but a connection failure raises a requests error (and urllib3
logs a retry warning) whose text contains the full path and query, and
pytest-html and JUnit XML copy that text into the reports.

Run from the project root:
    .venv/bin/python -m framework.scrub_reports
"""
import sys
from pathlib import Path

from framework import config

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"
MASK = "***"


def scrub(directory: Path = REPORTS_DIR) -> list[Path]:
    """Mask the key in place and return the files that contained it."""
    key = config.API_KEY.encode()
    scrubbed = []
    for path in sorted(p for p in directory.rglob("*") if p.is_file()):
        data = path.read_bytes()
        if key in data:
            path.write_bytes(data.replace(key, MASK.encode()))
            scrubbed.append(path)
    return scrubbed


def main() -> int:
    if not REPORTS_DIR.exists():
        print("no reports/ directory; nothing to scrub")
        return 0
    scrubbed = scrub()
    for path in scrubbed:
        print(f"masked API key in {path.relative_to(REPORTS_DIR.parent)}")
    print(f"scrubbed {len(scrubbed)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
