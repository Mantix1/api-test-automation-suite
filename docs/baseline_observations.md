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

## Findings to follow up (Phase 9)

- **`cod` type is inconsistent:** number on /weather success (200) and 401, string on 400/404 errors and on /forecast success ("200"). Candidate for TC-CON-04.
- **Unsupported methods are accepted:** POST /weather returns 200 instead of 405. PUT, DELETE and PATCH correctly return 405. Candidate for TC-NEG-07 (marked `xfail`).
- **405 responses lack an `Allow` header and say "Internal error":** PUT/DELETE/PATCH return `{"cod":"405","message":"Internal error"}` with no `Allow` header (RFC 9110 requires one). Doc mismatch / Observation.
- **Invalid `cnt` is silently corrected:** `cnt=0`, `cnt=-1` and `cnt=41` return 40 items instead of an error (`cnt=abc` correctly returns 400 "abc is not a number"). TC-BND-06 (marked `xfail`).
- **Coordinate validation depends on `units`:** `lat=90.0001` / `lat=-90.0001` / `lon=±180.0001` return 200 (coord clamped to the limit) when `units` is omitted, but 400 "wrong latitude/longitude" when any `units` value is sent. Values from about 0.01 past the limit (e.g. `90.01`) are rejected either way. Defect (inconsistent validation). TC-BND-02 (marked `xfail`).
- **Edge coordinates have an empty `name`:** poles and ±180 return `name: ""`; only `0,0` returns "Globe". Observation (TC-BND-01).
- **Whitespace-only `q` returns 404, empty `q` returns 400:** `q=" "` gives "city not found", `q=""` gives "Nothing to geocode". Observation (TC-BND-03).
- **Unicode `q` works, but CJK needs a country code:** "São Paulo,BR", "Москва,RU" and "東京,JP" all resolve (names returned in English, accents kept); bare "東京" returns 404. Observation (TC-BND-04).
- **Long and special-character `q` is handled cleanly:** 1000 chars, symbols, HTML and SQL-like strings all return a JSON 404 "city not found", never a 5xx. (TC-BND-05)
- **Unknown query params are silently ignored** (e.g. `lad`). Observation, not a defect.
- **Malformed percent-encoding is not rejected:** raw `q=%ZZ` returns 404 "city not found" instead of 400 Bad Request. Observation. (TC-NEG-06)
