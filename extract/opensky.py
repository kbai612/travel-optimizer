"""Flight arrival/departure activity via the OpenSky Network REST API.

Requires a free OpenSky account (https://opensky-network.org) — register,
create an API client under your account, and set OPENSKY_CLIENT_ID /
OPENSKY_CLIENT_SECRET (env or .env). Uses OAuth2 client-credentials auth.

OpenSky's arrival/departure endpoint only accepts windows spanning at most 2 day
partitions (~2 days; a 7-day window, despite matching some documentation, is
rejected with "You can only query across 2 partitions"). Rather than pulling a
full year of daily counts, this samples one representative 2-day window per
calendar month over the trailing 12 months (2 requests per month per
destination: arrivals + departures) — enough to rank "busier" vs "quieter"
months per airport without exhausting the free quota.
"""

import datetime as dt
import json
import logging
import os
import time

import httpx

from extract.client import ApiError, get_json, new_client, post_json
from extract.config import Destination, bronze_path, load_destinations

logger = logging.getLogger(__name__)

TOKEN_URL = (
    "https://auth.opensky-network.org/auth/realms/opensky-network"
    "/protocol/openid-connect/token"
)
ARRIVAL_URL = "https://opensky-network.org/api/flights/arrival"
DEPARTURE_URL = "https://opensky-network.org/api/flights/departure"


def _credentials() -> tuple[str, str]:
    client_id = os.environ.get("OPENSKY_CLIENT_ID")
    client_secret = os.environ.get("OPENSKY_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise SystemExit(
            "Missing OPENSKY_CLIENT_ID / OPENSKY_CLIENT_SECRET. "
            "Register a free account at https://opensky-network.org, create an API "
            "client under Account > API Client, and set both in your .env file."
        )
    return client_id, client_secret


def fetch_token(client: httpx.Client) -> str:
    client_id, client_secret = _credentials()
    payload = post_json(
        client,
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        },
    )
    return payload["access_token"]


def monthly_sample_windows(today: dt.date | None = None) -> list[tuple[dt.date, dt.date]]:
    """One representative 2-day window per calendar month over the trailing 12 months."""
    today = today or dt.date.today()
    windows = []
    for months_back in range(12, 0, -1):
        year, month = today.year, today.month - months_back
        while month <= 0:
            month += 12
            year -= 1
        start = dt.date(year, month, 8)  # 2nd week of the month; avoids month-boundary edge cases
        end = start + dt.timedelta(days=2)
        windows.append((start, end))
    return windows


def fetch_window(client: httpx.Client, token: str, icao: str, start: dt.date, end: dt.date) -> dict:
    headers = {"Authorization": f"Bearer {token}"}
    begin_ts = int(dt.datetime.combine(start, dt.time.min, tzinfo=dt.timezone.utc).timestamp())
    end_ts = int(dt.datetime.combine(end, dt.time.min, tzinfo=dt.timezone.utc).timestamp())
    params = {"airport": icao, "begin": begin_ts, "end": end_ts}

    payload = {"arrivals": [], "departures": []}
    for direction, url in (("arrivals", ARRIVAL_URL), ("departures", DEPARTURE_URL)):
        try:
            payload[direction] = get_json(client, url, params=params, headers=headers) or []
        except ApiError as exc:
            logger.warning("OpenSky %s failed for %s %s-%s: %s", direction, icao, start, end, exc)
        time.sleep(1)  # proactive pacing — the free tier rate-limits well under 1 req/sec
    return payload


def run(destinations: list[Destination] | None = None) -> None:
    destinations = destinations or load_destinations()
    windows = monthly_sample_windows()
    with new_client() as client:
        for dest in destinations:
            token = fetch_token(client)  # refresh per destination; token TTL is ~30 min
            for start, end in windows:
                payload = fetch_window(client, token, dest.icao, start, end)
                out_path = bronze_path(
                    "opensky", dest.iata, f"{start.isoformat()}_{end.isoformat()}.json"
                )
                out_path.write_text(json.dumps(payload))
                time.sleep(1)  # proactive pacing between sample windows
            print(f"[opensky] {dest.name} ({dest.icao}) -> {len(windows)} monthly sample windows landed")


if __name__ == "__main__":
    run()
