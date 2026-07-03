"""Streamlit dashboard: when's the best time to visit each tracked destination —
and, given a month and some constraints, where to go.

Run with: `uv run streamlit run dashboard/app.py`
"""

import os
import time
from pathlib import Path

import duckdb
import httpx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

DB_PATH = Path(__file__).resolve().parent.parent / "warehouse.duckdb"
# Committed fallback mart (see report/insights.py::export_snapshot) so a hosted deploy
# with no local warehouse — e.g. Streamlit Community Cloud — still has data to show.
SNAPSHOT_PATH = Path(__file__).resolve().parent / "snapshot" / "fct_travel_score.parquet"
HOME_AIRPORT_IATA = os.environ.get("HOME_AIRPORT_IATA", "JFK")

# Fares are stored in USD (Travelpayouts' native currency); this is a display-only
# conversion applied in the browser, not something baked into the warehouse.
FX_API_URL = "https://open.er-api.com/v6/latest/USD"
CURRENCY_OPTIONS = ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "CNY", "INR", "BRL", "MXN"]
CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "CAD": "C$",
    "AUD": "A$",
    "JPY": "¥",
    "CHF": "CHF ",
    "CNY": "¥",
    "INR": "₹",
    "BRL": "R$",
    "MXN": "MX$",
}

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# A month needs at least this score to count as "great"; below this, a caveated
# recommendation is flagged as low-confidence in the narrative text.
GREAT_SCORE_THRESHOLD = 75
CONFIDENCE_WARN = 0.7
# sea_temp_score at/above this reads as swim-comfortable — used by the "warm seas" filter.
WARM_SEA_THRESHOLD = 55

# Default monthly-signal weights — must mirror `vars:` in dbt/dbt_project.yml, so the
# dashboard's live-recomputed score matches the warehouse when weights are untouched.
# The sidebar lets users re-weight interactively; values are normalized to sum to 1.
DEFAULT_WEIGHTS = {
    "weather": 0.25,
    "demand": 0.20,
    "price": 0.18,
    "holiday": 0.12,
    "air_quality": 0.15,
    "sea_temp": 0.10,
}
# (weight key, slider label, mart sub-score column, mart has-real-data column)
WEIGHT_META = [
    ("weather", "Weather comfort", "weather_comfort_score", "has_weather"),
    ("demand", "Demand (low crowds)", "demand_score", "has_demand"),
    ("price", "Price (cheap fares)", "price_score", "has_price"),
    ("holiday", "Holiday pressure", "holiday_pressure_score", "has_holiday"),
    ("air_quality", "Air quality", "air_quality_score", "has_air_quality"),
    ("sea_temp", "Sea temperature", "sea_temp_score", "has_sea_temp"),
]
# Advisory level -> multiplier, mirroring dim_destination.sql (missing level = 100/no penalty).
ADVISORY_SCORE = {1: 100, 2: 85, 3: 60, 4: 30}

SIGNALS = [
    ("Weather comfort", "weather_comfort_score", "has_weather"),
    ("Demand (inverse)", "demand_score", "has_demand"),
    ("Price (inverse)", "price_score", "has_price"),
    ("Holiday pressure (inverse)", "holiday_pressure_score", "has_holiday"),
    ("Air quality (inverse)", "air_quality_score", "has_air_quality"),
    ("Sea temperature", "sea_temp_score", "has_sea_temp"),
]

ADVISORY_BADGES = {
    1: ("✅", "Level 1 — Exercise normal precautions"),
    2: ("🟡", "Level 2 — Exercise increased caution"),
    3: ("🟠", "Level 3 — Reconsider travel"),
    4: ("🔴", "Level 4 — Do not travel"),
}

