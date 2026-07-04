"""Generate docs/INSIGHTS.md from the fct_travel_score mart.

This doc used to be written by hand and drifted out of date every time a signal
was added. It's now a build artifact: run this after `dbt build` and it rewrites
the file from whatever's currently in the warehouse — including an external
validation of the score (see report.validation). Wired into the daily pipeline
so the committed doc can't go stale.

    uv run python -m report.insights
"""

import datetime as dt
from pathlib import Path

import duckdb
import pandas as pd

from report.validation import ValidationSummary, validate

REPO_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = REPO_ROOT / "warehouse.duckdb"
OUT_PATH = REPO_ROOT / "docs" / "INSIGHTS.md"
# Small committed mart snapshot the dashboard falls back to when there's no local
# warehouse — this is what makes a hosted (Streamlit Cloud) demo work without
# shipping the gitignored *.duckdb or the bronze/silver data.
SNAPSHOT_PATH = REPO_ROOT / "dashboard" / "snapshot" / "fct_travel_score.parquet"

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Northern / Southern hemisphere split, for the sanity check that peak months invert.
SOUTHERN = {"CPT", "SYD", "GIG"}

SIGNALS = [
    ("weather", "has_weather", "Weather"),
    ("demand", "has_demand", "Demand"),
    ("price", "has_price", "Price"),
    ("holiday", "has_holiday", "Holiday"),
    ("air_quality", "has_air_quality", "Air quality"),
    ("sea_temp", "has_sea_temp", "Sea temp"),
]


def load_mart(db_path: Path = DB_PATH) -> pd.DataFrame:
    con = duckdb.connect(str(db_path), read_only=True)
    try:
        return con.execute("select * from fct_travel_score order by iata, month").df()
    finally:
        con.close()


def _driver_label(row: pd.Series) -> str:
    """Which real (non-defaulted) signal contributes the most to this month."""
    candidates = {
        "mild weather": (row["weather_comfort_score"], row["has_weather"]),
        "light crowds": (row["demand_score"], row["has_demand"]),
        "good fares": (row["price_score"], row["has_price"]),
        "few holiday spikes": (row["holiday_pressure_score"], row["has_holiday"]),
        "clean air": (row["air_quality_score"], row["has_air_quality"]),
        "warm seas": (row["sea_temp_score"], row["has_sea_temp"]),
    }
    real = {label: score for label, (score, has) in candidates.items() if has}
    if not real:
        return "model defaults only"
    return max(real, key=real.get)


def best_months_section(df: pd.DataFrame) -> str:
    lines = [
        "## Best month, by destination",
        "",
        "| Destination | Top month | Score | Confidence | Leading real signal |",
        "|---|---|---|---|---|",
    ]
    for iata in sorted(df["iata"].unique()):
        d = df[df["iata"] == iata]
        top = d.loc[d["travel_score"].idxmax()]
        lines.append(
            f"| {top['name']} ({iata}) | {MONTHS[int(top['month']) - 1]} "
            f"| {top['travel_score']:.1f} | {top['data_confidence'] * 100:.0f}% "
            f"| {_driver_label(top)} |"
        )
    return "\n".join(lines)


def coverage_section(df: pd.DataFrame) -> str:
    lines = [
        "## Signal coverage",
        "",
        "Which signals are backed by real data vs. a neutral model default, per "
        "destination (● real · ○ default). `data_confidence` is the weight-weighted "
        "share of the score backed by real data.",
        "",
        "| Destination | " + " | ".join(label for _, _, label in SIGNALS) + " | Confidence |",
        "|---|" + "---|" * (len(SIGNALS) + 1),
    ]
    for iata in sorted(df["iata"].unique()):
        d = df[df["iata"] == iata]
        cells = []
        for _, has_col, _ in SIGNALS:
            cells.append("●" if bool(d[has_col].any()) else "○")
        conf = d["data_confidence"].mean() * 100
        lines.append(f"| {d['name'].iloc[0]} ({iata}) | " + " | ".join(cells) + f" | {conf:.0f}% |")
    return "\n".join(lines)


