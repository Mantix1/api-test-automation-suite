import pytest


@pytest.mark.boundary
@pytest.mark.tc("TC-BND-03")
@pytest.mark.parametrize(
    "q, expected_status, expected_message",
    [
        pytest.param("", 400, "Nothing to geocode", id="empty"),
        pytest.param(" ", 404, "city not found", id="whitespace"),
    ],
)
def test_current_weather_empty_city_query(api_client, q, expected_status, expected_message):
    response = api_client.get_current_weather(q=q)

    assert response.status_code == expected_status
    body = response.json()
    assert body["message"] == expected_message
    assert str(body["cod"]) == str(expected_status)


@pytest.mark.boundary
@pytest.mark.tc("TC-BND-04")
@pytest.mark.parametrize(
    "q, expected_name, expected_country",
    [
        pytest.param("São Paulo,BR", "São Paulo", "BR", id="latin_accent"),
        pytest.param("Москва,RU", "Moscow", "RU", id="cyrillic"),
        pytest.param("東京,JP", "Tokyo", "JP", id="cjk"),
    ],
)
def test_current_weather_unicode_city_query(api_client, q, expected_name, expected_country):
    response = api_client.get_current_weather(q=q)

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == expected_name
    assert body["sys"]["country"] == expected_country


@pytest.mark.boundary
@pytest.mark.tc("TC-BND-05")
@pytest.mark.parametrize(
    "q",
    [
        pytest.param("a" * 1000, id="1000_chars"),
        pytest.param("!@#$%^&*()", id="symbols"),
        pytest.param("<script>alert(1)</script>", id="html_tag"),
        pytest.param("' OR 1=1 --", id="sql_quote"),
    ],
)
def test_current_weather_long_or_special_city_query(api_client, q):
    response = api_client.get_current_weather(q=q)

    assert response.status_code == 404
    body = response.json()
    assert body["message"] == "city not found"