# Fixed categorical order + sequential blue ramp — see the dataviz reference palette.
COLOR_WEATHER = "#1baf7a"
COLOR_DEMAND = "#eda100"
COLOR_PRICE = "#008300"
COLOR_HOLIDAY = "#4a3aa7"
COLOR_AIR_QUALITY = "#c2410c"
COLOR_SEA_TEMP = "#0284c7"
MUTED_GRAY = "#a9a79f"
SEQUENTIAL_BLUE = ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#184f95"]
SURFACE = "#fcfcfb"
GRIDLINE = "#e1e0d9"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"

SIGNAL_COLORS = {
    "weather_comfort_score": COLOR_WEATHER,
    "demand_score": COLOR_DEMAND,
    "price_score": COLOR_PRICE,
    "holiday_pressure_score": COLOR_HOLIDAY,
    "air_quality_score": COLOR_AIR_QUALITY,
    "sea_temp_score": COLOR_SEA_TEMP,
}


def _freshness(mtime: float) -> str:
    age_hours = (time.time() - mtime) / 3600
    if age_hours < 1:
        return f"{age_hours * 60:.0f} min ago"
    if age_hours < 48:
        return f"{age_hours:.1f}h ago"
    return f"{age_hours / 24:.1f} days ago"


@st.cache_data(ttl=3600)
def load_scores() -> tuple[pd.DataFrame, str]:
    """Return (mart, source-caption). Prefers the live warehouse; falls back to the
    committed snapshot so a hosted demo works with no local pipeline run."""
    if DB_PATH.exists():
        try:
            con = duckdb.connect(str(DB_PATH), read_only=True)
            df = con.execute("select * from fct_travel_score order by iata, month").df()
            con.close()
            caption = f"Warehouse last built {_freshness(DB_PATH.stat().st_mtime)}."
        except duckdb.Error as e:
            st.error(
                f"Couldn't read `fct_travel_score` from {DB_PATH}: {e}\n\n"
                "The warehouse may be stale, or the mart may not have been built yet. "
                "Try re-running:\n\n`(cd dbt && dbt build --profiles-dir .)`"
            )
            st.stop()
    elif SNAPSHOT_PATH.exists():
        df = pd.read_parquet(SNAPSHOT_PATH)
        caption = (
            f"📦 Showing the bundled demo snapshot (committed {_freshness(SNAPSHOT_PATH.stat().st_mtime)}). "
            "Run the pipeline locally for a live warehouse — see the README."
        )
    else:
        st.error(
            f"No data found. Expected a warehouse at {DB_PATH} or a snapshot at "
            f"{SNAPSHOT_PATH}. Run the pipeline first:\n\n"
            "`python -m extract.run --all && python -m warehouse.load && "
            "(cd dbt && dbt build --profiles-dir .) && python -m report.insights`"
        )
        st.stop()
    if df.empty:
        st.error("`fct_travel_score` has no rows. Re-run the pipeline.")
        st.stop()
    df["month_name"] = df["month"].map(lambda m: MONTH_NAMES[m - 1])
    return df, caption


@st.cache_data(ttl=43200)
def fetch_exchange_rates() -> dict[str, float]:
    """USD-based FX rates, refreshed twice a day. Falls back to USD-only on failure."""
    try:
        resp = httpx.get(FX_API_URL, timeout=5.0)
        resp.raise_for_status()
        return resp.json().get("rates", {"USD": 1.0})
    except httpx.HTTPError:
        return {"USD": 1.0}


def advisory_multiplier(level: float) -> float:
    """Advisory level -> 0-100 multiplier; missing/unknown level = no penalty (100)."""
    if pd.isna(level):
        return 100.0
    return float(ADVISORY_SCORE.get(int(level), 100))


