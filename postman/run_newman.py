"""Run the Postman collection with Newman without the API key reaching disk or reports.

Run from the project root (needs `npm install` once):
    .venv/bin/python -m postman.run_newman                  # every folder
    .venv/bin/python -m postman.run_newman --folder Smoke   # push/PR subset

The key comes from .env via framework.config. It is written only to a private
temporary environment file that is deleted after the run, and the output and
reports are checked for it afterwards.
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

from framework import config

ROOT = Path(__file__).resolve().parent.parent
POSTMAN_DIR = ROOT / "postman"
COLLECTION = POSTMAN_DIR / "OpenWeatherMap_API_Tests.postman_collection.json"
ENVIRONMENT = POSTMAN_DIR / "OpenWeatherMap.postman_environment.json"
REPORTS_DIR = ROOT / "reports"


def environment_with_key() -> dict:
    environment = json.loads(ENVIRONMENT.read_text(encoding="utf-8"))
    values = {"baseUrl": config.BASE_URL, "geoBaseUrl": config.GEO_BASE_URL, "apiKey": config.API_KEY}
    for entry in environment["values"]:
        entry["value"] = values.get(entry["key"], entry["value"])
    return environment


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Postman collection with Newman.")
    parser.add_argument("--folder", help="run only this folder, e.g. Smoke")
    args = parser.parse_args()

    suffix = f"-{args.folder.lower()}" if args.folder else ""
    html_report = REPORTS_DIR / f"newman{suffix}.html"
    junit_report = REPORTS_DIR / f"newman{suffix}-junit.xml"
    REPORTS_DIR.mkdir(exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        env_file = Path(tmp) / "environment.json"
        env_file.touch(mode=0o600)
        env_file.write_text(json.dumps(environment_with_key()), encoding="utf-8")

        command = [
            "npx", "--no-install", "newman", "run", str(COLLECTION),
            "--environment", str(env_file),
            "--delay-request", "500",
            "--timeout-request", str(config.TIMEOUT_SECONDS * 1000),
            "--reporters", "cli,htmlextra,junit",
            "--reporter-htmlextra-export", str(html_report),
            "--reporter-htmlextra-title", "OpenWeatherMap API Tests",
            "--reporter-htmlextra-skipHeaders", "x-api-key",
            "--reporter-htmlextra-skipEnvironmentVars", "apiKey",
            "--reporter-junit-export", str(junit_report),
        ]
        if args.folder:
            command += ["--folder", args.folder]
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)

    output = result.stdout + result.stderr
    print(output.replace(config.API_KEY, "***"))

    leaked = [p.name for p in (html_report, junit_report) if p.exists() and config.API_KEY in p.read_text(encoding="utf-8")]
    if leaked:
        for name in leaked:
            (REPORTS_DIR / name).unlink()
        print(f"API key found in {', '.join(leaked)}; report deleted.", file=sys.stderr)
        return 1
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
