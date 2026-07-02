"""Historical daily weather via the Open-Meteo Archive API (ERA5) — keyless.

Pulls the last 3 complete calendar years per destination so downstream dbt
models can compute per-month climate normals (the weather comfort index).
"""

import datetime as dt
import json

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


def run(destinations: list[Destination] | None = None) -> None:
    destinations = destinations or load_destinations()
    start_year, end_year = climate_year_range()
    with new_client() as client:
        for dest in destinations:
            payload = fetch_destination(client, dest, start_year, end_year)
            out_path = bronze_path("open_meteo", dest.iata, f"{start_year}_{end_year}.json")
            out_path.write_text(json.dumps(payload))
            print(f"[open_meteo] {dest.name} ({dest.iata}) -> {out_path}")


if __name__ == "__main__":
    run()
