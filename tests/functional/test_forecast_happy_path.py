import pytest

@pytest.mark.functional
@pytest.mark.regression
@pytest.mark.tc("TC-FUN-03")
def test_forecast_by_city_with_count(api_client):
    response = api_client.get_forecast(q="Tokyo,JP", cnt=5)
    assert response.status_code == 200
    body = response.json()
    assert body["cnt"] == 5
    assert len(body["list"]) == 5
    assert body["city"]["name"] == "Tokyo"
    assert body["city"]["country"] == "JP"
    timestamps = [item["dt"] for item in body["list"]]
    for (t1, t2) in zip(timestamps, timestamps[1:]):
        assert t2 - t1 == 10800 # Ensure timestamps are in 3-hour intervals (10800 seconds)
