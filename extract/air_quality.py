"""Historical hourly PM2.5 via the Open-Meteo Air Quality API (CAMS) — keyless.

Pulls the same 3 complete calendar years as extract/open_meteo.py so downstream
dbt models can compute per-month air-quality normals. CAMS global reanalysis
only covers August 2022 onwards, but that's already within our climate window.
"""

import json
import time

import httpx

from extract.client import get_json, new_client
from extract.config import Destination, bronze_path, load_destinations
from extract.open_meteo import REQUEST_SPACING_SECONDS, climate_year_range

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

HOURLY_VARS = ["pm2_5"]


def fetch_destination(
    client: httpx.Client, dest: Destination, start_year: int, end_year: int
) -> dict:
    params = {
        "latitude": dest.lat,
        "longitude": dest.lon,
        "start_date": f"{start_year}-01-01",
        "end_date": f"{end_year}-12-31",
        "hourly": ",".join(HOURLY_VARS),
        "timezone": "auto",
    }
    return get_json(client, AIR_QUALITY_URL, params=params)


def run(destinations: list[Destination] | None = None) -> None:
    destinations = destinations or load_destinations()
    start_year, end_year = climate_year_range()
    with new_client() as client:
        for i, dest in enumerate(destinations):
            if i:
                time.sleep(REQUEST_SPACING_SECONDS)  # shared Open-Meteo minute-limit; see open_meteo.py
            payload = fetch_destination(client, dest, start_year, end_year)
            out_path = bronze_path("air_quality", dest.iata, f"{start_year}_{end_year}.json")
            out_path.write_text(json.dumps(payload))
            print(f"[air_quality] {dest.name} ({dest.iata}) -> {out_path}")


if __name__ == "__main__":
    run()
