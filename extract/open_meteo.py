"""Historical daily weather via the Open-Meteo Archive API (ERA5) — keyless.

Pulls the last 3 complete calendar years per destination so downstream dbt
models can compute per-month climate normals (the weather comfort index).
"""

import datetime as dt
import json
import time

import httpx

from extract.client import get_json, new_client
from extract.config import Destination, bronze_path, load_destinations

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "precipitation_hours",
    "windspeed_10m_max",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "sunshine_duration",
]


def climate_year_range(today: dt.date | None = None) -> tuple[int, int]:
    """Last 3 complete calendar years, e.g. a run in mid-2026 covers (2023, 2025)."""
    today = today or dt.date.today()
    end_year = today.year - 1
    return end_year - 2, end_year


def fetch_destination(
    client: httpx.Client, dest: Destination, start_year: int, end_year: int
) -> dict:
    params = {
        "latitude": dest.lat,
        "longitude": dest.lon,
        "start_date": f"{start_year}-01-01",
        "end_date": f"{end_year}-12-31",
        "daily": ",".join(DAILY_VARS),
        "timezone": "auto",
    }
    return get_json(client, ARCHIVE_URL, params=params)


# All three Open-Meteo extractors (weather, air_quality, marine) share one per-IP
# minute-rate limit. Each archive request is heavy (3 years of daily/hourly data),
# and a burst of ~9 trips the limit with a "Minutely API request limit exceeded"
# 429 whose 60s reset outlasts the shared client's backoff — so a fresh full run
# across many destinations would crash mid-source. This proactive per-destination
# spacing keeps a full run comfortably under that ceiling. Imported by
# air_quality.py and marine.py so the three sources pace identically.
REQUEST_SPACING_SECONDS = 8


def run(destinations: list[Destination] | None = None) -> None:
    destinations = destinations or load_destinations()
    start_year, end_year = climate_year_range()
    with new_client() as client:
        for i, dest in enumerate(destinations):
            if i:
                time.sleep(REQUEST_SPACING_SECONDS)
            payload = fetch_destination(client, dest, start_year, end_year)
            out_path = bronze_path("open_meteo", dest.iata, f"{start_year}_{end_year}.json")
            out_path.write_text(json.dumps(payload))
            print(f"[open_meteo] {dest.name} ({dest.iata}) -> {out_path}")


if __name__ == "__main__":
    run()
