# OpenWeatherMap API Test Automation Suite

[![CI](https://github.com/Mantix1/api-test-automation-suite/actions/workflows/ci.yml/badge.svg)](https://github.com/Mantix1/api-test-automation-suite/actions/workflows/ci.yml)
[![Nightly](https://github.com/Mantix1/api-test-automation-suite/actions/workflows/nightly.yml/badge.svg)](https://github.com/Mantix1/api-test-automation-suite/actions/workflows/nightly.yml)

An API test suite for the public [OpenWeatherMap API](https://openweathermap.org/api), built with pytest and Postman/Newman and run in GitHub Actions. It covers three endpoints with functional, negative, boundary, contract and performance tests, and it has found **6 defects and 2 documentation mismatches** in the live API, each filed as a [GitHub issue](https://github.com/Mantix1/api-test-automation-suite/issues?q=label%3Aupstream) and tracked by a test.

| | |
|---|---|
| **Endpoints** | `GET /data/2.5/weather`, `GET /data/2.5/forecast`, `GET /geo/1.0/direct` |
| **Test cases** | 25 IDs, 76 test runs: see the [test case matrix](docs/test_case_matrix.md) |
| **Stack** | Python 3.12, pytest, requests, jsonschema (Draft-07), pytest-html, Postman, Newman + htmlextra, GitHub Actions |
| **Runs** | Every push/PR: P1 regression subset + Newman Smoke folder. Nightly: everything, including performance |

## Bugs found

The most serious one: if `lat` is not a valid number (even `abc` or empty) and `lon=0`, `/weather` returns **200 with London's weather** instead of an error, so a client with a parsing bug silently shows the wrong city.

| Issue | Finding | Type | Severity |
|---|---|---|---|
| [#1](https://github.com/Mantix1/api-test-automation-suite/issues/1) | Invalid or empty `lat` with `lon=0` returns weather for London (51.5, 0) | Defect | High |
| [#2](https://github.com/Mantix1/api-test-automation-suite/issues/2) | `lat=90.0001` is accepted without `units`, rejected with it | Defect | Medium |
| [#3](https://github.com/Mantix1/api-test-automation-suite/issues/3) | `POST /weather` returns 200 instead of 405 | Defect | Medium |
| [#4](https://github.com/Mantix1/api-test-automation-suite/issues/4) | 405 responses have no `Allow` header and say "Internal error" | Defect | Low |
| [#5](https://github.com/Mantix1/api-test-automation-suite/issues/5) | `/forecast` silently turns `cnt=0`, `-1`, `41` into 40 | Defect | Medium |
| [#6](https://github.com/Mantix1/api-test-automation-suite/issues/6) | `/direct` `limit=0` returns 10 results (documented max is 5) | Defect | Medium |
| [#7](https://github.com/Mantix1/api-test-automation-suite/issues/7) | `cod` is a number on some responses and a string on others | Doc mismatch | Low |
| [#8](https://github.com/Mantix1/api-test-automation-suite/issues/8) | API key accepted in an undocumented `x-api-key` header | Doc mismatch | Low |

Each defect has a test that asserts the **correct** behavior and is marked `xfail(strict=True)` with the issue number in its reason. The suite stays green while the bug exists, and fails as soon as the API is fixed, which is the signal to re-verify and close the issue. Smaller observations are in [docs/baseline_observations.md](docs/baseline_observations.md).

## How it works

```
framework/           config (env/.env), endpoint URLs, API client, schema helper, report scrubber
schemas/             Draft-07 JSON Schemas, shared by pytest and the Postman collection
tests/
  functional/        happy paths                                      (TC-FUN)
  negative/          auth, invalid input, unsupported methods         (TC-NEG)
  boundary/          coordinate, query, cnt and limit edges           (TC-BND)
  contract/          schemas, Content-Type, error format, XML mode    (TC-CON)
  performance/       p95 response time                                (TC-PERF)
postman/             collection builder, generated collection, environment, Newman runner
.github/workflows/   ci.yml (push/PR), nightly.yml (03:00 UTC)
docs/                test case matrix, baseline observations
```

- **One API client.** `framework/api_client.py` wraps a `requests.Session` with a timeout and transport-level retries (429/5xx, GET only). Tests get it from a session-scoped `api_client` fixture and never hardcode URLs.
- **Markers and traceability.** `--strict-markers` is on. Every test has a category marker, `regression` if it is P1, and `tc("TC-XXX-NN")` linking it to the matrix.
- **Parametrized edges.** Boundary and negative tests use `pytest.param(..., id="readable_name")`, so each edge case is reported on its own.
- **Stable assertions.** The live API returns real weather, so tests assert types, ranges, relationships and fixed facts (city name, error message), never temperatures.
- **One set of schemas.** `schemas/*.json` are used by pytest (`framework/schemas.py`, which reports every violation with its JSON path) and are embedded into the Postman collection by `postman/build_collection.py`. CI fails if the collection is out of date.
- **Live API, rate-limited.** The free tier allows 60 calls/min, so tests run serially, the performance test paces itself at one call per second, and the nightly Newman job waits for pytest to finish.

## Keeping the API key secret

The key is the only secret, and OpenWeatherMap expects it in the URL (`appid`), which tends to leak into logs and reports. The suite handles that in layers:

- Locally it lives in `.env` (gitignored); in CI it is a GitHub Actions secret.
- Assertions never include URLs, because a failing assert would print `appid`.
- The Postman collection sends the key in an `x-api-key` header instead of the URL, and `postman/run_newman.py` keeps it out of files, hides it in the HTML report, masks console output, and deletes any report that still contains it.
- A connection error puts the full URL into pytest's report. `framework/scrub_reports.py` masks the key in every report, and CI uploads artifacts only after the scrub succeeds.

## Running locally

Requires Python 3.12+ and, for Newman, Node.js 24. Get a free API key at [openweathermap.org](https://home.openweathermap.org/users/sign_up).

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # then set OWM_API_KEY

pytest -m "not performance"     # everything except the ~60 s performance test
pytest -m regression            # P1 subset, as on every push
pytest -m boundary -v -rxX      # one category, with xfail reasons
pytest                          # full suite, as nightly

pytest --html=reports/report.html --self-contained-html --junitxml=reports/junit.xml
python -m framework.scrub_reports   # mask the key before sharing reports/
```

Postman and Newman:

```bash
npm ci
python -m postman.build_collection             # regenerate after editing the builder or schemas/
python -m postman.run_newman --folder Smoke    # or no --folder for everything
```

To explore in the Postman app, import `postman/OpenWeatherMap_API_Tests.postman_collection.json` and `postman/OpenWeatherMap.postman_environment.json`, then put your key in the environment's `apiKey` current value.

## CI

| Workflow | Trigger | Runs | Artifacts |
|---|---|---|---|
| [`ci.yml`](.github/workflows/ci.yml) | push and PR to `main` | `pytest -m regression`, Newman Smoke, collection freshness check | pytest-html, JUnit, Newman htmlextra (14 days) |
| [`nightly.yml`](.github/workflows/nightly.yml) | daily 03:00 UTC, manual | full pytest incl. performance, then all Newman folders | same, 30 days; p95 per endpoint in the JUnit XML |

Pull requests from forks are skipped because they cannot read the API key secret.

## Reporting a finding

Use the **Upstream API finding** issue template. Each finding is classified as Defect, Doc mismatch or Observation, gets a severity, a reproduction with `$OWM_API_KEY` in place of the real key, and a link to the test that tracks it.

## License

[MIT](LICENSE)
