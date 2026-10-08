import pytest

from framework import endpoints


@pytest.mark.negative
@pytest.mark.tc("TC-NEG-07")
@pytest.mark.parametrize(
    "method",
    [
        pytest.param(
            "POST",
            marks=pytest.mark.xfail(
                strict=True,
                raises=AssertionError,
                reason="Upstream: POST /weather returns 200 instead of 405",
            ),
        ),
        "PUT",
        "DELETE",
        "PATCH",
    ],
)
def test_current_weather_rejects_unsupported_method(api_client, method):
    response = api_client.send(method, endpoints.CURRENT_WEATHER, {"q": "London,GB"})

    assert response.status_code == 405
