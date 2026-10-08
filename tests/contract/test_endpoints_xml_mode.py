import xml.etree.ElementTree as ET

import pytest


@pytest.mark.contract
@pytest.mark.tc("TC-CON-05")
@pytest.mark.parametrize(
    "helper, params, expected_status, expected_root",
    [
        pytest.param("get_current_weather", {"q": "London,GB"}, 200, "current", id="weather"),
        pytest.param("get_forecast", {"q": "Tokyo,JP", "cnt": 1}, 200, "weatherdata", id="forecast"),
        pytest.param("get_current_weather", {"q": "Zzqxwvy"}, 404, "Error", id="weather_error"),
    ],
)
def test_xml_mode_returns_xml(api_client, helper, params, expected_status, expected_root):
    response = getattr(api_client, helper)(mode="xml", **params)

    assert response.status_code == expected_status
    assert response.headers["Content-Type"].startswith("application/xml")
    root = ET.fromstring(response.content)
    assert root.tag == expected_root
