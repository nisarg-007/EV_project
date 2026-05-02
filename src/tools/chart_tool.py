"""
LangGraph chart generation tool.
Accepts a chart_type + a pandas .query() string, runs it against the EV
registrations dataset, and returns Plotly HTML for embedding.
"""

import os
import json
import logging
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from typing import Optional

from langchain_core.tools import tool  # type: ignore

logger = logging.getLogger(__name__)

PARQUET_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "processed",
    "Electric_Vehicle_Population_Data.parquet"
)
GEOJSON_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "wa_counties.geojson"
)
GEOJSON_URL = (
    "https://raw.githubusercontent.com/deldersveld/topojson/master/"
    "countries/us-states/WA-53-washington-counties.json"
)

_df_cache: Optional[pd.DataFrame] = None


def _load_df() -> pd.DataFrame:
    global _df_cache
    if _df_cache is None:
        _df_cache = pd.read_parquet(PARQUET_PATH)
        _df_cache.columns = [c.strip() for c in _df_cache.columns]
    return _df_cache


def _ensure_geojson() -> dict:
    if not os.path.exists(GEOJSON_PATH):
        os.makedirs(os.path.dirname(GEOJSON_PATH), exist_ok=True)
        try:
            resp = requests.get(GEOJSON_URL, timeout=10)
            resp.raise_for_status()
            with open(GEOJSON_PATH, "w") as f:
                json.dump(resp.json(), f)
        except Exception as exc:
            logger.warning("Could not download WA GeoJSON: %s", exc)
            return {}
    with open(GEOJSON_PATH) as f:
        return json.load(f)


def _to_html(fig) -> str:
    return fig.to_html(full_html=False, include_plotlyjs="cdn", config={"responsive": True})


DARK_TEMPLATE = dict(
    template="plotly_dark",
)

def _apply_dark_layout(fig):
    fig.update_layout(
        paper_bgcolor="#0D1117",
        plot_bgcolor="#0D1117",
        font=dict(color="#CBD5E1")
    )
    return fig



@tool(
    description=(
        "Generate an interactive chart from WA State EV registration data.\n"
        "chart_type: 'bar' | 'pie' | 'line' | 'scatter' | 'choropleth_wa'\n"
        "query: a pandas .query() string applied to the EV DataFrame "
        "(columns: County, Make, Model, Model Year, Electric Vehicle Type, Electric Range).\n"
        "Example: chart_type='bar', query='County == \"King\"', title='King County EVs'\n"
        "Returns: dict with keys 'html', 'chart_type', 'row_count', 'error'."
    )
)
def generate_chart_tool(
    chart_type: str,
    query: str = "",
    title: str = "",
    x_label: str = "",
    y_label: str = "",
) -> dict:
    """
    Generate a Plotly chart from EV registration data.

    Example calls:
      generate_chart_tool(chart_type="pie", query="County == 'King'", title="King County EV Types")
      generate_chart_tool(chart_type="bar", query="Make == 'TESLA'", title="Tesla Model Distribution")
      generate_chart_tool(chart_type="line", title="Statewide YoY Registrations")
      generate_chart_tool(chart_type="choropleth_wa", title="EV Density by County")
    """
    try:
        df = _load_df()
        if query:
            df = df.query(query)

        row_count = len(df)
        if row_count == 0:
            return {"html": "", "chart_type": chart_type, "row_count": 0,
                    "error": "Query returned 0 rows."}

        ct = chart_type.lower().strip()

        if ct == "bar":
            fig = _bar(df, title, x_label, y_label)
        elif ct == "pie":
            fig = _pie(df, title)
        elif ct == "line":
            fig = _line(df, title, x_label, y_label)
        elif ct == "scatter":
            fig = _scatter(df, title, x_label, y_label)
        elif ct == "choropleth_wa":
            fig = _choropleth(df, title)
        else:
            return {"html": "", "chart_type": ct, "row_count": row_count,
                    "error": f"Unknown chart_type '{chart_type}'."}

        return {"html": _to_html(fig), "chart_type": ct, "row_count": row_count, "error": None}

    except Exception as exc:
        logger.exception("generate_chart_tool error")
        return {"html": "", "chart_type": chart_type, "row_count": 0, "error": str(exc)}


# ── Individual chart builders ─────────────────────────────────────────────────

def _bar(df: pd.DataFrame, title: str, x_label: str, y_label: str):
    counts = df.groupby("Make").size().reset_index(name="count").sort_values("count", ascending=False).head(15)
    fig = px.bar(
        counts, x="Make", y="count",
        title=title or "EV Count by Make",
        labels={"Make": x_label or "Make", "count": y_label or "Count"},
        color="count",
        color_continuous_scale="Viridis",
        **DARK_TEMPLATE,
    )
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    return _apply_dark_layout(fig)


def _pie(df: pd.DataFrame, title: str):
    col = "Electric Vehicle Type" if "Electric Vehicle Type" in df.columns else "Make"
    counts = df[col].value_counts().reset_index()
    counts.columns = [col, "count"]
    fig = px.pie(
        counts, names=col, values="count",
        title=title or f"Distribution by {col}",
        color_discrete_sequence=px.colors.sequential.Plasma_r,
        **DARK_TEMPLATE,
    )
    fig.update_traces(textinfo="percent+label")
    return _apply_dark_layout(fig)


def _line(df: pd.DataFrame, title: str, x_label: str, y_label: str):
    if "Model Year" not in df.columns:
        raise ValueError("'Model Year' column required for line chart.")
    by_year = df.groupby("Model Year").size().reset_index(name="count").sort_values("Model Year")
    fig = px.line(
        by_year, x="Model Year", y="count",
        title=title or "EV Registrations Over Time",
        labels={"Model Year": x_label or "Model Year", "count": y_label or "Registrations"},
        markers=True,
        **DARK_TEMPLATE,
    )
    fig.update_traces(line_color="#00D4FF", marker_color="#7C3AED")
    return _apply_dark_layout(fig)


def _scatter(df: pd.DataFrame, title: str, x_label: str, y_label: str):
    if "Electric Range" not in df.columns or "Model Year" not in df.columns:
        raise ValueError("'Electric Range' and 'Model Year' required for scatter.")
    sample = df[df["Electric Range"] > 0].sample(min(2000, len(df)), random_state=42)
    fig = px.scatter(
        sample, x="Model Year", y="Electric Range",
        color="Make",
        title=title or "Electric Range vs Model Year",
        labels={"Model Year": x_label or "Model Year", "Electric Range": y_label or "Range (mi)"},
        opacity=0.6,
        **DARK_TEMPLATE,
    )
    return _apply_dark_layout(fig)


def _choropleth(df: pd.DataFrame, title: str):
    geojson = _ensure_geojson()
    counts = df.groupby("County").size().reset_index(name="ev_count")

    if not geojson:
        # Fallback: simple bar chart when GeoJSON unavailable
        fig = px.bar(
            counts.sort_values("ev_count", ascending=False),
            x="County", y="ev_count",
            title=title or "EV Count by County",
            **DARK_TEMPLATE,
        )
        return _apply_dark_layout(fig)

    fig = px.choropleth(
        counts,
        geojson=geojson,
        locations="County",
        featureidkey="properties.NAME",
        color="ev_count",
        color_continuous_scale="Plasma",
        title=title or "EV Density by County — Washington State",
        labels={"ev_count": "EV Count"},
        **DARK_TEMPLATE,
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
    return _apply_dark_layout(fig)
