"""Historical hourly sea-surface temperature via the Open-Meteo Marine API — keyless.

Pulls the same 3 complete calendar years as extract/open_meteo.py so downstream
dbt models can compute per-month swim-comfort normals. Some destinations sit far
enough from open water that the API has no sea grid cell nearby; that destination
is skipped (its bronze file is simply never written) and int_sea_temperature.sql
has no rows for it, so fct_travel_score falls back to a neutral score rather than
failing the whole run.
"""

import json
import logging
import time

import httpx

from extract.client import ApiError, get_json, new_client
from extract.config import Destination, bronze_path, load_destinations
from extract.open_meteo import REQUEST_SPACING_SECONDS, climate_year_range

logger = logging.getLogger(__name__)

MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"

HOURLY_VARS = ["sea_surface_temperature"]


def fetch_destination(
    client: httpx.Client, dest: Destination, start_year: int, end_year: int
) -> dict:
    params = {
        "latitude": dest.lat,
        "longitude": dest.lon,
        "start_date": f"{start_year}-01-01",
        "end_date": f"{end_year}-12-31",
        "hourly": ",".join(HOURLY_VARS),
        "cell_selection": "sea",
        "timezone": "auto",
    }
    return get_json(client, MARINE_URL, params=params)


def run(destinations: list[Destination] | None = None) -> None:
    destinations = destinations or load_destinations()
    start_year, end_year = climate_year_range()
    with new_client() as client:
        for i, dest in enumerate(destinations):
            if i:
                time.sleep(REQUEST_SPACING_SECONDS)  # shared Open-Meteo minute-limit; see open_meteo.py
            try:
                payload = fetch_destination(client, dest, start_year, end_year)
            except ApiError as exc:
                logger.warning("No sea grid cell near %s (%s): %s", dest.name, dest.iata, exc)
                print(f"[marine] {dest.name} ({dest.iata}) -> skipped, no nearby sea data")
                continue
            out_path = bronze_path("marine", dest.iata, f"{start_year}_{end_year}.json")
            out_path.write_text(json.dumps(payload))
            print(f"[marine] {dest.name} ({dest.iata}) -> {out_path}")


if __name__ == "__main__":
    run()
