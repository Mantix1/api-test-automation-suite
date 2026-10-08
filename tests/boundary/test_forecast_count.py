import pytest

SILENTLY_CORRECTS_CNT = pytest.mark.xfail(
    strict=True,
    raises=AssertionError,
    reason="Upstream: out-of-range cnt returns 200 with 40 items instead of 400",
)


@pytest.mark.boundary
@pytest.mark.tc("TC-BND-06")
@pytest.mark.parametrize(
    "cnt",
    [
        pytest.param(1, id="min"),
        pytest.param(40, id="max"),
    ],
)
def test_forecast_accepts_cnt_at_limits(api_client, cnt):
    response = api_client.get_forecast(q="Tokyo,JP", cnt=cnt)

    assert response.status_code == 200
    body = response.json()
    assert body["cnt"] == cnt
    assert len(body["list"]) == cnt


@pytest.mark.boundary
@pytest.mark.tc("TC-BND-06")
@pytest.mark.parametrize(
    "cnt",
    [
        pytest.param(0, id="zero", marks=SILENTLY_CORRECTS_CNT),
        pytest.param(-1, id="negative", marks=SILENTLY_CORRECTS_CNT),
        pytest.param(41, id="above_max", marks=SILENTLY_CORRECTS_CNT),
        pytest.param("abc", id="not_a_number"),
    ],
)
def test_forecast_rejects_invalid_cnt(api_client, cnt):
    response = api_client.get_forecast(q="Tokyo,JP", cnt=cnt)

    assert response.status_code == 400
