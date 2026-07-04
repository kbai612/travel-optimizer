"""Fare-seasonality via the Travelpayouts Data API — free (affiliate-network signup,
no card, no MAU minimum on these endpoints).

Register at https://www.travelpayouts.com/programs/100/tools/api and set
TRAVELPAYOUTS_TOKEN (env or .env). Two endpoints are pulled per destination:

- "cheapest tickets grouped by month" (/v1/prices/monthly): one representative cheapest
  fare per calendar month for a given origin/destination pair.
- "calendar of prices" (/v1/prices/calendar): the cheapest fare for each *day* of a given
  month — finer-grained than the monthly endpoint.

Both return cached/historical fares (not live quotes). Each run writes a date-stamped
snapshot rather than overwriting, so re-running over time accumulates a growing price
history that downstream averaging makes progressively more accurate.

Replaces Amadeus's Flight Cheapest Date Search, which is gone: Amadeus decommissioned
its entire self-service portal (including existing free keys) on 2026-07-17.
"""

import json
import logging
import os
from datetime import date

import httpx

from extract.client import ApiError, get_json, new_client
from extract.config import Destination, bronze_path, load_destinations

logger = logging.getLogger(__name__)

MONTHLY_PRICES_URL = "https://api.travelpayouts.com/v1/prices/monthly"
CALENDAR_PRICES_URL = "https://api.travelpayouts.com/v1/prices/calendar"

HOME_AIRPORT_IATA = os.environ.get("HOME_AIRPORT_IATA", "JFK")

# How many months of day-level calendar data to pull per destination each run (current
# month + the next N-1). Six months balances near-term coverage against API volume
# (N months x number of destinations calls per run).
CALENDAR_MONTHS = 6


def _token() -> str:
    token = os.environ.get("TRAVELPAYOUTS_TOKEN")
    if not token:
        raise SystemExit(
            "Missing TRAVELPAYOUTS_TOKEN. Register a free account at "
            "https://www.travelpayouts.com/programs/100/tools/api and set it in your .env file."
        )
    return token


def _upcoming_months(n: int = CALENDAR_MONTHS, today: date | None = None) -> list[str]:
    """The current month plus the next n-1, as ascending 'YYYY-MM' strings."""
    today = today or date.today()
    months = []
    year, month = today.year, today.month
    for _ in range(n):
        months.append(f"{year:04d}-{month:02d}")
        month += 1
        if month > 12:
            month = 1
            year += 1
    return months


def fetch_monthly_prices(client: httpx.Client, origin: str, destination: str) -> dict:
    params = {"currency": "USD", "origin": origin, "destination": destination, "token": _token()}
    try:
        payload = get_json(client, MONTHLY_PRICES_URL, params=params) or {}
    except ApiError as exc:
        logger.warning("Travelpayouts monthly prices failed for %s->%s: %s", origin, destination, exc)
        return {}
    return payload.get("data", {}) if payload.get("success") else {}


def fetch_price_calendar(client: httpx.Client, origin: str, destination: str, month: str) -> dict:
    """Cheapest fare per day for `month` ('YYYY-MM'), keyed by 'YYYY-MM-DD' date string."""
    params = {
        "currency": "USD",
        "origin": origin,
        "destination": destination,
        "depart_date": month,
        "calendar_type": "departure_date",
        "token": _token(),
    }
    try:
        payload = get_json(client, CALENDAR_PRICES_URL, params=params) or {}
    except ApiError as exc:
        logger.warning(
            "Travelpayouts calendar failed for %s->%s %s: %s", origin, destination, month, exc
        )
        return {}
    return payload.get("data", {}) if payload.get("success") else {}


def run(destinations: list[Destination] | None = None) -> None:
    destinations = destinations or load_destinations()
    collected_at = date.today().isoformat()
    months = _upcoming_months()
    with new_client() as client:
        for dest in destinations:
            same_as_home = dest.iata == HOME_AIRPORT_IATA
            if same_as_home:
                # A destination that IS the configured home airport has no meaningful
                # fare to search for — skip the doomed API calls rather than round-trip
                # a guaranteed 400 (Travelpayouts rejects origin == destination).
                monthly: dict = {}
                days: dict = {}
                print(f"[travelpayouts] {dest.name} ({dest.iata}) skipped: same as HOME_AIRPORT_IATA")
            else:
                monthly = fetch_monthly_prices(client, HOME_AIRPORT_IATA, dest.iata)
                days = {}
                for month in months:
                    for day, fare in fetch_price_calendar(
                        client, HOME_AIRPORT_IATA, dest.iata, month
                    ).items():
                        price = (fare or {}).get("price")
                        if price is not None:
                            days[day] = price

            monthly_path = bronze_path("travelpayouts", dest.iata, f"monthly_prices_{collected_at}.json")
            monthly_path.write_text(
                json.dumps({"origin": HOME_AIRPORT_IATA, "collected_at": collected_at, "monthly": monthly})
            )
            calendar_path = bronze_path(
                "travelpayouts_calendar", dest.iata, f"calendar_{collected_at}.json"
            )
            calendar_path.write_text(
                json.dumps({"origin": HOME_AIRPORT_IATA, "collected_at": collected_at, "days": days})
            )
            if not same_as_home:
                print(
                    f"[travelpayouts] {dest.name} ({dest.iata}) -> "
                    f"{len(monthly)} months, {len(days)} daily fares"
                )


if __name__ == "__main__":
    run()
