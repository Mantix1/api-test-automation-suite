"""Load JSON Schemas from schemas/ and check responses against them."""
import json
from pathlib import Path

from jsonschema import Draft7Validator

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "schemas"


def load_schema(name: str) -> dict:
    with open(SCHEMA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def assert_matches_schema(instance, name: str) -> None:
    """Fail with every schema violation listed, each with its JSON path."""
    schema = load_schema(name)
    Draft7Validator.check_schema(schema)
    errors = sorted(Draft7Validator(schema).iter_errors(instance), key=lambda e: list(e.path))
    messages = [f"{list(e.path)}: {e.message}" for e in errors]
    assert not messages, f"{name} violations:\n" + "\n".join(messages)
