"""Public holidays via the Nager.Date API — keyless.

Pulls the last 3 years of public holidays per destination country so
downstream dbt models can compute holiday-proximity demand pressure by month.
Not every country is covered by Nager.Date; a missing country/year yields an
empty list rather than failing the whole run.
"""

import datetime as dt
import json
import logging

import httpx

from extract.client import ApiError, get_json, new_client
from extract.config import Destination, bronze_path, load_destinations

logger = logging.getLogger(__name__)

HOLIDAYS_URL = "https://date.nager.at/api/v3/PublicHolidays/{year}/{country}"


def holiday_years(today: dt.date | None = None) -> list[int]:
    today = today or dt.date.today()
    return [today.year - 2, today.year - 1, today.year]


def fetch_country_year(client: httpx.Client, country: str, year: int) -> list[dict]:
    url = HOLIDAYS_URL.format(year=year, country=country)
    try:
        return get_json(client, url) or []
    except ApiError as exc:
        logger.warning("No holiday data for %s %s: %s", country, year, exc)
        return []


def run(destinations: list[Destination] | None = None) -> None:
    destinations = destinations or load_destinations()
    years = holiday_years()
    with new_client() as client:
        for dest in destinations:
            holidays = []
            for year in years:
                holidays.extend(fetch_country_year(client, dest.country, year))
            out_path = bronze_path("nager", dest.iata, f"{years[0]}_{years[-1]}.json")
            out_path.write_text(json.dumps(holidays))
            print(f"[nager] {dest.name} ({dest.country}) -> {out_path} ({len(holidays)} holidays)")


if __name__ == "__main__":
    run()
