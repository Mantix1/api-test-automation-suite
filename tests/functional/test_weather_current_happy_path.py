import pytest

@pytest.mark.functional
@pytest.mark.regression
@pytest.mark.tc("TC-FUN-01")
def test_current_weather_by_city_name(api_client):
    response = api_client.get_current_weather(q="London,GB")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "London"
    assert body["sys"]["country"] == "GB"
    assert isinstance(body["main"]["temp"], (int, float))
    