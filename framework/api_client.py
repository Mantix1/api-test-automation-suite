"""Thin wrapper around requests for the OpenWeatherMap API."""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from framework import config,endpoints


class OpenWeatherClient:
    def __init__(self, api_key: str = config.API_KEY):
        self.api_key = api_key
        self.session = requests.Session()
        retry = Retry(
            total =3,
            backoff_factor=1,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def get(self, url: str, params: dict | None = None, include_key: bool = True) -> requests.Response:
        params = dict(params or {})
        if include_key:
            params.setdefault("appid", self.api_key)
        return self.session.get(url, params=params, timeout=config.TIMEOUT_SECONDS)

    def get_current_weather(self, **params) -> requests.Response:
        return self.get(endpoints.CURRENT_WEATHER, params)

    def get_forecast(self, **params) -> requests.Response:
        return self.get(endpoints.FORECAST, params)

    def geocode_direct(self, **params) -> requests.Response:
        return self.get(endpoints.GEOCODING_DIRECT, params)

    def get_raw_query(self, url: str, raw_query: str) -> requests.Response:
        """Send a GET with raw_query appended exactly as given, without re-encoding."""
        request = requests.Request("GET", url, params={"appid": self.api_key})
        prepared = self.session.prepare_request(request)
        prepared.url = f"{prepared.url}&{raw_query}"
        return self.session.send(prepared, timeout=config.TIMEOUT_SECONDS)
    