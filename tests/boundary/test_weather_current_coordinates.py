import pytest

ACCEPTS_TINY_OVERFLOW = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Upstream: values just past the limit return 200 unless units is set",
)


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


@pytest.mark.boundary
@pytest.mark.tc("TC-BND-02")
@pytest.mark.parametrize(
    "params, expected_message",
    [
        pytest.param({"lat": 90.01, "lon": 0}, "wrong latitude", id="lat_above_max"),
        pytest.param({"lat": -90.01, "lon": 0}, "wrong latitude", id="lat_below_min"),
        pytest.param({"lat": 0, "lon": 180.01}, "wrong longitude", id="lon_above_max"),
        pytest.param({"lat": 0, "lon": -180.01}, "wrong longitude", id="lon_below_min"),
        pytest.param(
            {"lat": 90.0001, "lon": 0, "units": "metric"},
            "wrong latitude",
            id="lat_tiny_overflow_with_units",
        ),
        pytest.param(
            {"lat": 90.0001, "lon": 0},
            "wrong latitude",
            id="lat_tiny_overflow",
            marks=ACCEPTS_TINY_OVERFLOW,
        ),
        pytest.param(
            {"lat": -90.0001, "lon": 0},
            "wrong latitude",
            id="lat_tiny_underflow",
            marks=ACCEPTS_TINY_OVERFLOW,
        ),
        pytest.param(
            {"lat": 0, "lon": 180.0001},
            "wrong longitude",
            id="lon_tiny_overflow",
            marks=ACCEPTS_TINY_OVERFLOW,
        ),
        pytest.param(
            {"lat": 0, "lon": -180.0001},
            "wrong longitude",
            id="lon_tiny_underflow",
            marks=ACCEPTS_TINY_OVERFLOW,
        ),
    ],
)
def test_current_weather_rejects_out_of_range_coordinates(api_client, params, expected_message):
    response = api_client.get_current_weather(**params)

    assert response.status_code == 400
    body = response.json()
    assert body["message"] == expected_message
