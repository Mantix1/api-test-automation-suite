import pytest


@pytest.mark.functional
@pytest.mark.regression
@pytest.mark.tc("TC-FUN-04")
def test_geocoding_by_city_name(api_client):
    response = api_client.geocode_direct(q="Paris,FR", limit=1)

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    place = body[0]
    assert place["name"] == "Paris"
    assert place["country"] == "FR"
    assert place["lat"] == pytest.approx(48.8566, abs=0.1)
    assert place["lon"] == pytest.approx(2.3522, abs=0.1)
