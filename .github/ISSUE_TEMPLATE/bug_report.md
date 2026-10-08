---
name: Upstream API finding
about: Report a bug or doc mismatch found in the OpenWeatherMap API
title: "[Upstream] "
labels: upstream
assignees: ""
---

<!-- Never paste a real API key. Use $OWM_API_KEY in commands. -->

## Summary

One sentence: what the API does wrong.

## Classification

- **Type:** Defect / Doc mismatch / Observation
- **Severity:** High / Medium / Low
- **Endpoint:** `GET /data/2.5/weather` / `GET /data/2.5/forecast` / `GET /geo/1.0/direct`

## Steps to reproduce

```bash
curl -s "https://api.openweathermap.org/data/2.5/weather?q=London,GB&appid=$OWM_API_KEY"
```

## Expected

What should happen, and why (link to the API docs or the HTTP spec).

## Actual

Status code and the relevant part of the response body.

## Evidence

- **Test:** `TC-XXX-NN` in `tests/...` (marked `xfail(strict=True)`, so the suite fails when this is fixed)
- **First seen:** YYYY-MM-DD

## Impact

Who is affected and how.
