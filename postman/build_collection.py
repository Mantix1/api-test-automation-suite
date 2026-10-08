"""Build the Postman collection from Python so it stays in sync with schemas/.

Run from the project root:
    .venv/bin/python -m postman.build_collection           # write the collection
    .venv/bin/python -m postman.build_collection --check   # fail if the file is out of date
"""
import argparse
import json
import sys
from pathlib import Path

from framework.schemas import load_schema

POSTMAN_DIR = Path(__file__).resolve().parent
COLLECTION_PATH = POSTMAN_DIR / "OpenWeatherMap_API_Tests.postman_collection.json"

# Collection variable name -> file in schemas/. Tests read the schema with
# JSON.parse(pm.collectionVariables.get(name)).
SCHEMA_VARIABLES = {
    "schemaCurrentWeather": "current_weather.json",
    "schemaForecast": "forecast.json",
    "schemaGeocodingDirect": "geocoding_direct.json",
    "schemaError": "error.json",
}

# The key goes in an x-api-key header instead of appid, so it never appears in
# URLs, which Newman prints in its CLI output and HTML report.
API_KEY_AUTH = {
    "type": "apikey",
    "apikey": [
        {"key": "key", "value": "x-api-key", "type": "string"},
        {"key": "value", "value": "{{apiKey}}", "type": "string"},
        {"key": "in", "value": "header", "type": "string"},
    ],
}
NO_AUTH = {"type": "noauth"}


def status_is(code):
    return [f'pm.test("Status is {code}", () => pm.response.to.have.status({code}));']


def json_content_type():
    return [
        'pm.test("Content-Type is application/json; charset=utf-8", () => {',
        '    pm.response.to.have.header("Content-Type", "application/json; charset=utf-8");',
        "});",
    ]


def matches_schema(variable):
    return [
        f'pm.test("Body matches {SCHEMA_VARIABLES[variable]}", () => {{',
        f'    pm.response.to.have.jsonSchema(JSON.parse(pm.collectionVariables.get("{variable}")));',
        "});",
    ]


def error_message_is(message):
    return [
        f'pm.test("Error message is \\"{message}\\"", () => {{',
        f'    pm.expect(pm.response.json().message).to.eql("{message}");',
        "});",
    ]


def request(name, url, tests, auth=None):
    item = {
        "name": name,
        "event": [{"listen": "test", "script": {"type": "text/javascript", "exec": tests}}],
        "request": {"method": "GET", "header": [], "url": url},
    }
    if auth is not None:
        item["request"]["auth"] = auth
    return item


SMOKE = [
    request(
        "TC-FUN-01 Weather by city",
        "{{baseUrl}}/weather?q=London,GB",
        status_is(200)
        + json_content_type()
        + matches_schema("schemaCurrentWeather")
        + [
            'pm.test("City is London, GB", () => {',
            "    const body = pm.response.json();",
            '    pm.expect(body.name).to.eql("London");',
            '    pm.expect(body.sys.country).to.eql("GB");',
            "});",
        ],
    ),
    request(
        "TC-FUN-02 Weather by coordinates",
        "{{baseUrl}}/weather?lat=51.5074&lon=-0.1278&units=metric",
        status_is(200)
        + matches_schema("schemaCurrentWeather")
        + [
            'pm.test("Coordinates are near the request", () => {',
            "    const coord = pm.response.json().coord;",
            "    pm.expect(coord.lat).to.be.closeTo(51.5074, 0.1);",
            "    pm.expect(coord.lon).to.be.closeTo(-0.1278, 0.1);",
            "});",
        ],
    ),
    request(
        "TC-FUN-03 Forecast with cnt=5",
        "{{baseUrl}}/forecast?q=Tokyo,JP&cnt=5",
        status_is(200)
        + json_content_type()
        + matches_schema("schemaForecast")
        + [
            'pm.test("Returns 5 entries, 3 hours apart", () => {',
            "    const body = pm.response.json();",
            "    pm.expect(body.cnt).to.eql(5);",
            "    pm.expect(body.list).to.have.lengthOf(5);",
            "    for (let i = 1; i < body.list.length; i++) {",
            "        pm.expect(body.list[i].dt - body.list[i - 1].dt).to.eql(10800);",
            "    }",
            "});",
        ],
    ),
    request(
        "TC-FUN-04 Geocode Paris,FR",
        "{{geoBaseUrl}}/direct?q=Paris,FR&limit=1",
        status_is(200)
        + json_content_type()
        + matches_schema("schemaGeocodingDirect")
        + [
            'pm.test("One result: Paris, FR", () => {',
            "    const body = pm.response.json();",
            "    pm.expect(body).to.have.lengthOf(1);",
            '    pm.expect(body[0].name).to.eql("Paris");',
            '    pm.expect(body[0].country).to.eql("FR");',
            "});",
        ],
    ),
    request(
        "TC-NEG-01 Invalid API key",
        "{{baseUrl}}/weather?q=London,GB&appid=invalid_api_key",
        status_is(401)
        + [
            'pm.test("Message says the key is invalid", () => {',
            '    pm.expect(pm.response.json().message).to.include("Invalid API key");',
            "});",
        ],
        auth=NO_AUTH,
    ),
    request(
        "TC-NEG-02 Missing API key",
        "{{baseUrl}}/weather?q=London,GB",
        status_is(401)
        + [
            'pm.test("Message says the key is invalid", () => {',
            '    pm.expect(pm.response.json().message).to.include("Invalid API key");',
            "});",
        ],
        auth=NO_AUTH,
    ),
    request(
        "TC-NEG-03 Unknown city",
        "{{baseUrl}}/weather?q=Zzqxwvy",
        status_is(404) + error_message_is("city not found") + matches_schema("schemaError"),
    ),
]

