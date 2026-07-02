# Travel Optimizer

**When is the best time to travel to a given destination?** This pipeline blends
real weather history, flight/demand activity, fare seasonality, and public-holiday
pressure into a single 0–100 "travel score" per destination, per calendar month —
and a short list of recommended months with the reasoning behind them.

Everything runs at zero cost: local Python extractors, a local DuckDB warehouse,
dbt for transformation and testing, GitHub Actions for scheduling, and a Streamlit
dashboard for the output. See `docs/INSIGHTS.md` for current findings.

## Architecture

```
  extract/ (Python)              DuckDB warehouse (medallion)
  ├─ open_meteo.py    ─┐         raw.*    landed bronze -> flattened silver
  ├─ nager.py           ├──►     stg_*    typed, cleaned            ──►  dbt
  ├─ opensky.py         │        int_*    per-(destination, month)  models
  └─ travelpayouts.py  ─┘                 sub-scores
                                  fct_travel_score / dim_destination (marts)
                                              │
  GitHub Actions (cron)  ──────────────────► Streamlit dashboard (dashboard/app.py)
                                              docs/INSIGHTS.md
```

- **Ingestion** (`extract/`) — one module per API, each landing raw JSON to
  `data/bronze/<source>/<iata>/`. Shared retry/backoff + 429 handling lives in
  `extract/client.py`.
- **Warehouse** (`warehouse/load.py`) — flattens bronze JSON into typed silver
  parquet, then loads it into `warehouse.duckdb` (`raw` schema).
- **Transform** (`dbt/`) — `staging` (typed 1:1 views over `raw`) →
  `intermediate` (per-destination, per-month sub-scores) → `marts`
  (`fct_travel_score`, `dim_destination`), with dbt tests at every layer.
- **Orchestration** (`.github/workflows/`) — `pipeline.yml` runs the full
  extract → load → dbt build chain on a daily cron (and manually via
  `workflow_dispatch`); `ci.yml` lints and runs a credential-free smoke test of
  the whole DAG on every PR.
- **Serving** (`dashboard/app.py`) — Streamlit: pick a destination, see the
  score by month, the sub-score breakdown, and a plain-language recommendation.

## Data sources

| Signal | Source | Auth |
|---|---|---|
| Weather (3yr daily history) | [Open-Meteo](https://open-meteo.com/) Archive API | none |
| Public holidays | [Nager.Date](https://date.nager.at/) | none |
| Flight arrival/departure activity (demand) | [OpenSky Network](https://opensky-network.org/) | free account |
| Fare seasonality (price) | [Travelpayouts Data API](https://www.travelpayouts.com/programs/100/tools/api) | free account |

Amadeus Self-Service originally supplied the demand + price signals but is not an
option: Amadeus decommissioned the entire self-service portal, including existing
free keys, on 2026-07-17.

## Setup

Requires [uv](https://docs.astral.sh/uv/) (installs Python + deps, no system
Python needed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync
```

Open-Meteo and Nager.Date need no credentials. To pull flight and price data too,
copy `.env.example` to `.env` and fill in free OpenSky + Travelpayouts credentials
(see comments in that file for where to register).

## Running the pipeline

```bash
# 1. Extract (add --dest LIS HND ... to scope to specific airports)
uv run python -m extract.run --all
# or, without OpenSky/Travelpayouts credentials: --source open_meteo nager

# 2. Flatten bronze -> silver parquet -> warehouse.duckdb
uv run python -m warehouse.load

# 3. Build + test the dbt models
cd dbt && uv run dbt build --profiles-dir . && cd ..

# 4. Explore the results
uv run streamlit run dashboard/app.py
```

The OpenSky/Travelpayouts raw tables always exist (even empty) once step 2 has run
at least once, so `dbt build` and the dashboard work with just the keyless sources —
the demand and price sub-scores default to a neutral 50 until credentials are
added, and pick up real data automatically on the next pipeline run with no code
changes.

## Score methodology

Each destination gets one row per calendar month in `fct_travel_score`, blending
four 0–100 sub-scores (weights are dbt vars in `dbt/dbt_project.yml`, defaulting
to weather 0.35 / demand 0.25 / price 0.20 / holiday 0.20):

- **Weather comfort** (`int_weather_comfort`) — climate normals from 3 years of
  Open-Meteo daily history, scored against a ~21°C ideal with penalties for rain
  and wind.
- **Demand** (`int_demand_index`, inverted) — OpenSky's relative flight-volume
  index for that destination; a below-average-traffic month scores higher.
- **Price** (`int_price_index`, inverted) — Travelpayouts cheapest-fare-by-month,
  indexed against that destination's own average month.
- **Holiday pressure** (`int_holiday_pressure`, inverted) — density of public
  holidays in the destination's country that month.

## Known limitations

- **Travelpayouts prices are cached/historical fares**, not live quotes — a real
  fare-search API (e.g. a paid Amadeus Enterprise key, or Google Flights via
  SerpApi) would give more current pricing, at a cost.
- **OpenSky sampling** — the API only accepts windows spanning 2 day partitions
  (a documented-elsewhere 7-day window is rejected), so `extract/opensky.py`
  samples one representative 2-day window per calendar month instead of every day.
- **Nager.Date country coverage** is not universal (e.g. Thailand returns zero
  holidays) — that destination's holiday-pressure score is neutral by design
  rather than wrong.
- The weather comfort formula is a simple, documented heuristic (`int_weather_comfort.sql`),
  not a validated tourism-comfort index — it's tunable but worth treating as a
  starting point.

## Repo layout

```
config/destinations.yml   destinations tracked by the pipeline
extract/                  one module per API source + shared HTTP client
warehouse/load.py         bronze JSON -> silver parquet -> DuckDB
dbt/                      staging -> intermediate -> marts, seeds, tests
dashboard/app.py          Streamlit UI
docs/INSIGHTS.md          current findings
.github/workflows/        pipeline.yml (cron) + ci.yml (PR lint + smoke test)
```
