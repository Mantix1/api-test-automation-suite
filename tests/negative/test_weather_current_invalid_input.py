import pytest

from framework import endpoints


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.tc("TC-NEG-03")
def test_current_weather_unknown_city(api_client):
    response = api_client.get_current_weather(q="Zzqxwvy")

    assert response.status_code == 404
    body = response.json()
    assert "city not found" in body["message"]
    assert str(body["cod"]) == "404"


@pytest.mark.negative
@pytest.mark.tc("TC-NEG-04")
def test_current_weather_without_location(api_client):
    response = api_client.get_current_weather()

    assert response.status_code == 400
    body = response.json()
    assert "Nothing to geocode" in body["message"]
    assert str(body["cod"]) == "400"


@pytest.mark.negative
@pytest.mark.tc("TC-NEG-05")
def test_current_weather_non_numeric_latitude(api_client):
    response = api_client.get_current_weather(lat="abc", lon=-0.1278)

    assert response.status_code == 400
    body = response.json()
    assert "wrong latitude" in body["message"]
    assert str(body["cod"]) == "400"


@pytest.mark.negative
@pytest.mark.tc("TC-NEG-06")
def test_current_weather_malformed_encoding(api_client):
    response = api_client.get_raw_query(endpoints.CURRENT_WEATHER, "q=%ZZ")

    sent_raw = response.request.url.endswith("&q=%ZZ")
    assert sent_raw, "query was re-encoded; the test did not send malformed input"
    assert 400 <= response.status_code < 500
    body = response.json()
    assert "message" in body


FALLS_BACK_TO_LONDON = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Upstream #1: invalid lat with lon=0 returns 200 for (51.5, 0) unless units is set",
)


@pytest.mark.negative
@pytest.mark.tc("TC-NEG-08")
@pytest.mark.parametrize(
    "params, expected_message",
    [
        pytest.param({"lat": "abc", "lon": 0}, "wrong latitude", id="non_numeric_lat", marks=FALLS_BACK_TO_LONDON),
        pytest.param({"lat": "12,3", "lon": 0}, "wrong latitude", id="comma_decimal_lat", marks=FALLS_BACK_TO_LONDON),
        pytest.param({"lat": "", "lon": 0}, "wrong latitude", id="empty_lat", marks=FALLS_BACK_TO_LONDON),
        pytest.param({"lat": "abc", "lon": 0, "units": "metric"}, "wrong latitude", id="non_numeric_lat_with_units"),
    ],
)
def test_current_weather_invalid_latitude_at_zero_longitude(api_client, params, expected_message):
    response = api_client.get_current_weather(**params)

    assert response.status_code == 400
    body = response.json()
    assert body["message"] == expected_message
