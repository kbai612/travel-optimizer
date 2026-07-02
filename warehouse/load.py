"""Flattens bronze JSON into silver parquet, then registers it as DuckDB tables.

Run after the extractors: `python -m warehouse.load`
dbt's `raw` sources (see dbt/models/staging/sources.yml) read from the tables
this script creates in warehouse.duckdb.
"""

import json
from pathlib import Path

import duckdb
import pandas as pd

from extract.config import BRONZE_DIR, REPO_ROOT

SILVER_DIR = REPO_ROOT / "data" / "silver"
DB_PATH = REPO_ROOT / "warehouse.duckdb"


def _iter_bronze_files(source: str):
    source_dir = BRONZE_DIR / source
    if not source_dir.exists():
        return
    for iata_dir in sorted(source_dir.iterdir()):
        if not iata_dir.is_dir():
            continue
        for path in sorted(iata_dir.glob("*.json")):
            yield iata_dir.name, path


def flatten_weather() -> pd.DataFrame:
    rows = []
    for iata, path in _iter_bronze_files("open_meteo"):
        daily = json.loads(path.read_text())["daily"]
        for i in range(len(daily["time"])):
            rows.append(
                {
                    "iata": iata,
                    "date": daily["time"][i],
                    "temp_max_c": daily["temperature_2m_max"][i],
                    "temp_min_c": daily["temperature_2m_min"][i],
                    "temp_mean_c": daily["temperature_2m_mean"][i],
                    "precipitation_mm": daily["precipitation_sum"][i],
                    "precipitation_hours": daily["precipitation_hours"][i],
                    "windspeed_max_kmh": daily["windspeed_10m_max"][i],
                }
            )
    return pd.DataFrame(rows)


def flatten_holidays() -> pd.DataFrame:
    rows = []
    for iata, path in _iter_bronze_files("nager"):
        for h in json.loads(path.read_text()):
            rows.append(
                {
                    "iata": iata,
                    "date": h["date"],
                    "name": h.get("name"),
                    "local_name": h.get("localName"),
                    "country_code": h.get("countryCode"),
                    "is_global": h.get("global"),
                    "types": ",".join(h.get("types") or []),
                }
            )
    return pd.DataFrame(rows)


# Fixed schemas for the auth-gated sources so their raw/staging tables always exist —
# even with zero rows before OpenSky/Travelpayouts credentials are configured — which
# lets downstream marts LEFT JOIN against them unconditionally instead of branching on
# whether the data happens to be present.
FLIGHTS_SCHEMA = {
    "iata": "string",
    "window_start": "string",
    "window_end": "string",
    "arrivals": "Int64",
    "departures": "Int64",
}
PRICE_MONTHLY_SCHEMA = {
    "iata": "string",
    "origin": "string",
    "period": "string",
    "price": "Float64",
}


def _typed_frame(rows: list[dict], schema: dict[str, str]) -> pd.DataFrame:
    df = pd.DataFrame(rows, columns=list(schema.keys()))
    return df.astype(schema)


def flatten_flights() -> pd.DataFrame:
    """One row per (destination, sampled window) — see extract/opensky.py for the sampling scheme."""
    rows = []
    for iata, path in _iter_bronze_files("opensky"):
        window_start, window_end = path.stem.split("_")
        payload = json.loads(path.read_text())
        rows.append(
            {
                "iata": iata,
                "window_start": window_start,
                "window_end": window_end,
                "arrivals": len(payload.get("arrivals") or []),
                "departures": len(payload.get("departures") or []),
            }
        )
    return _typed_frame(rows, FLIGHTS_SCHEMA)


def flatten_price_monthly() -> pd.DataFrame:
    """One row per (destination, calendar month) — see extract/travelpayouts.py."""
    rows = []
    for iata, path in _iter_bronze_files("travelpayouts"):
        payload = json.loads(path.read_text())
        origin = payload.get("origin")
        for period, fare in (payload.get("monthly") or {}).items():
            rows.append(
                {
                    "iata": iata,
                    "origin": origin,
                    "period": period,
                    "price": (fare or {}).get("price"),
                }
            )
    return _typed_frame(rows, PRICE_MONTHLY_SCHEMA)


def write_silver(df: pd.DataFrame, source: str) -> Path:
    out_dir = SILVER_DIR / source
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{source}.parquet"
    df.to_parquet(out_path, index=False)
    return out_path


def load_duckdb(tables: dict[str, Path]) -> None:
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    for table_name, parquet_path in tables.items():
        con.execute(
            f"CREATE OR REPLACE TABLE raw.{table_name} AS "
            f"SELECT * FROM read_parquet('{parquet_path.as_posix()}')"
        )
    con.close()


def run() -> None:
    weather_df = flatten_weather()
    holidays_df = flatten_holidays()
    if weather_df.empty:
        raise SystemExit("No weather bronze data — run `python -m extract.run --source open_meteo` first.")
    if holidays_df.empty:
        raise SystemExit("No holiday bronze data — run `python -m extract.run --source nager` first.")

    flights_df = flatten_flights()
    price_df = flatten_price_monthly()

    tables = {
        "weather_daily": write_silver(weather_df, "open_meteo"),
        "holidays": write_silver(holidays_df, "nager"),
        "flights_sampled": write_silver(flights_df, "opensky"),
        "price_monthly": write_silver(price_df, "travelpayouts"),
    }
    load_duckdb(tables)
    print(
        f"Loaded {len(weather_df)} weather rows, {len(holidays_df)} holiday rows, "
        f"{len(flights_df)} flight-window rows, {len(price_df)} monthly-price rows into {DB_PATH}"
    )


if __name__ == "__main__":
    run()
