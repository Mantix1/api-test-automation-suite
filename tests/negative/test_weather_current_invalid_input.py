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
