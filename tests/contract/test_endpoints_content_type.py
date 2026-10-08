import pytest


@pytest.mark.contract
@pytest.mark.regression
@pytest.mark.tc("TC-CON-03")
@pytest.mark.parametrize(
    "helper, params",
    [
        pytest.param("get_current_weather", {"q": "London,GB"}, id="weather"),
        pytest.param("get_forecast", {"q": "Tokyo,JP", "cnt": 1}, id="forecast"),
        pytest.param("geocode_direct", {"q": "Paris,FR", "limit": 1}, id="geocoding"),
        pytest.param("get_current_weather", {"q": "Zzqxwvy"}, id="weather_error"),
    ],
)
def test_endpoint_returns_json_content_type(api_client, helper, params):
    response = getattr(api_client, helper)(**params)

    media_type, _, parameters = response.headers["Content-Type"].partition(";")
    assert media_type.strip() == "application/json"
    assert parameters.strip().lower() == "charset=utf-8"
