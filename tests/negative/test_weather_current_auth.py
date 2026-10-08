import pytest

from framework import endpoints


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.tc("TC-NEG-01")
def test_current_weather_with_invalid_api_key(api_client):
    response = api_client.get_current_weather(q="London,GB", appid="invalid_api_key")

    assert response.status_code == 401
    body = response.json()
    assert "Invalid API key" in body["message"]
    assert str(body["cod"]) == "401"


@pytest.mark.negative
@pytest.mark.regression
@pytest.mark.tc("TC-NEG-02")
def test_current_weather_without_api_key(api_client):
    response = api_client.get(endpoints.CURRENT_WEATHER, params={"q": "London,GB"}, include_key=False)

    assert response.status_code == 401
    body = response.json()
    assert "Invalid API key" in body["message"]
    assert str(body["cod"]) == "401"
