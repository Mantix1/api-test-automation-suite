import pytest

from framework.schemas import assert_matches_schema


@pytest.mark.contract
@pytest.mark.regression
@pytest.mark.tc("TC-CON-01")
@pytest.mark.parametrize(
    "params",
    [
        pytest.param({"q": "London,GB"}, id="by_city"),
        pytest.param({"lat": 35.6895, "lon": 139.6917, "units": "metric"}, id="by_coords_metric"),
    ],
)
def test_current_weather_matches_schema(api_client, params):
    response = api_client.get_current_weather(**params)

    assert response.status_code == 200
    assert_matches_schema(response.json(), "current_weather.json")