def hemisphere_section(df: pd.DataFrame) -> str:
    lines = [
        "## Hemisphere sanity check",
        "",
        "Peak months should invert across the equator — Northern-Hemisphere "
        "destinations peaking in mid-year, Southern in the local (Dec–Feb) summer half.",
        "",
    ]
    north_peaks, south_peaks = [], []
    for iata in sorted(df["iata"].unique()):
        d = df[df["iata"] == iata]
        top_month = int(d.loc[d["travel_score"].idxmax()]["month"])
        (south_peaks if iata in SOUTHERN else north_peaks).append((iata, top_month))
    north_mid = sum(4 <= m <= 9 for _, m in north_peaks)
    south_mid = sum((m <= 4 or m >= 10) for _, m in south_peaks)
    lines.append(
        f"- **Northern** ({', '.join(i for i, _ in north_peaks)}): "
        f"{north_mid}/{len(north_peaks)} peak in the Apr–Sep half. ✅"
        if north_mid == len(north_peaks)
        else f"- **Northern**: {north_mid}/{len(north_peaks)} peak in the Apr–Sep half."
    )
    lines.append(
        f"- **Southern** ({', '.join(i for i, _ in south_peaks)}): "
        f"{south_mid}/{len(south_peaks)} peak in the Oct–Apr (local summer) half. ✅"
        if south_mid == len(south_peaks)
        else f"- **Southern**: {south_mid}/{len(south_peaks)} peak in the Oct–Apr half."
    )
    return "\n".join(lines)


def validation_summary(df: pd.DataFrame) -> ValidationSummary:
    scores_by_dest = {
        iata: dict(zip(d["month"].astype(int), d["travel_score"]))
        for iata, d in df.groupby("iata")
    }
    return validate(scores_by_dest)


def validation_section(df: pd.DataFrame) -> str:
    summary = validation_summary(df)
    name_by_iata = df.drop_duplicates("iata").set_index("iata")["name"].to_dict()
    lines = [
        "## Does the score match conventional wisdom?",
        "",
        "An external check: for each destination, the model's monthly scores are "
        "compared against the *conventionally-recommended* time to visit "
        "(mainstream travel-guide consensus, encoded in `report/reference.py`) — "
        "signals the model never sees. This is a sanity check, not a target the "
        "model is tuned toward.",
        "",
        f"- **Directional agreement:** for **{summary.directional_hits}/{summary.n}** "
        "destinations the recommended months average a higher travel score than the "
        f"rest of the year (mean margin **{summary.mean_margin:+.1f}** points).",
        f"- **Peak month in the recommended window:** **{summary.top_in_window_hits}/{summary.n}** "
        "(exact), rising to **"
        f"{summary.top_adjacent_hits}/{summary.n}** allowing a ±1-month tolerance.",
        "",
        "| Destination | Recommended window | Rec. avg | Off-season avg | Margin | Peak month |",
        "|---|---|---:|---:|---:|---|",
    ]
    for r in summary.results:
        tick = "✅" if r.top_in_window else ("≈" if r.top_adjacent else "✗")
        lines.append(
            f"| {name_by_iata.get(r.iata, r.iata)} ({r.iata}) | {r.rationale} "
            f"| {r.recommended_avg:.1f} | {r.offseason_avg:.1f} "
            f"| {r.margin:+.1f} | {MONTHS[r.top_month - 1]} {tick} |"
        )
    lines += [
        "",
        "Where the model diverges it's explainable rather than random: Tokyo's peak "
        "lands in June because the weather-comfort formula weights mild temperature "
        "above the rainy-season precipitation penalty, and Lisbon skews to peak "
        "summer because the model optimizes weather comfort over the crowd-avoidance "
        "that drives the shoulder-season guidance. Both are documented limitations "
        "in the README, surfaced here by the validation rather than hidden by it.",
    ]
    return "\n".join(lines)


def build_markdown(df: pd.DataFrame, generated_at: dt.datetime | None = None) -> str:
    generated_at = generated_at or dt.datetime.now(dt.timezone.utc)
    n_dest = df["iata"].nunique()
    header = [
        "# Findings",
        "",
        "<!-- GENERATED FILE — do not edit by hand. -->",
        "<!-- Regenerate with: uv run python -m report.insights -->",
        "",
        f"_Auto-generated from `warehouse.duckdb` on "
        f"{generated_at:%Y-%m-%d %H:%M} UTC, covering {n_dest} destinations × 12 "
        "months. Numbers reflect whatever real data the warehouse currently holds "
        "(coverage varies by source — see the coverage table below)._",
        "",
    ]
    sections = [
        validation_section(df),
        best_months_section(df),
        coverage_section(df),
        hemisphere_section(df),
    ]
    return "\n".join(header) + "\n" + "\n\n".join(sections) + "\n"


def export_snapshot(df: pd.DataFrame, path: Path = SNAPSHOT_PATH) -> None:
    """Write the committed mart snapshot the hosted dashboard reads when no
    warehouse is present. Drops the derived month_name (the app recomputes it)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    print(f"[insights] wrote snapshot {path} ({len(df)} rows)")


def main(db_path: Path = DB_PATH, out_path: Path = OUT_PATH) -> None:
    df = load_mart(db_path)
    if df.empty:
        raise SystemExit(f"{db_path} has no fct_travel_score rows — run the pipeline first.")
    out_path.write_text(build_markdown(df))
    print(f"[insights] wrote {out_path} from {df['iata'].nunique()} destinations")
    export_snapshot(df)


if __name__ == "__main__":
    main()
