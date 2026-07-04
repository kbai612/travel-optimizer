# Travel Optimizer

**When is the best time to travel to a given destination?** This pipeline blends
real weather history, flight/demand activity, fare seasonality, public-holiday
pressure, air quality, and sea temperature into a single 0–100 "travel score" per
destination, per calendar month — adjusted for the destination country's travel
advisory level — and a short list of recommended months with the reasoning
behind them.

Everything runs at zero cost: local Python extractors, a local DuckDB warehouse,
dbt for transformation and testing, GitHub Actions for scheduling, and a Streamlit
dashboard for the output. See `docs/INSIGHTS.md` for current findings.

**🌐 Live demo:** _<!-- paste your Streamlit Community Cloud URL here after deploying (see "Deploy the dashboard" below) -->_ — the hosted app runs off a small committed data snapshot, so it works with no backend. Explore it in two modes: **When should I go?** (per destination) and **Where should I go?** (rank destinations for a month + your constraints).

## Architecture

```
  extract/ (Python)              DuckDB warehouse (medallion)
  ├─ open_meteo.py   ─┐          raw.*    landed bronze -> flattened silver
  ├─ nager.py          │         stg_*    typed, cleaned            ──►  dbt
  ├─ opensky.py        │         int_*    per-(destination, month)  models
  ├─ travelpayouts.py  ├──►               sub-scores
  ├─ air_quality.py    │         dim_destination -- advisory_score (per-country)
  ├─ marine.py         │                    │
  └─ state_dept.py    ─┘         fct_travel_score = blended sub-scores x advisory (marts)
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
  Travel advisory is per-country rather than per-month, so it lives on
  `dim_destination` and is applied as a multiplier in `fct_travel_score`.
- **Orchestration** (`.github/workflows/`) — `pipeline.yml` runs the full
  extract → load → dbt build chain on a daily cron (and manually via
  `workflow_dispatch`); `ci.yml` lints and runs a credential-free smoke test of
  the whole DAG on every PR. Because each run starts from a clean checkout with an
  empty `data/`, the daily job restores the Travelpayouts price snapshots from a GCS
  bucket before extracting and pushes them back after, so the accumulated fare history
  survives between runs (every other source regenerates its full history each run and
  needs no persistence). Set repo **variable** `GCS_BRONZE_BUCKET` (bucket name) and
  **secret** `GCP_SA_KEY` (service-account JSON with object read/write on that bucket)
  to enable it; leave `GCS_BRONZE_BUCKET` unset and the persistence steps no-op.
- **Serving** (`dashboard/app.py`) — Streamlit, two modes: **"When should I go?"**
  (pick a destination, see the score by month, sub-score breakdown, and a
  plain-language recommendation) and **"Where should I go?"** (fix a month plus
  constraints — budget, swim-friendly seas, max advisory level — and rank every
  destination head-to-head).

## Data sources

| Signal | Source | Auth |
|---|---|---|
| Weather (3yr daily history) | [Open-Meteo](https://open-meteo.com/) Archive API | none |
| Public holidays | [Nager.Date](https://date.nager.at/) | none |
| Flight arrival/departure activity (demand) | [OpenSky Network](https://opensky-network.org/) | free account |
| Fare seasonality (price) | [Travelpayouts Data API](https://www.travelpayouts.com/programs/100/tools/api) — monthly + day-level calendar, accumulated across runs | free account |
| Air quality (PM2.5, 3yr hourly history) | [Open-Meteo Air Quality API](https://open-meteo.com/en/docs/air-quality-api) | none |
| Sea-surface temperature (3yr hourly history) | [Open-Meteo Marine API](https://open-meteo.com/en/docs/marine-weather-api) | none |
| Travel advisory level (per country) | [US State Dept Travel Advisories](https://cadataapi.state.gov/api/TravelAdvisories) | none |

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

Open-Meteo (weather, air quality, marine), Nager.Date, and the State Department
advisory feed need no credentials. To pull flight and price data too, copy
`.env.example` to `.env` and fill in free OpenSky + Travelpayouts credentials
(see comments in that file for where to register). Keep `HOME_AIRPORT_IATA`
stable if you want one continuous fare history: if you change origins later,
the old snapshots stay on disk but the price index only uses the latest
origin's snapshots so different departure airports never get mixed.

## Running the pipeline

```bash
# 1. Extract (add --dest LIS HND ... to scope to specific airports)
uv run python -m extract.run --all
# or, without OpenSky/Travelpayouts credentials:
# --source open_meteo nager air_quality marine state_dept

