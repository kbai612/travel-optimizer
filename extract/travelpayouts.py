"""Fare-seasonality via the Travelpayouts Data API — free (affiliate-network signup,
no card, no MAU minimum on this endpoint).

Register at https://www.travelpayouts.com/programs/100/tools/api and set
TRAVELPAYOUTS_TOKEN (env or .env). The "cheapest tickets grouped by month" endpoint
returns one representative cheapest fare per calendar month for a given
origin/destination pair — a cached/historical fare, not a live quote.

Replaces Amadeus's Flight Cheapest Date Search, which is gone: Amadeus decommissioned
its entire self-service portal (including existing free keys) on 2026-07-17.
"""

import json
import logging
import os

import httpx

from extract.client import ApiError, get_json, new_client
from extract.config import Destination, bronze_path, load_destinations

logger = logging.getLogger(__name__)

MONTHLY_PRICES_URL = "https://api.travelpayouts.com/v1/prices/monthly"

HOME_AIRPORT_IATA = os.environ.get("HOME_AIRPORT_IATA", "JFK")


def _token() -> str:
    token = os.environ.get("TRAVELPAYOUTS_TOKEN")
    if not token:
        raise SystemExit(
            "Missing TRAVELPAYOUTS_TOKEN. Register a free account at "
            "https://www.travelpayouts.com/programs/100/tools/api and set it in your .env file."
        )
    return token


def fetch_monthly_prices(client: httpx.Client, origin: str, destination: str) -> dict:
    params = {"currency": "USD", "origin": origin, "destination": destination, "token": _token()}
    try:
        payload = get_json(client, MONTHLY_PRICES_URL, params=params) or {}
    except ApiError as exc:
        logger.warning("Travelpayouts monthly prices failed for %s->%s: %s", origin, destination, exc)
        return {}
    return payload.get("data", {}) if payload.get("success") else {}


def run(destinations: list[Destination] | None = None) -> None:
    destinations = destinations or load_destinations()
    with new_client() as client:
        for dest in destinations:
            if dest.iata == HOME_AIRPORT_IATA:
                # A destination that IS the configured home airport has no meaningful
                # fare to search for — skip the doomed API call rather than round-trip
                # a guaranteed 400 (Travelpayouts rejects origin == destination).
                monthly = {}
                print(f"[travelpayouts] {dest.name} ({dest.iata}) skipped: same as HOME_AIRPORT_IATA")
            else:
                monthly = fetch_monthly_prices(client, HOME_AIRPORT_IATA, dest.iata)
            out_path = bronze_path("travelpayouts", dest.iata, "monthly_prices.json")
            out_path.write_text(json.dumps({"origin": HOME_AIRPORT_IATA, "monthly": monthly}))
            if dest.iata != HOME_AIRPORT_IATA:
                print(f"[travelpayouts] {dest.name} ({dest.iata}) -> {out_path} ({len(monthly)} months)")


if __name__ == "__main__":
    run()
