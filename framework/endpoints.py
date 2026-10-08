"""Full URLs for every endpoint under test. The only place paths are defined."""
from framework import config

CURRENT_WEATHER = f"{config.BASE_URL}/weather"
FORECAST = f"{config.BASE_URL}/forecast"
GEOCODING_DIRECT = f"{config.GEO_BASE_URL}/direct"