# 2. Flatten bronze -> silver parquet -> warehouse.duckdb
uv run python -m warehouse.load

# 3. Build + test the dbt models
cd dbt && uv run dbt build --profiles-dir . && cd ..

# 4. Regenerate docs/INSIGHTS.md from the fresh mart (incl. score validation)
uv run python -m report.insights

# 5. Explore the results
uv run streamlit run dashboard/app.py
```

The OpenSky/Travelpayouts raw tables always exist (even empty) once step 2 has run
at least once, so `dbt build` and the dashboard work with just the keyless sources —
the demand and price sub-scores default to a neutral 50 until credentials are
added, and pick up real data automatically on the next pipeline run with no code
changes.

## Deploy the dashboard

The dashboard reads a live `warehouse.duckdb` when one is present, and otherwise
falls back to `dashboard/snapshot/fct_travel_score.parquet` — a small,
committed export of the mart. That snapshot is what makes a **zero-backend
hosted demo** possible: neither the warehouse nor the bronze/silver data is in git,
but the snapshot is, so a fresh clone (or a cloud host) has something to show.

To publish it for free on [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push this repo to GitHub.
2. At [share.streamlit.io](https://share.streamlit.io), create an app pointing at
   `dashboard/app.py` on your default branch.
3. Deploy — no secrets required. The app loads the committed snapshot and the
   theme in `.streamlit/config.toml`.
4. Paste the resulting URL into the **Live demo** line near the top of this README.

The snapshot is regenerated and committed back on every daily pipeline run (see
`report/insights.py` and `.github/workflows/pipeline.yml`), so the hosted demo
tracks the latest data without any manual step. Refresh it locally any time with
`uv run python -m report.insights`.

## Score methodology

Each destination gets one row per calendar month in `fct_travel_score`, blending
six 0–100 sub-scores (weights are dbt vars in `dbt/dbt_project.yml`, defaulting
to weather 0.25 / demand 0.20 / price 0.18 / holiday 0.12 / air quality 0.15 /
sea temperature 0.10 — these six must sum to 1.0):

- **Weather comfort** (`int_weather_comfort`) — climate normals from 3 years of
  Open-Meteo daily history, scored against a ~22°C *feels-like* (apparent
  temperature) ideal, with penalties for rain and wind and credit for sunshine
  hours. Apparent temperature already folds in humidity and wind, so a humid
  35°C day and a dry 35°C day no longer score the same.
- **Demand** (`int_demand_index`, inverted) — OpenSky's relative flight-volume
  index for that destination; a below-average-traffic month scores higher.
- **Price** (`int_price_index`, inverted) — Travelpayouts fares indexed against that
  destination's own average month. Prefers the day-level calendar endpoint (averaged to
  a monthly figure) where available and falls back to the cheapest-fare-by-month endpoint.
  Both sources are date-stamped and accumulated across runs, so the index grows more
  accurate the longer the pipeline runs. Same-day re-runs naturally overwrite that
  day's snapshot file; later days add new history.
- **Holiday pressure** (`int_holiday_pressure`, inverted) — density of public
  holidays in the destination's country that month.
- **Air quality** (`int_air_quality`, inverted) — monthly average PM2.5 from
  Open-Meteo's Air Quality API, scored against the WHO annual guideline.
- **Sea temperature** (`int_sea_temperature`) — monthly average sea-surface
  temperature from Open-Meteo's Marine API, scored against a ~26°C
  swim-comfort ideal. Neutral (50) for destinations with no nearby sea grid
  cell (e.g. landlocked airports).

The blended monthly score is then **multiplied** by a country-level safety
adjustment (`dim_destination.advisory_score`) derived from the US State
Department's travel advisory level for that destination's country — Level 1
applies no adjustment, Level 4 heavily discounts every month's score. This is
a multiplier rather than a seventh additive weight because advisory level is
static per country, not seasonal.

### Is the score any good?

Because the score is a heuristic blend, it's validated against an *external*
reference the model never sees: the conventionally-recommended time to visit each
destination (`report/reference.py`). `report/validation.py` checks whether the
model's monthly scores line up with that consensus, and `docs/INSIGHTS.md`
reports the result each build — currently the recommended months out-score the
rest of the year for 6/8 destinations, and the peak month lands within a month of
the recommended window for all 8. The two directional misses (Tokyo, Lisbon) map
to documented formula behavior rather than random error — see below.

## Known limitations

- **Travelpayouts prices are cached/historical fares**, not live quotes — a real
  fare-search API (e.g. a paid Amadeus Enterprise key, or Google Flights via
  SerpApi) would give more current pricing, at a cost. Accumulating date-stamped
  snapshots mitigates this: each run adds observations rather than overwriting, so the
  price index converges on a fuller picture over time.
- **OpenSky sampling** — the API only accepts windows spanning 2 day partitions
  (a documented-elsewhere 7-day window is rejected), so `extract/opensky.py`
  samples one representative 2-day window per calendar month instead of every day.
- **OpenSky's free-tier daily quota is tight** — observed exhaustion after ~4
  destinations' worth of requests in one run, and it's a daily cap, not a burst
  limit (pacing requests doesn't help once it's hit). `extract/opensky.py` is
  idempotent (a window already in `data/bronze/opensky/` is skipped) and stops
  the whole run immediately on the first confirmed 429 rather than retrying
  through every remaining destination. In practice this means: a single `--all`
  run won't get full coverage in one day, but repeated runs (e.g. the daily cron)
  converge on it — each run picks up only what's still missing.
- **Nager.Date country coverage** is not universal (e.g. Thailand returns zero
  holidays) — that destination's holiday-pressure score is neutral by design
  rather than wrong.
- The weather comfort formula is a simple, documented heuristic (`int_weather_comfort.sql`),
  not a validated tourism-comfort index — it's tunable but worth treating as a
  starting point.
- **Air quality history is shorter than the other signals** — Open-Meteo's CAMS
  global reanalysis only goes back to August 2022, though that's already within
  the pipeline's 3-complete-year window, so no destination should be short on data.
- **Sea temperature has no data for destinations without a nearby sea grid
  cell** (`extract/marine.py` skips the destination and logs a warning rather
  than failing the run) — `sea_temp_score` defaults to neutral (50) there,
  same as any other missing signal.
- **Travel advisory matching is name-based, not code-based** — the State
  Department feed doesn't publish a reliable ISO country code per entry, so
  `extract/state_dept.py` matches on the country name parsed from the advisory
  title against a small fixed dictionary (`COUNTRY_NAME_TO_CODE`) covering only
  the countries in `config/destinations.yml`. Adding a destination in a new
  country requires adding its name to that dictionary too.
- **Travel advisory coverage isn't universal either** — the State Department
  doesn't publish a self-advisory for the US (so `New York` always gets the
  neutral default, which is correct, not a gap), and at last check the feed
  simply had no entry for Brazil (so `Rio de Janeiro` falls back to neutral
  too, same treatment as any other missing signal).

## Repo layout

```
config/destinations.yml   destinations tracked by the pipeline
extract/                  one module per API source + shared HTTP client
warehouse/load.py         bronze JSON -> silver parquet -> DuckDB
dbt/                      staging -> intermediate -> marts, seeds, tests
report/                   generates docs/INSIGHTS.md + external score validation
dashboard/app.py          Streamlit UI
tests/                    pytest unit tests (retry/date/parse/validation logic)
docs/INSIGHTS.md          current findings (generated by `report.insights`)
.github/workflows/        pipeline.yml (cron) + ci.yml (PR lint + smoke test)
```
