import statistics
import time

import pytest

SAMPLES = 20
PAUSE_SECONDS = 1
P95_THRESHOLD_MS = 2000


@pytest.mark.performance
@pytest.mark.tc("TC-PERF-01")
@pytest.mark.parametrize(
    "helper, params",
    [
        pytest.param("get_current_weather", {"q": "London,GB"}, id="weather"),
        pytest.param("get_forecast", {"q": "Tokyo,JP", "cnt": 5}, id="forecast"),
        pytest.param("geocode_direct", {"q": "Paris,FR", "limit": 1}, id="geocoding"),
    ],
)
def test_endpoint_p95_response_time(api_client, record_property, helper, params):
    timings_ms = []
    for _ in range(SAMPLES):
        response = getattr(api_client, helper)(**params)
        assert response.status_code == 200
        timings_ms.append(response.elapsed.total_seconds() * 1000)
        time.sleep(PAUSE_SECONDS)

    p95 = statistics.quantiles(timings_ms, n=20, method="inclusive")[18]
    record_property("p95_ms", round(p95))
    assert p95 < P95_THRESHOLD_MS, f"p95 {p95:.0f} ms (max {max(timings_ms):.0f} ms)"
