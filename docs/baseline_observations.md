# Phase 0: Manual Exploration & Baseline Observations

This document records the baseline behavior, response times, and initial observations of the OpenWeatherMap API endpoints using Postman. These manual findings form the basis for our automated PyTest suites.

All requests include `appid={{apiKey}}` unless the row says otherwise. ⚠️ marks a surprise worth following up.

Times: rows 1–9 and 11 were measured in Postman (web). Rows 8b, 10 and 12–15 were measured with a Python `requests` script from WSL, which is consistently slower (~100–250 ms), so compare times only within the same source.

| # | Request | Status | Time (ms) | Notes |
|---|---|---|---|---|
| 1 | GET /weather?q=London,GB | 200 | 34 | name=London, country=GB (by city) |
| 2 | GET /weather?lat=51.5074&lon=-0.1278&units=metric | 200 | 34 | name=London, country=GB; units=metric → temp in °C. Typo `lad` first gave 400 "Nothing to geocode": unknown params are silently ignored (by coords) |
| 3 | GET /weather?q=Zzqxwvy | 404 | 122 | message="city not found". ⚠️ cod is a STRING "404" here (unknown city) |
| 4 | GET /weather?q=London,GB&appid=invalid | 401 | 40 | message="Invalid API key. Please see https://openweathermap.org/faq#error401 for more info." ⚠️ cod is a NUMBER 401 here (invalid key) |
| 5 | GET /weather?q=London,GB (appid omitted) | 401 | 32 | Identical body to #4: missing and invalid key are not distinguished (missing key) |
| 6 | GET /weather (no location params) | 400 | 37 | message="Nothing to geocode", cod is a STRING "400" (no location) |
| 7 | GET /weather?lat=a&lon=-0.1278&units=metric | 400 | 33 | message="wrong latitude", cod is a STRING "400" (invalid lat) |
| 8a | GET /weather?lat=90.0001&lon=0&units=metric | 400 | 37 | Same body as #7: out-of-range lat is rejected (lat out of range). ⚠️ Without `units` the same lat returns 200 (see findings) |
| 8b | GET /weather?lat=0&lon=0 | 200 | 208 | name="Globe", no `sys.country` field: valid response for open ocean (lat/lon zero) |
| 9 | GET /weather?q=São Paulo,BR | 200 | 38 | name keeps the "ã" (unicode city) |
| 10 | POST /weather?q=London,GB | 200 | 182 | ⚠️ POST is accepted and returns normal weather data; no 405 and no `Allow` header (unsupported method) |
| 11 | GET /weather?q=London,GB&mode=xml | 200 | 42 | Body is XML (`<current><city ...>`), Content-Type=`application/xml; charset=utf-8` (xml mode) |
| 12 | GET /forecast?q=Tokyo,JP&cnt=5 | 200 | 246 | cnt=5, `list` has 5 items. ⚠️ cod is a STRING "200" here, but a NUMBER 200 on /weather (forecast) |
| 13a | GET /forecast?q=Tokyo,JP&cnt=41 | 200 | 163 | ⚠️ No error: silently capped, cnt=40 and `list` has 40 items (cnt above max) |
| 13b | GET /forecast?q=Tokyo,JP&cnt=0 | 200 | 199 | ⚠️ No error: cnt=0 is ignored, returns all 40 items (cnt zero) |
| 14 | GET /direct?q=Paris,FR&limit=1 | 200 | 128 | Body is an ARRAY with 1 object: name=Paris, lat, lon, country=FR, plus `local_names` (geocode) |
| 15 | GET /direct?q= | 400 | 101 | cod="400" (STRING), message="Nothing to geocode": same error format as /weather #6 (geocode empty q) |

## Findings

Defects and doc mismatches are filed as GitHub Issues labeled `upstream` (Phase 9, last verified 2026-10-08). Each `xfail` reason in the tests names its issue, and `strict=True` makes the suite fail if the API is fixed, which is the signal to close the issue.

| # | Finding | Type | Severity | Test |
|---|---|---|---|---|
| [#1](https://github.com/Mantix1/api-test-automation-suite/issues/1) | Invalid or empty `lat` with `lon=0` returns 200 for (51.5, 0) "Poplar"; any `units` value makes it a correct 400 | Defect | High | TC-NEG-08 (xfail) |
| [#2](https://github.com/Mantix1/api-test-automation-suite/issues/2) | `±90.0001` / `±180.0001` return 200 (clamped) without `units`, 400 with `units`; `±90.01` always 400 | Defect | Medium | TC-BND-02 (xfail) |
| [#3](https://github.com/Mantix1/api-test-automation-suite/issues/3) | POST `/weather` returns 200; PUT/DELETE/PATCH correctly return 405 | Defect | Medium | TC-NEG-07 (xfail) |
| [#4](https://github.com/Mantix1/api-test-automation-suite/issues/4) | 405 responses have no `Allow` header (RFC 9110) and say "Internal error" | Defect | Low | none (manual) |
| [#5](https://github.com/Mantix1/api-test-automation-suite/issues/5) | `/forecast` `cnt=0`, `-1`, `41` return 200 with 40 entries; `cnt=abc` correctly 400 | Defect | Medium | TC-BND-06 (xfail) |
| [#6](https://github.com/Mantix1/api-test-automation-suite/issues/6) | `/direct` `limit=0` returns 10 results (docs: max 5); `limit=-1` returns 404 "not found" | Defect | Medium | TC-BND-07 (xfail) |
| [#7](https://github.com/Mantix1/api-test-automation-suite/issues/7) | `cod` is a number on `/weather` 200 and on 401 (all endpoints), a string on 400/404 and on `/forecast` 200 | Doc mismatch | Low | TC-CON-04 (xfail), schemas |
| [#8](https://github.com/Mantix1/api-test-automation-suite/issues/8) | Key accepted in an undocumented `x-api-key` header (the Postman collection uses it to keep the key out of URLs) | Doc mismatch | Low | none (Postman relies on it) |

### Observations (not filed)

- **Raw `q=%ZZ`** (malformed percent-encoding) returns 404 "city not found", not 400. (TC-NEG-06)
- **`mode=xml` errors are XML:** an unknown city returns `<Error><cod>404</cod><message>city not found</message></Error>` with `application/xml`. (TC-CON-05)
- **Edge coordinates have an empty `name`:** poles and ±180 return `name: ""`; `0,0` returns "Globe" with no `sys.country`. (TC-BND-01)
- **Whitespace-only `q`** returns 404 "city not found"; empty `q` returns 400 "Nothing to geocode". (TC-BND-03)
- **Unicode `q` works** ("São Paulo,BR", "Москва,RU", "東京,JP"; names in English, accents kept), but bare "東京" returns 404. (TC-BND-04)
- **Long and special-character `q`** (1000 chars, symbols, HTML, SQL-like) always gets a JSON 404, never a 5xx. (TC-BND-05)
- **`/direct` `limit=6`** is capped to 5 results, which matches the docs. (TC-BND-07)
- **Unknown or invalid values are silently ignored:** unknown params (`lad`), `units=kelvin` / `units=xyz` (treated as `standard`), `lang=zz` (English), `mode=bogus` (JSON). Found in the Phase 9 bug hunt.
- **`cnt=2.5`** returns 400 "2.5 is not a number" (correct status, slightly misleading message: it is a number, just not an integer).
