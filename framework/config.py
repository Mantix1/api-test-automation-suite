"""Loads settings from environment variables (and from .env when running locally)."""
import os
from dotenv import load_dotenv

load_dotenv()

PLACEHOLDER_KEY = "your_api_key_her"

def _require(name: str) -> str:
    value = os.getenv(name)
    if not value or value == PLACEHOLDER_KEY:
        raise RuntimeError(
            f"Missing enviroment variables {name}."
            "Copy .env.example to .env and fill it in"
        )
    return value

API_KEY = _require("OWM_API_KEY")
BASE_URL = _require("OWM_BASE_URL")
GEO_BASE_URL = _require("OWM_GEO_BASE_URL")
TIMEOUT_SECOND = 10