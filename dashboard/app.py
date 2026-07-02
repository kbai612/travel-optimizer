"""Streamlit dashboard: when's the best time to visit each tracked destination.

Run with: `uv run streamlit run dashboard/app.py`
"""

from pathlib import Path

import duckdb
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DB_PATH = Path(__file__).resolve().parent.parent / "warehouse.duckdb"

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Fixed categorical order + sequential blue ramp — see the dataviz reference palette.
COLOR_WEATHER = "#1baf7a"
COLOR_DEMAND = "#eda100"
COLOR_PRICE = "#008300"
COLOR_HOLIDAY = "#4a3aa7"
SEQUENTIAL_BLUE = ["#cde2fb", "#9ec5f4", "#5598e7", "#2a78d6", "#184f95"]
SURFACE = "#fcfcfb"
GRIDLINE = "#e1e0d9"
TEXT_SECONDARY = "#52514e"


@st.cache_data
def load_scores() -> pd.DataFrame:
    con = duckdb.connect(str(DB_PATH), read_only=True)
    df = con.execute("select * from fct_travel_score order by iata, month").df()
    con.close()
    df["month_name"] = df["month"].map(lambda m: MONTH_NAMES[m - 1])
    return df


def recommendation(dest_df: pd.DataFrame, name: str) -> str:
    top = dest_df.sort_values("travel_score", ascending=False).head(3)
    lines = []
    for _, row in top.iterrows():
        drivers = {
            "mild weather": row["weather_comfort_score"],
            "light crowds": row["demand_score"],
            "good fares": row["price_score"],
            "few holiday spikes": row["holiday_pressure_score"],
        }
        best_driver = max(drivers, key=drivers.get)
        lines.append(f"**{row['month_name']}** (score {row['travel_score']:.0f}, driven by {best_driver})")
    return f"Best months to visit {name}: " + ", ".join(lines) + "."


def score_bar_chart(dest_df: pd.DataFrame) -> go.Figure:
    colors = [SEQUENTIAL_BLUE[min(4, int(s // 20))] for s in dest_df["travel_score"]]
    fig = go.Figure()
    fig.add_bar(x=dest_df["month_name"], y=dest_df["travel_score"], marker_color=colors)
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
        yaxis=dict(range=[0, 100], gridcolor=GRIDLINE, title="Travel score"),
        xaxis=dict(title=None),
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        showlegend=False,
        margin=dict(t=20, b=10),
    )
    return fig


def sub_score_chart(dest_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for label, column, color in [
        ("Weather comfort", "weather_comfort_score", COLOR_WEATHER),
        ("Demand (inverse)", "demand_score", COLOR_DEMAND),
        ("Price (inverse)", "price_score", COLOR_PRICE),
        ("Holiday pressure (inverse)", "holiday_pressure_score", COLOR_HOLIDAY),
    ]:
        fig.add_trace(
            go.Scatter(
                x=dest_df["month_name"],
                y=dest_df[column],
                mode="lines+markers",
                name=label,
                line=dict(color=color, width=2),
                marker=dict(size=6),
            )
        )
    fig.update_layout(
        yaxis=dict(range=[0, 100], gridcolor=GRIDLINE, title="Sub-score"),
        xaxis=dict(title=None),
        plot_bgcolor=SURFACE,
        paper_bgcolor=SURFACE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(t=40, b=10),
    )
    return fig


st.set_page_config(page_title="Travel Optimizer", layout="wide")
st.title("When should you actually go?")
st.caption(
    "Blends weather comfort, flight/demand activity, fare seasonality, and "
    "holiday-driven pressure into one score per destination, per month."
)

if not DB_PATH.exists():
    st.error(
        f"No warehouse found at {DB_PATH}. Run the pipeline first:\n\n"
        "`python -m extract.run --all && python -m warehouse.load && "
        "(cd dbt && dbt build --profiles-dir .)`"
    )
    st.stop()

scores = load_scores()
destinations = scores[["iata", "name"]].drop_duplicates().sort_values("name")

dest_name = st.selectbox("Destination", destinations["name"])
dest_iata = destinations.loc[destinations["name"] == dest_name, "iata"].iloc[0]
dest_df = scores[scores["iata"] == dest_iata].sort_values("month")

st.markdown(recommendation(dest_df, dest_name))

col1, col2 = st.columns(2)
with col1:
    st.subheader("Travel score by month")
    st.plotly_chart(score_bar_chart(dest_df), width="stretch")
with col2:
    st.subheader("What's driving the score")
    st.plotly_chart(sub_score_chart(dest_df), width="stretch")

def _score_cell_color(value: float) -> str:
    idx = min(4, int(value // 20))
    return f"background-color: {SEQUENTIAL_BLUE[idx]}"


st.subheader("All destinations, all months")
pivot = scores.pivot(index="name", columns="month_name", values="travel_score")[MONTH_NAMES]
st.dataframe(
    pivot.style.map(_score_cell_color).format("{:.0f}"),
    width="stretch",
)

with st.expander("How the score is built"):
    st.markdown(
        """
- **Weather comfort** — Open-Meteo daily history (last 3 full years), scored
  against a ~21°C ideal with rain/wind penalties.
- **Demand** *(inverse)* — OpenSky flight-volume seasonality, indexed against
  that destination's own average month. Neutral (50) until OpenSky credentials
  are configured — see `.env.example`.
- **Price** *(inverse)* — Travelpayouts cheapest-fare-by-month, indexed against
  that destination's own average month. Neutral (50) until a Travelpayouts
  token is configured.
- **Holiday pressure** *(inverse)* — density of public holidays (Nager.Date)
  in that destination's country and month.

Weights are set in `dbt/dbt_project.yml` (`vars:`) and can be re-tuned without
touching any SQL.
"""
    )
