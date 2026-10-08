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

@pytest.mark.functional
@pytest.mark.regression
@pytest.mark.tc("TC-FUN-02")
def test_current_weather_by_coordinates(api_client):
    response = api_client.get_current_weather(lat=51.5074, lon=-0.1278, units="metric")
    assert response.status_code == 200
    body = response.json()
    assert body["coord"]["lat"] == pytest.approx(51.5074, abs=0.1)
    assert body["coord"]["lon"] == pytest.approx(-0.1278, abs=0.1)
    assert body["sys"]["country"] == "GB"
    assert -60 <= body["main"]["temp"] <= 60
