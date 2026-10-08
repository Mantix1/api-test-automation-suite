import pytest

from framework.api_client import OpenWeatherClient


@pytest.fixture(scope="session")
def api_client():
    client = OpenWeatherClient()
    yield client
    client.session.close()
