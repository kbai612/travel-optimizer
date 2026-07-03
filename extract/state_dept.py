"""Country-level travel-advisory levels via the US State Department API — keyless.

Unlike the other three extractors, this signal is per-country and static (not
per-month), so it's landed once per destination rather than as a time series.
The feed's `Title` field reads like "Portugal - Level 1: Exercise Normal
Precautions" -- there's no reliable ISO country code on each entry, so titles
are matched against our own destination country names.
"""

import json
import logging
import re

import httpx

from extract.client import get_json, new_client
from extract.config import Destination, bronze_path, load_destinations

logger = logging.getLogger(__name__)

ADVISORIES_URL = "https://cadataapi.state.gov/api/TravelAdvisories"

TITLE_RE = re.compile(r"^(?P<country>.+?)\s*-\s*Level\s*(?P<level>\d)\s*:", re.IGNORECASE)

# State Department advisory titles use plain country names, not ISO codes.
# Mapped only for the countries this pipeline currently tracks
# (config/destinations.yml) -- extend this if new destinations are added.
COUNTRY_NAME_TO_CODE = {
    "portugal": "PT",
    "japan": "JP",
    "united states": "US",
    "south africa": "ZA",
    "thailand": "TH",
    "australia": "AU",
    "iceland": "IS",
    "brazil": "BR",
    "france": "FR",
    "united kingdom": "GB",
    "italy": "IT",
    "spain": "ES",
    "netherlands": "NL",
    "turkey": "TR",
    "turkiye": "TR",
    "united arab emirates": "AE",
    "singapore": "SG",
    "indonesia": "ID",
    "hong kong": "HK",
    "mexico": "MX",
    "morocco": "MA",
    "argentina": "AR",
}


def fetch_advisories(client: httpx.Client) -> list[dict]:
    return get_json(client, ADVISORIES_URL) or []


def parse_advisory(entry: dict) -> tuple[str, int] | None:
    match = TITLE_RE.match(entry.get("Title") or "")
    if not match:
        return None
    country_code = COUNTRY_NAME_TO_CODE.get(match.group("country").strip().lower())
    if not country_code:
        return None
    return country_code, int(match.group("level"))


def run(destinations: list[Destination] | None = None) -> None:
    destinations = destinations or load_destinations()
    wanted_countries = {dest.country for dest in destinations}

    with new_client() as client:
        advisories = fetch_advisories(client)

    by_country: dict[str, dict] = {}
    for entry in advisories:
        parsed = parse_advisory(entry)
        if not parsed:
            continue
        country_code, level = parsed
        if country_code in wanted_countries:
            by_country[country_code] = {
                "country_code": country_code,
                "level": level,
                "updated": entry.get("Updated"),
            }

    for dest in destinations:
        record = by_country.get(dest.country)
        if not record:
            logger.warning("No travel advisory found for %s (%s)", dest.name, dest.country)
            continue
        out_path = bronze_path("state_dept", dest.iata, "advisory.json")
        out_path.write_text(json.dumps(record))
        print(f"[state_dept] {dest.name} ({dest.country}) -> Level {record['level']}")


if __name__ == "__main__":
    run()
