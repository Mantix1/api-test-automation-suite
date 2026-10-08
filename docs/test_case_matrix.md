# Test Case Matrix

Every automated test carries `@pytest.mark.tc("TC-XXX-NN")` linking it to a row below. One ID can cover several parametrized cases, so 25 IDs expand to 76 test runs.

- **Priority:** P1 cases carry the `regression` marker and run on every push and pull request. P2 cases run nightly.
- **Status:** ✅ passes. ⚠️ the API currently deviates from the expected result; those cases are `xfail(strict=True)` and linked to an [upstream issue](https://github.com/Mantix1/api-test-automation-suite/issues?q=label%3Aupstream). If the API is fixed, the suite fails, which is the signal to close the issue.
- **Postman:** the case is also in the Postman collection (Smoke folder on push, Extended nightly).

| ID | Title | Endpoint | Priority | Expected result | Cases | Status | Postman |
|---|---|---|---|---|---|---|---|
| **Functional** | | | | | | | |
| TC-FUN-01 | Current weather by city name | `/weather` | P1 | 200; `name` London, `sys.country` GB | 1 | ✅ | Smoke |
| TC-FUN-02 | Current weather by coordinates | `/weather` | P1 | 200; `coord` within 0.1° of the request | 1 | ✅ | Smoke |
| TC-FUN-03 | Forecast with `cnt=5` | `/forecast` | P1 | 200; 5 entries, timestamps 10800 s apart, Tokyo/JP | 1 | ✅ | Smoke |
| TC-FUN-04 | Geocode `Paris,FR` | `/direct` | P1 | 200; list of 1, Paris/FR, coordinates within 0.1° | 1 | ✅ | Smoke |
| **Negative** | | | | | | | |
| TC-NEG-01 | Invalid API key | `/weather` | P1 | 401 "Invalid API key" | 1 | ✅ | Smoke |
| TC-NEG-02 | Missing API key | `/weather` | P1 | 401 "Invalid API key" | 1 | ✅ | Smoke |
| TC-NEG-03 | Unknown city | `/weather` | P1 | 404 "city not found" | 1 | ✅ | Smoke |
| TC-NEG-04 | No location parameters | `/weather` | P2 | 400 "Nothing to geocode" | 1 | ✅ | Extended |
| TC-NEG-05 | Non-numeric latitude | `/weather` | P2 | 400 "wrong latitude" | 1 | ✅ | Extended |
| TC-NEG-06 | Malformed percent-encoding `q=%ZZ` | `/weather` | P2 | 4xx with a JSON `message` (API returns 404) | 1 | ✅ | |
| TC-NEG-07 | Unsupported HTTP methods | `/weather` | P2 | 405 for POST, PUT, DELETE, PATCH | 4 | ⚠️ POST [#3](https://github.com/Mantix1/api-test-automation-suite/issues/3) | |
| TC-NEG-08 | Invalid latitude with `lon=0` | `/weather` | P2 | 400 "wrong latitude" | 4 | ⚠️ 3 cases [#1](https://github.com/Mantix1/api-test-automation-suite/issues/1) | |
| **Boundary** | | | | | | | |
| TC-BND-01 | Coordinate edges (±90, ±180, 0/0) | `/weather` | P2 | 200; `coord` echoes the request | 7 | ✅ | Extended |
| TC-BND-02 | Just outside ±90 / ±180 | `/weather` | P2 | 400 "wrong latitude/longitude" | 9 | ⚠️ 4 cases [#2](https://github.com/Mantix1/api-test-automation-suite/issues/2) | Extended |
| TC-BND-03 | Empty and whitespace `q` | `/weather` | P2 | 400 "Nothing to geocode" / 404 "city not found" | 2 | ✅ | |
| TC-BND-04 | Unicode `q` (Latin accent, Cyrillic, CJK) | `/weather` | P2 | 200; English name, accents kept | 3 | ✅ | Extended |
| TC-BND-05 | 1000-char and special-character `q` | `/weather` | P2 | 404 "city not found", never 5xx | 4 | ✅ | |
| TC-BND-06 | Forecast `cnt` limits | `/forecast` | P2 | 1 and 40 return that many; 0, -1, 41, `abc` return 400 | 6 | ⚠️ 3 cases [#5](https://github.com/Mantix1/api-test-automation-suite/issues/5) | Extended |
| TC-BND-07 | Geocoding `limit` | `/direct` | P2 | 1, 5, 6 return at most 5; 0, -1, `abc` return 400 | 6 | ⚠️ 2 cases [#6](https://github.com/Mantix1/api-test-automation-suite/issues/6) | |
| **Contract** | | | | | | | |
| TC-CON-01 | Weather and forecast match JSON Schema | `/weather`, `/forecast` | P1 | Body valid against `schemas/current_weather.json`, `schemas/forecast.json` | 3 | ✅ | Smoke |
| TC-CON-02 | Geocoding matches JSON Schema | `/direct` | P2 | Body valid against `schemas/geocoding_direct.json` | 2 | ✅ | Smoke |
| TC-CON-03 | JSON `Content-Type` | all | P1 | `application/json; charset=utf-8`, including errors | 4 | ✅ | Smoke |
| TC-CON-04 | Consistent error format | all | P1 | Every error matches `schemas/error.json` (string `cod`, non-empty `message`) | 6 | ⚠️ 401 cases [#7](https://github.com/Mantix1/api-test-automation-suite/issues/7) | Extended |
| TC-CON-05 | `mode=xml` | `/weather`, `/forecast` | P2 | `application/xml`, parseable, expected root element (incl. `<Error>`) | 3 | ✅ | Extended |
| **Performance** | | | | | | | |
| TC-PERF-01 | p95 response time | all | P2 (nightly) | p95 of 20 calls per endpoint under 2000 ms | 3 | ✅ | |

## Where each test lives

| ID | File |
|---|---|
| FUN-01, 02 | `tests/functional/test_weather_current_happy_path.py` |
| FUN-03 | `tests/functional/test_forecast_happy_path.py` |
| FUN-04 | `tests/functional/test_geocoding_happy_path.py` |
| NEG-01, 02 | `tests/negative/test_weather_current_auth.py` |
| NEG-03..06, 08 | `tests/negative/test_weather_current_invalid_input.py` |
| NEG-07 | `tests/negative/test_weather_current_methods.py` |
| BND-01, 02 | `tests/boundary/test_weather_current_coordinates.py` |
| BND-03..05 | `tests/boundary/test_weather_current_city_query.py` |
| BND-06 | `tests/boundary/test_forecast_count.py` |
| BND-07 | `tests/boundary/test_geocoding_limit.py` |
| CON-01 | `tests/contract/test_weather_current_schema.py`, `tests/contract/test_forecast_schema.py` |
| CON-02 | `tests/contract/test_geocoding_schema.py` |
| CON-03 | `tests/contract/test_endpoints_content_type.py` |
| CON-04 | `tests/contract/test_endpoints_error_format.py` |
| CON-05 | `tests/contract/test_endpoints_xml_mode.py` |
| PERF-01 | `tests/performance/test_endpoints_response_time.py` |

Run one case by ID with `pytest -k` on the function name, or list a category with `pytest -m boundary -v`.