EXTENDED = [
    request(
        "TC-NEG-04 No location",
        "{{baseUrl}}/weather",
        status_is(400) + error_message_is("Nothing to geocode") + matches_schema("schemaError"),
    ),
    request(
        "TC-NEG-05 Non-numeric latitude",
        "{{baseUrl}}/weather?lat=abc&lon=-0.1278",
        status_is(400) + error_message_is("wrong latitude") + matches_schema("schemaError"),
    ),
    request(
        "TC-BND-01 Coordinate corner 90,180",
        "{{baseUrl}}/weather?lat=90&lon=180",
        status_is(200)
        + [
            'pm.test("Coordinates are echoed back", () => {',
            "    const coord = pm.response.json().coord;",
            "    pm.expect(coord.lat).to.eql(90);",
            "    pm.expect(coord.lon).to.eql(180);",
            "});",
        ],
    ),
    request(
        "TC-BND-02 Latitude above 90",
        "{{baseUrl}}/weather?lat=90.01&lon=0",
        status_is(400) + error_message_is("wrong latitude"),
    ),
    request(
        "TC-BND-04 Unicode city name",
        "{{baseUrl}}/weather?q=São Paulo,BR",
        status_is(200)
        + [
            'pm.test("Name keeps the accent", () => {',
            '    pm.expect(pm.response.json().name).to.eql("São Paulo");',
            "});",
        ],
    ),
    request(
        "TC-BND-06 Forecast with cnt=40",
        "{{baseUrl}}/forecast?q=Tokyo,JP&cnt=40",
        status_is(200)
        + [
            'pm.test("Returns 40 entries", () => {',
            "    pm.expect(pm.response.json().list).to.have.lengthOf(40);",
            "});",
        ],
    ),
    request(
        "TC-CON-04 Geocoding error format",
        "{{geoBaseUrl}}/direct?q=",
        status_is(400) + error_message_is("Nothing to geocode") + matches_schema("schemaError"),
    ),
    request(
        "TC-CON-05 XML mode",
        "{{baseUrl}}/weather?q=London,GB&mode=xml",
        status_is(200)
        + [
            'pm.test("Content-Type is application/xml", () => {',
            '    pm.expect(pm.response.headers.get("Content-Type")).to.include("application/xml");',
            "});",
            'pm.test("Body parses as XML with a <current> root", () => {',
            "    pm.expect(xml2Json(pm.response.text())).to.have.property(\"current\");",
            "});",
        ],
    ),
]


def build():
    return {
        "info": {
            "name": "OpenWeatherMap API Tests",
            "description": (
                "Generated by postman/build_collection.py; edit that file, not this one. "
                "Smoke runs on every push, Extended runs nightly. "
                "Schemas are copied from schemas/ into collection variables."
            ),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "auth": API_KEY_AUTH,
        "item": [
            {"name": "Smoke", "item": SMOKE},
            {"name": "Extended", "item": EXTENDED},
        ],
        "variable": [
            {"key": name, "value": json.dumps(load_schema(file), separators=(",", ":"))}
            for name, file in SCHEMA_VARIABLES.items()
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="exit 1 if the collection file is out of date")
    args = parser.parse_args()

    text = json.dumps(build(), indent=2, ensure_ascii=False) + "\n"
    if args.check:
        current = COLLECTION_PATH.read_text(encoding="utf-8") if COLLECTION_PATH.exists() else ""
        if current != text:
            sys.exit(f"{COLLECTION_PATH.name} is out of date; run: python -m postman.build_collection")
        print(f"{COLLECTION_PATH.name} is up to date")
        return
    COLLECTION_PATH.write_text(text, encoding="utf-8")
    print(f"wrote {COLLECTION_PATH.relative_to(POSTMAN_DIR.parent)}")


if __name__ == "__main__":
    main()
