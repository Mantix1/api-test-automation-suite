import pytest

from framework.schemas import assert_matches_schema


@pytest.mark.contract
@pytest.mark.regression
@pytest.mark.tc("TC-CON-01")
def test_forecast_matches_schema(api_client):
    response = api_client.get_forecast(q="Tokyo,JP", cnt=5)

    assert response.status_code == 200
    assert_matches_schema(response.json(), "forecast.json")
