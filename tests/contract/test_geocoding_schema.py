import pytest

from framework.schemas import assert_matches_schema


@pytest.mark.contract
@pytest.mark.tc("TC-CON-02")
@pytest.mark.parametrize(
    "q, limit",
    [
        pytest.param("Paris,FR", 1, id="single_result"),
        pytest.param("London", 5, id="multiple_results"),
    ],
)
def test_geocoding_matches_schema(api_client, q, limit):
    response = api_client.geocode_direct(q=q, limit=limit)

    assert response.status_code == 200
    body = response.json()
    assert 1 <= len(body) <= limit
    assert_matches_schema(body, "geocoding_direct.json")
