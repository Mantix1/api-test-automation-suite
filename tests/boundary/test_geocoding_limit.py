import pytest

IGNORES_INVALID_LIMIT = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Upstream #6: limit=0 returns 10 results and limit=-1 returns 404 instead of 400",
)


@pytest.mark.boundary
@pytest.mark.tc("TC-BND-07")
@pytest.mark.parametrize(
    "limit",
    [
        pytest.param(1, id="min"),
        pytest.param(5, id="max"),
        pytest.param(6, id="above_max_is_capped"),
    ],
)
def test_geocoding_returns_at_most_five_results(api_client, limit):
    response = api_client.geocode_direct(q="London", limit=limit)

    assert response.status_code == 200
    body = response.json()
    assert 1 <= len(body) <= min(limit, 5)


@pytest.mark.boundary
@pytest.mark.tc("TC-BND-07")
@pytest.mark.parametrize(
    "limit",
    [
        pytest.param(0, id="zero", marks=IGNORES_INVALID_LIMIT),
        pytest.param(-1, id="negative", marks=IGNORES_INVALID_LIMIT),
        pytest.param("abc", id="not_a_number"),
    ],
)
def test_geocoding_rejects_invalid_limit(api_client, limit):
    response = api_client.geocode_direct(q="London", limit=limit)

    assert response.status_code == 400
