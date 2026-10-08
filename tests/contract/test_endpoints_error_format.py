import pytest

from framework.schemas import assert_matches_schema

COD_IS_A_NUMBER = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Upstream #7: 401 errors send cod as a number; other errors send a string",
)


@pytest.mark.contract
@pytest.mark.regression
@pytest.mark.tc("TC-CON-04")
@pytest.mark.parametrize(
    "helper, params, expected_status",
    [
        pytest.param("get_current_weather", {"q": "Zzqxwvy"}, 404, id="weather_404"),
        pytest.param("get_current_weather", {}, 400, id="weather_400"),
        pytest.param("get_forecast", {"q": "Zzqxwvy"}, 404, id="forecast_404"),
        pytest.param("geocode_direct", {"q": ""}, 400, id="geocoding_400"),
        pytest.param(
            "get_current_weather",
            {"q": "London,GB", "appid": "invalid_api_key"},
            401,
            id="weather_401",
            marks=COD_IS_A_NUMBER,
        ),
        pytest.param(
            "geocode_direct",
            {"q": "Paris,FR", "appid": "invalid_api_key"},
            401,
            id="geocoding_401",
            marks=COD_IS_A_NUMBER,
        ),
    ],
)
def test_error_body_has_consistent_format(api_client, helper, params, expected_status):
    response = getattr(api_client, helper)(**params)

    assert response.status_code == expected_status
    body = response.json()
    assert str(body["cod"]) == str(expected_status)
    assert_matches_schema(body, "error.json")