def apply_weights(scores: pd.DataFrame, weights: dict[str, float]) -> pd.DataFrame:
    """Recompute travel_score, data_confidence and an uncertainty band from the mart's
    stored sub-scores under a (possibly re-tuned) set of weights.

    The mart already stores each sub-score with its neutral default coalesced in, so
    with DEFAULT_WEIGHTS this reproduces fct_travel_score.travel_score exactly — the
    sidebar sliders just re-blend the same components without a warehouse rebuild.
    """
    total = sum(weights.values()) or 1.0
    w = {k: v / total for k, v in weights.items()}
    adv = scores["advisory_level"].map(advisory_multiplier)

    blended = sum(scores[col] * w[key] for key, _, col, _ in WEIGHT_META)
    # Weight-weighted share of the score backed by real (non-defaulted) data.
    confidence = sum(scores[has].astype(float) * w[key] for key, _, _, has in WEIGHT_META)
    # Defaulted signals sit at a neutral 50 but could truly be anywhere in 0-100, so the
    # blended score could plausibly swing by ±(missing weight × 50); carry that through
    # the advisory multiplier to get a band on the final score.
    band = (1.0 - confidence) * 50.0 * adv / 100.0

    out = scores.copy()
    out["travel_score"] = (blended * adv / 100.0).round(1)
    out["data_confidence"] = confidence.round(2)
    out["score_band"] = band.round(1)
    return out


def recommendation(dest_df: pd.DataFrame, name: str) -> str:
    top = dest_df.sort_values("travel_score", ascending=False).head(3)
    lines = []
    low_confidence_months = []
    for _, row in top.iterrows():
        drivers = {}
        if row["has_weather"]:
            drivers["mild weather"] = row["weather_comfort_score"]
        if row["has_demand"]:
            drivers["light crowds"] = row["demand_score"]
        if row["has_price"]:
            drivers["good fares"] = row["price_score"]
        if row["has_holiday"]:
            drivers["few holiday spikes"] = row["holiday_pressure_score"]
        if row["has_air_quality"]:
            drivers["clean air"] = row["air_quality_score"]
        if row["has_sea_temp"]:
            drivers["warm seas"] = row["sea_temp_score"]
        if drivers:
            best_driver = max(drivers, key=drivers.get)
            driver_text = f"driven by {best_driver}"
        else:
            driver_text = "no real signals yet for this month"
        lines.append(f"**{row['month_name']}** (score {row['travel_score']:.0f}, {driver_text})")
        if row["data_confidence"] < CONFIDENCE_WARN:
            low_confidence_months.append(row["month_name"])

    text = f"Best months to visit {name}: " + ", ".join(lines) + "."
    if low_confidence_months:
        text += (
            f" ⚠️ {', '.join(low_confidence_months)} relies partly on model "
            "defaults, not real data — see the coverage below."
        )
    return text


def advisory_badge(dest_df: pd.DataFrame) -> str:
    level = dest_df["advisory_level"].iloc[0]
    if pd.isna(level):
        return "⚪ **No US State Dept advisory on file** for this destination's country."
    icon, label = ADVISORY_BADGES.get(int(level), ("⚪", f"Level {level}"))
    return f"{icon} **US State Dept travel advisory:** {label}."


def advisory_short(level: float) -> str:
    """Compact icon+level for tables, tolerant of a missing (NaN) advisory."""
    if pd.isna(level):
        return "⚪ n/a"
    icon, _ = ADVISORY_BADGES.get(int(level), ("⚪", ""))
    return f"{icon} L{int(level)}"


