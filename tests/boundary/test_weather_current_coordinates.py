import pytest


@pytest.mark.boundary
@pytest.mark.tc("TC-BND-01")
@pytest.mark.parametrize(
    "lat, lon",
    [
        pytest.param(90, 0, id="north_pole"),
        pytest.param(-90, 0, id="south_pole"),
        pytest.param(0, 180, id="lon_max"),
        pytest.param(0, -180, id="lon_min"),
        pytest.param(90, 180, id="max_corner"),
        pytest.param(-90, -180, id="min_corner"),
        pytest.param(0, 0, id="origin"),
    ],
)
def test_current_weather_accepts_coordinate_edges(api_client, lat, lon):
    response = api_client.get_current_weather(lat=lat, lon=lon)

    assert response.status_code == 200
    body = response.json()
    assert body["coord"]["lat"] == pytest.approx(lat)
    assert body["coord"]["lon"] == pytest.approx(lon)
    assert isinstance(body["name"], str)