def score_bar_chart(dest_df: pd.DataFrame) -> go.Figure:
    colors = [SEQUENTIAL_BLUE[min(4, int(s // 20))] for s in dest_df["travel_score"]]
    fig = go.Figure()
    # Uncertainty band: widths grow for months leaning on defaulted (guessed) signals.
    error_y = None
    if "score_band" in dest_df and dest_df["score_band"].fillna(0).gt(0).any():
        error_y = dict(
            type="data",
            array=dest_df["score_band"],
            color=TEXT_SECONDARY,
            thickness=1.3,
            width=4,
        )
    fig.add_bar(
        x=dest_df["month_name"], y=dest_df["travel_score"], marker_color=colors, error_y=error_y
    )
    for _, row in dest_df.nlargest(3, "travel_score").iterrows():
        fig.add_annotation(
            x=row["month_name"],
            y=row["travel_score"],
            text=f"{row['travel_score']:.0f}",
            showarrow=False,
            yshift=14,
            font=dict(color=TEXT_SECONDARY, size=12),
        )
    fig.update_layout(
        template=None,
        font=dict(color=TEXT_PRIMARY),
        yaxis=dict(
            range=[0, 100], gridcolor=GRIDLINE, title="Travel score", linecolor=GRIDLINE
        ),
        xaxis=dict(title=None, linecolor=GRIDLINE, automargin=True),
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        showlegend=False,
        margin=dict(t=20, b=40),
    )
    return fig


def sub_score_chart(dest_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for label, column, has_column in SIGNALS:
        has_any_real = dest_df[has_column].any()
        color = SIGNAL_COLORS[column] if has_any_real else MUTED_GRAY
        name = label if has_any_real else f"{label} (no data — model default)"
        marker_symbols = ["circle" if h else "circle-open" for h in dest_df[has_column]]
        fig.add_trace(
            go.Scatter(
                x=dest_df["month_name"],
                y=dest_df[column],
                mode="lines+markers",
                name=name,
                line=dict(color=color, width=2, dash="solid" if has_any_real else "dot"),
                marker=dict(size=7, symbol=marker_symbols, color=color),
            )
        )
    fig.update_layout(
        template=None,
        font=dict(color=TEXT_PRIMARY),
        yaxis=dict(
            range=[0, 100], gridcolor=GRIDLINE, title="Sub-score", linecolor=GRIDLINE
        ),
        xaxis=dict(title=None, linecolor=GRIDLINE, automargin=True),
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, x=0, font=dict(color=TEXT_PRIMARY)),
        margin=dict(t=90, b=40),
    )
    return fig


def radar_chart(best_row: pd.Series) -> go.Figure:
    categories = [label for label, _, _ in SIGNALS]
    values = [best_row[column] for _, column, _ in SIGNALS]
    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + values[:1],
            theta=categories + categories[:1],
            fill="toself",
            line=dict(color=COLOR_WEATHER, width=2),
            fillcolor="rgba(27,175,122,0.15)",
            name=best_row["month_name"],
        )
    )
    fig.update_layout(
        template=None,
        polar=dict(
            bgcolor=SURFACE,
            radialaxis=dict(range=[0, 100], gridcolor=GRIDLINE, linecolor=GRIDLINE),
            angularaxis=dict(gridcolor=GRIDLINE, linecolor=GRIDLINE),
        ),
        font=dict(color=TEXT_PRIMARY, size=11),
        paper_bgcolor=SURFACE,
        showlegend=False,
        margin=dict(t=60, b=40, l=40, r=40),
    )
    return fig


def seasonality_bar_chart(dest_df: pd.DataFrame) -> go.Figure:
    scores = dest_df["travel_score"]
    colors = [SEQUENTIAL_BLUE[min(4, int(s // 20))] for s in scores]
    fig = go.Figure()
    fig.add_bar(
        x=dest_df["month_name"],
        y=scores,
        marker_color=colors,
        text=[f"{s:.0f}" for s in scores],
        textposition="outside",
        textfont=dict(color=TEXT_PRIMARY, size=11),
        hovertemplate="%{x}: %{y:.0f}<extra></extra>",
    )
    fig.update_layout(
        template=None,
        font=dict(color=TEXT_PRIMARY),
        yaxis=dict(range=[0, 115], visible=False),
        xaxis=dict(title=None, linecolor=GRIDLINE, automargin=True),
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        showlegend=False,
        margin=dict(t=20, b=40),
    )
    return fig


def price_chart(dest_df: pd.DataFrame, currency: str, symbol: str, fx_rate: float) -> go.Figure:
    converted = dest_df["avg_price"] * fx_rate
    fig = go.Figure()
    fig.add_bar(
        x=dest_df["month_name"],
        y=converted,
        marker_color=COLOR_PRICE,
        text=[f"{symbol}{p:,.0f}" if pd.notna(p) else "" for p in converted],
        textposition="outside",
        textfont=dict(color=TEXT_PRIMARY, size=11),
        hovertemplate="%{x}: " + symbol + "%{y:,.0f}<extra></extra>",
    )
    # Pad the top of the range so outside-positioned bar labels don't get clipped.
    max_price = converted.max()
    fig.update_layout(
        template=None,
        font=dict(color=TEXT_PRIMARY),
        yaxis=dict(
            range=[0, max_price * 1.15],
            gridcolor=GRIDLINE,
            linecolor=GRIDLINE,
            title=f"Cheapest fare ({currency})",
        ),
        xaxis=dict(title=None, linecolor=GRIDLINE, automargin=True),
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        showlegend=False,
        margin=dict(t=40, b=40),
    )
    return fig


def ranked_destinations_chart(view: pd.DataFrame) -> go.Figure:
    """Horizontal bar of destinations ranked by travel score (best on top)."""
    ordered = view.sort_values("travel_score")  # ascending -> highest ends up on top
    colors = [SEQUENTIAL_BLUE[min(4, int(s // 20))] for s in ordered["travel_score"]]
    labels = [f"{n} · {w}" for n, w in zip(ordered["name"], ordered["when"])]
    fig = go.Figure()
    fig.add_bar(
        x=ordered["travel_score"],
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{s:.0f}" for s in ordered["travel_score"]],
        textposition="outside",
        textfont=dict(color=TEXT_PRIMARY, size=12),
        hovertemplate="%{y}: %{x:.0f}<extra></extra>",
    )
    fig.update_layout(
        template=None,
        font=dict(color=TEXT_PRIMARY),
        xaxis=dict(range=[0, 105], gridcolor=GRIDLINE, title="Travel score", linecolor=GRIDLINE),
        yaxis=dict(title=None, linecolor=GRIDLINE, automargin=True),
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        showlegend=False,
        margin=dict(t=20, b=40, l=10),
        height=max(240, 46 * len(view)),
    )
    return fig


def _score_cell_color(value: float) -> str:
    idx = min(4, int(value // 20))
    return f"background-color: {SEQUENTIAL_BLUE[idx]}"


def render_when_view(
    scores: pd.DataFrame, currency: str, currency_symbol: str, fx_rate: float
) -> None:
    """Per-destination view: pick a place, see the best months and why."""
    destinations = scores[["iata", "name"]].drop_duplicates().sort_values("name")
    dest_name = st.selectbox("Destination", destinations["name"])
    dest_iata = destinations.loc[destinations["name"] == dest_name, "iata"].iloc[0]
    dest_df = scores[scores["iata"] == dest_iata].sort_values("month")

    st.markdown(recommendation(dest_df, dest_name))
    st.caption(advisory_badge(dest_df))

    best_row = dest_df.loc[dest_df["travel_score"].idxmax()]
    worst_row = dest_df.loc[dest_df["travel_score"].idxmin()]
    avg_score = dest_df["travel_score"].mean()
    spread = best_row["travel_score"] - worst_row["travel_score"]
    if spread >= 25:
        spread_label = "Huge"
    elif spread >= 12:
        spread_label = "Moderate"
    else:
        spread_label = "Barely"
    great_months = int((dest_df["travel_score"] >= GREAT_SCORE_THRESHOLD).sum())
    overall_confidence = dest_df["data_confidence"].mean()
    missing_signals = [
        label.split(" (")[0] for label, _, has_col in SIGNALS if not dest_df[has_col].all()
    ]

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1.container(border=True):
        st.metric(
            "Best month",
            best_row["month_name"],
            delta=f"+{best_row['travel_score'] - avg_score:.0f} vs avg",
        )
    with kpi2.container(border=True):
        st.metric("Timing matters", spread_label, delta=f"{spread:.0f} pt spread", delta_color="off")
    with kpi3.container(border=True):
        st.metric(f"Great months (≥{GREAT_SCORE_THRESHOLD})", f"{great_months}/12")
    with kpi4.container(border=True):
        st.metric(
            "Data confidence",
            f"{overall_confidence * 100:.0f}%",
            help=(
                f"Model defaults used for: {', '.join(missing_signals)}."
                if missing_signals
                else "All six signals have real data all year."
            ),
        )

    sorted_df = dest_df.sort_values("travel_score", ascending=False)
    shoulder_row = sorted_df.iloc[1] if len(sorted_df) > 1 else None
    insight = f"**Avoid:** {worst_row['month_name']} tends to score lowest ({worst_row['travel_score']:.0f})."
    if shoulder_row is not None:
        insight += (
            f" **Shoulder pick:** {shoulder_row['month_name']} is close behind the top month "
            f"({shoulder_row['travel_score']:.0f}) and may be less crowded or cheaper to book."
        )
    st.markdown(insight)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Travel score by month")
        st.plotly_chart(score_bar_chart(dest_df), width="stretch", theme=None)
        st.caption(
            "Error bars show the uncertainty band — wider where the month leans on "
            "defaulted (guessed) signals rather than real data."
        )
    with col2:
        st.subheader("What's driving the score")
        st.plotly_chart(sub_score_chart(dest_df), width="stretch", theme=None)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader(f"Why {best_row['month_name']} wins")
        st.plotly_chart(radar_chart(best_row), width="stretch", theme=None)
    with col4:
        st.subheader("Seasonality at a glance")
        st.plotly_chart(seasonality_bar_chart(dest_df), width="stretch", theme=None)
        st.caption("Jan→Dec — same color scale as the table below.")

    st.subheader(f"Fares by month (from {HOME_AIRPORT_IATA}, {currency})")
    if dest_df["avg_price"].notna().any():
        st.plotly_chart(
            price_chart(dest_df, currency, currency_symbol, fx_rate), width="stretch", theme=None
        )
        st.caption(
            f"Cheapest fare found per month ({currency}), {HOME_AIRPORT_IATA} → {dest_iata}. "
            "Blank months have no fare data yet. Converted from USD at a live exchange rate."
            if currency != "USD"
            else f"Cheapest fare found per month (USD), {HOME_AIRPORT_IATA} → {dest_iata}. "
            "Blank months have no fare data yet."
        )
    else:
        st.info(
            "No fare data available yet for this destination — configure a Travelpayouts "
            "token to populate this chart. See `.env.example`."
        )

    st.subheader("All destinations, all months")
    pivot = scores.pivot(index="name", columns="month_name", values="travel_score")[MONTH_NAMES]
    st.dataframe(pivot.style.map(_score_cell_color).format("{:.0f}"), width="stretch")

    with st.expander("How the score is built"):
        st.markdown(SCORE_METHODOLOGY_MD)


def render_where_view(
    scores: pd.DataFrame, currency: str, currency_symbol: str, fx_rate: float
) -> None:
    """Cross-destination view: fix a month + constraints, rank every destination."""
    st.markdown(
        "Flip the question around: pick when you can travel and what matters to you, "
        "and see **where** scores best."
    )

    ctrl1, ctrl2 = st.columns([2, 2])
    with ctrl1:
        month_choice = st.selectbox(
            "I can travel in…",
            ["Each destination's best month"] + MONTH_NAMES,
            help="Pick a specific month to compare everywhere head-to-head, or let each "
            "destination put its own best month forward.",
        )
    with ctrl2:
        max_advisory = st.select_slider(
            "Max US State Dept advisory level",
            options=[1, 2, 3, 4],
            value=4,
            format_func=lambda level_value: f"≤ Level {level_value}",
            help="Level 1 = normal precautions … Level 4 = do not travel. Destinations "
            "with no advisory on file (e.g. USA) always pass.",
        )

    f1, f2 = st.columns(2)
    with f1:
        warm_seas = st.checkbox(
            "🏖️ Swim-friendly seas only",
            help="Keep only destinations with a warm-enough sea-surface temperature "
            "that month (needs real marine data — landlocked airports are excluded).",
        )
    with f2:
        real_price_only = st.checkbox(
            "💵 Only where I have real fare data",
            help="Exclude destinations whose price sub-score is a neutral model default.",
        )

    # Build the per-destination candidate rows for the chosen month.
    if month_choice == "Each destination's best month":
        idx = scores.groupby("iata")["travel_score"].idxmax()
        view = scores.loc[idx].copy()
        when_label = "each destination's best month"
    else:
        month_num = MONTH_NAMES.index(month_choice) + 1
        view = scores[scores["month"] == month_num].copy()
        when_label = month_choice
    view["when"] = view["month_name"]
    view["fare"] = view["avg_price"] * fx_rate

    # Budget filter, in the selected currency. Only meaningful when some fares exist.
    priced = view["fare"].dropna()
    budget = None
    if not priced.empty:
        lo, hi = int(priced.min()), int(priced.max())
        if hi > lo:
            budget = st.slider(
                f"Max fare from {HOME_AIRPORT_IATA} ({currency})",
                min_value=lo,
                max_value=hi,
                value=hi,
                help="Destinations with no fare data yet are kept regardless (shown as “—”).",
            )

    # Apply filters. Missing advisory (NaN) is treated as passing — it means no
    # published advisory, not an unknown risk; same rationale as dim_destination.
    n_total = len(view)
    view = view[view["advisory_level"].isna() | (view["advisory_level"] <= max_advisory)]
    if warm_seas:
        view = view[view["has_sea_temp"] & (view["sea_temp_score"] >= WARM_SEA_THRESHOLD)]
    if real_price_only:
        view = view[view["has_price"]]
    if budget is not None:
        view = view[view["fare"].isna() | (view["fare"] <= budget)]

    if view.empty:
        st.warning("No destinations match those filters — try loosening them.")
        return

    view = view.sort_values("travel_score", ascending=False)
    winner = view.iloc[0]
    runners = ", ".join(view.iloc[1:3]["name"]) if len(view) > 1 else ""
    headline = (
        f"🏆 For **{when_label}**, **{winner['name']}** scores highest "
        f"(**{winner['travel_score']:.0f}** in {winner['when']})."
    )
    if runners:
        headline += f" Next best: {runners}."
    if len(view) < n_total:
        headline += f" _({len(view)} of {n_total} destinations match your filters.)_"
    st.markdown(headline)

    chart_col, table_col = st.columns([3, 2])
    with chart_col:
        st.plotly_chart(ranked_destinations_chart(view), width="stretch", theme=None)
    with table_col:
        table = pd.DataFrame(
            {
                "Destination": view["name"].values,
                "Month": view["when"].values,
                "Score": view["travel_score"].round(0).astype(int).values,
                "Confidence": (view["data_confidence"] * 100).round(0).astype(int).astype(str)
                + "%",
                f"Fare ({currency})": [
                    f"{currency_symbol}{p:,.0f}" if pd.notna(p) else "—" for p in view["fare"]
                ],
                "Advisory": [advisory_short(lvl) for lvl in view["advisory_level"]],
            }
        )
        table.index = range(1, len(table) + 1)
        table.index.name = "Rank"
        st.dataframe(table, width="stretch")

    st.caption(
        "Score blends weather, demand, price, holidays, air quality and sea temperature, "
        "then applies the country's safety-advisory multiplier. “Confidence” is the share "
        "of that score backed by real (non-default) data."
    )
    with st.expander("How the score is built"):
        st.markdown(SCORE_METHODOLOGY_MD)


SCORE_METHODOLOGY_MD = """
- **Weather comfort** — Open-Meteo daily history (last 3 full years), scored
  against a ~22°C *feels-like* (apparent temperature) ideal, with rain, wind,
  and sunshine-hours factored in.
- **Demand** *(inverse)* — OpenSky flight-volume seasonality, indexed against
  that destination's own average month. Neutral (50) until OpenSky credentials
  are configured — see `.env.example`.
- **Price** *(inverse)* — Travelpayouts cheapest-fare-by-month, indexed against
  that destination's own average month. Neutral (50) until a Travelpayouts
  token is configured.
- **Holiday pressure** *(inverse)* — density of public holidays (Nager.Date)
  in that destination's country and month.
- **Air quality** *(inverse)* — Open-Meteo Air Quality (CAMS) monthly PM2.5
  average, scored against the WHO annual guideline.
- **Sea temperature** — Open-Meteo Marine monthly sea-surface temperature,
  scored against a ~26°C swim-comfort ideal. Neutral (50) for destinations
  without a nearby sea grid cell.

These six signals are blended by weight into a monthly score, which is then
**multiplied** by a country-level safety adjustment from the US State
Department's travel advisory (Level 1 = no adjustment, Level 4 = heavily
discounted).

Weights are set in `dbt/dbt_project.yml` (`vars:`) and can be re-tuned without
touching any SQL.

**Coverage & confidence** — `data_confidence` is the weight-weighted share of the
score backed by real data, computed in `fct_travel_score.sql`.
"""


st.set_page_config(page_title="Travel Optimizer", layout="wide")
st.title("When — and where — should you actually go?")
st.caption(
    "Blends weather comfort, flight/demand activity, fare seasonality, holiday-driven "
    "pressure, air quality, and sea temperature into one score per destination, per "
    "month — then adjusts for the destination country's travel advisory level."
)

raw_scores, data_caption = load_scores()
st.caption(data_caption)
fx_rates = fetch_exchange_rates()
available_currencies = [c for c in CURRENCY_OPTIONS if c in fx_rates] or ["USD"]

with st.sidebar:
    st.header("Display")
    currency = st.selectbox("Currency", available_currencies)
    st.caption("Fares are stored in USD and converted here at a live rate.")

    st.header("⚖️ Signal weights")
    st.caption(
        "Re-blend the score live — no warehouse rebuild. Weights are normalized to "
        "sum to 1, so only their *relative* size matters."
    )
    weights = {
        key: st.slider(label, 0.0, 0.50, DEFAULT_WEIGHTS[key], 0.01)
        for key, label, _, _ in WEIGHT_META
    }
    weight_total = sum(weights.values())
    if weight_total == 0:
        st.warning("All weights are zero — falling back to the defaults.")
        weights = dict(DEFAULT_WEIGHTS)
    is_custom = any(
        abs(weights[k] - DEFAULT_WEIGHTS[k]) > 1e-9 for k in DEFAULT_WEIGHTS
    )
    if is_custom:
        norm = ", ".join(
            f"{label.split(' (')[0]} {weights[key] / sum(weights.values()) * 100:.0f}%"
            for key, label, _, _ in WEIGHT_META
        )
        st.caption(f"**Custom mix** (normalized): {norm}")
    else:
        st.caption("Using the pipeline's default weights.")

fx_rate = fx_rates.get(currency, 1.0)
currency_symbol = CURRENCY_SYMBOLS.get(currency, f"{currency} ")

# Recompute scores under the (possibly re-tuned) weights before rendering either view.
scores = apply_weights(raw_scores, weights)
if is_custom:
    st.info(
        "⚙️ Showing a **custom weighting** — scores below differ from the pipeline "
        "default. Adjust the sliders in the sidebar, or set them all back to reset.",
        icon="⚙️",
    )

tab_when, tab_where = st.tabs(["🗓️ When should I go?", "🌍 Where should I go?"])
with tab_when:
    render_when_view(scores, currency, currency_symbol, fx_rate)
with tab_where:
    render_where_view(scores, currency, currency_symbol, fx_rate)
