import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import duckdb
from src.components.sidebar import render_sidebar

st.set_page_config(layout="wide", page_title="EV Forecast", page_icon="📈", initial_sidebar_state="expanded")

PARQUET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'Electric_Vehicle_Population_Data.parquet'))

# ── CSS (matches rest of app) ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');
html,body,.main,[data-testid="stAppViewContainer"]{background:#08090F!important;font-family:'Inter',sans-serif!important;}
.block-container{max-width:1400px!important;padding:0 2rem 3rem!important;}
header[data-testid="stHeader"]{display:none!important;}
[data-testid="stSidebarNav"]{display:none!important;}
[data-testid="stSidebar"]{background:#09101A!important;border-right:1px solid #1A2236!important;}
[data-testid="stSidebarContent"]{padding-top:0!important;}
div[data-testid="stSidebar"] .stButton{margin-bottom:6px!important;}
div[data-testid="stSidebar"] .stButton>button{
    background:transparent!important;color:#64748B!important;border:1px solid transparent!important;
    border-radius:10px!important;padding:.55rem .9rem!important;font-weight:500!important;
    font-size:.875rem!important;text-align:left!important;width:100%!important;
    box-shadow:none!important;transition:all .15s!important;
}
div[data-testid="stSidebar"] .stButton>button:hover{
    background:rgba(0,212,255,.07)!important;border-color:rgba(0,212,255,.2)!important;
    color:#00D4FF!important;
}
[data-testid="stMetric"]{background:#111827!important;border:1px solid #1A2236!important;border-radius:16px!important;padding:1rem 1.25rem!important;position:relative;overflow:hidden;}
[data-testid="stMetric"]::after{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,#7C3AED,#00D4FF);}
[data-testid="stMetricValue"]{color:#00D4FF!important;font-weight:800!important;}
[data-testid="stMetricLabel"]{color:#64748B!important;font-size:.68rem!important;text-transform:uppercase!important;letter-spacing:.08em!important;}
</style>
""", unsafe_allow_html=True)

# ── Sidebar nav ───────────────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar()

# ── Load timeseries from parquet ──────────────────────────────────────────────
@st.cache_data
def load_ts() -> pd.DataFrame:
    q = f"""
        SELECT County AS county,
               CAST("Model Year" AS INT) AS year,
               COUNT(*) AS registrations
        FROM '{PARQUET_PATH}'
        WHERE "Model Year" IS NOT NULL
          AND CAST("Model Year" AS INT) < 2024
          AND State = 'WA'
        GROUP BY county, year
        ORDER BY county, year
    """
    df = duckdb.query(q).to_df()
    df["date"] = pd.to_datetime(df["year"].astype(str) + "-12-31")
    return df

ts_all = load_ts()
all_counties = sorted(ts_all["county"].dropna().unique())

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="padding:1.75rem 0 1.25rem;">
    <div style="color:#64748B;font-size:.62rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.3rem;">Predictive Analytics</div>
    <h1 style="color:#F1F5F9;font-size:1.85rem;font-weight:900;margin:0 0 .3rem;letter-spacing:-.5px;">EV Registration Forecast</h1>
    <p style="color:#64748B;font-size:.85rem;margin:0;">County-level growth predictions using Prophet + ARIMA · Washington State 2025–2030</p>
</div>
""", unsafe_allow_html=True)

# ── Controls ──────────────────────────────────────────────────────────────────
ctrl1, ctrl2, ctrl3, ctrl4, ctrl5 = st.columns([2, 1, 1, 1, 1])
with ctrl1:
    selected_counties = st.multiselect(
        "Select counties to forecast",
        options=all_counties,
        default=["King", "Pierce", "Snohomish"],
        help="Pick 1–5 counties for best readability"
    )
with ctrl2:
    start_year = st.slider("View start year", 2010, 2024, 2018)
with ctrl3:
    forecast_years = st.slider("Forecast horizon", 1, 10, 6)
with ctrl4:
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    show_bands = st.checkbox("Show confidence bands", value=True)
with ctrl5:
    st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
    log_scale = st.checkbox("Log scale", value=True, help="Recommended when mixing large and small counties")

if not selected_counties:
    st.info("Select at least one county above.")
    st.stop()

# ── Run forecasts ─────────────────────────────────────────────────────────────
COLORS = ["#00D4FF", "#7C3AED", "#F72585", "#10B981", "#F59E0B"]

try:
    from src.forecasting.forecaster import EVForecaster
    forecaster_available = True
except ImportError:
    forecaster_available = False

fig = go.Figure()
metrics = []
periods = forecast_years * 1  # annual frequency → 1 point per year

status_placeholder = st.empty()

for i, county in enumerate(selected_counties[:5]):
    color = COLORS[i % len(COLORS)]
    county_ts = ts_all[ts_all["county"] == county].sort_values("date")

    # Historical trace
    fig.add_trace(go.Scatter(
        x=county_ts["date"], y=county_ts["registrations"],
        name=f"{county} (actual)",
        mode="lines+markers",
        line=dict(color=color, width=2),
        marker=dict(size=5),
    ))

    if not forecaster_available or len(county_ts) < 2:
        metrics.append({"County": county, "Model": "N/A", "Note": "Insufficient data"})
        continue

    try:
        status_placeholder.markdown(f'<div style="color:#64748B;font-size:.8rem;">Running forecast for {county}…</div>', unsafe_allow_html=True)
        fc = EVForecaster().fit(county_ts.rename(columns={"date": "date", "registrations": "registrations"}), county)
        pred = fc.predict(periods=periods)

        # Stitch last historical point to forecast for visual continuity
        last_hist = county_ts.iloc[-1]
        stitch_x = [last_hist["date"]] + pred["ds"].tolist()
        stitch_y = [last_hist["registrations"]] + pred["yhat"].tolist()

        fig.add_trace(go.Scatter(
            x=stitch_x, y=stitch_y,
            name=f"{county} (forecast · {fc._model_name})",
            mode="lines",
            line=dict(color=color, width=2, dash="dot"),
        ))

        if show_bands:
            band_x = [last_hist["date"]] + pred["ds"].tolist() + pred["ds"].tolist()[::-1]
            band_y = ([last_hist["registrations"]] + pred["yhat_upper"].tolist() +
                      pred["yhat_lower"].tolist()[::-1])
            fig.add_trace(go.Scatter(
                x=band_x, y=band_y,
                fill="toself",
                fillcolor=color.replace(")", ", 0.08)").replace("rgb", "rgba") if "rgb" in color else color + "14",
                line=dict(color="rgba(0,0,0,0)"),
                showlegend=False,
                hoverinfo="skip",
            ))

        last_actual = int(county_ts["registrations"].iloc[-1])
        last_forecast = int(pred["yhat"].iloc[-1])
        growth_pct = (last_forecast - last_actual) / max(last_actual, 1) * 100
        metrics.append({
            "County": county,
            "Model": fc._model_name.upper(),
            f"{2024 + forecast_years} Forecast": f"{last_forecast:,}",
            "Growth": f"+{growth_pct:.0f}%",
        })
    except Exception as e:
        metrics.append({"County": county, "Model": "Error", "Note": str(e)[:60]})

status_placeholder.empty()

# ── Chart ─────────────────────────────────────────────────────────────────────
fig.update_layout(
    paper_bgcolor="#08090F", plot_bgcolor="#0D1117",
    font=dict(family="Inter,sans-serif", size=11, color="#CBD5E1"),
    height=500,
    margin=dict(l=60, r=30, t=40, b=50),
    xaxis=dict(gridcolor="#1A2236", zeroline=False, title="Year", range=[f"{start_year}-01-01", f"{2024 + forecast_years}-12-31"]),
    yaxis=dict(
        gridcolor="#1A2236", zeroline=False, title="Annual Registrations",
        type="log" if log_scale else "linear",
        **({
            "tickvals": [10, 100, 500, 1000, 5000, 10000, 50000, 100000],
            "ticktext": ["10", "100", "500", "1k", "5k", "10k", "50k", "100k"],
        } if log_scale else {})
    ),
    legend=dict(bgcolor="rgba(8,9,15,.9)", bordercolor="#1A2236", borderwidth=1, font=dict(size=11)),
    hoverlabel=dict(bgcolor="#111827", bordercolor="#1A2236", font_color="#E2E8F0"),
    hovermode="x unified",
)

# Add a vertical "today" line
fig.add_vline(x=pd.to_datetime("2023-12-31").timestamp() * 1000, line_dash="dash", line_color="rgba(100,116,139,.5)",
              annotation_text="Today", annotation_font_color="#64748B", annotation_font_size=10)

# Add user-friendly summary
if metrics:
    county_names = ", ".join([m["County"] for m in metrics])
    total_new = sum([int(str(m.get(f"{2024 + forecast_years} Forecast", "0")).replace(",", "")) for m in metrics if m.get(f"{2024 + forecast_years} Forecast") != "N/A"])
    st.info(f"**Insight:** You are predicting EV growth for {county_names} over the next {forecast_years} years (2025–{2024 + forecast_years}). By {2024 + forecast_years}, the model projects a total of **{total_new:,} EVs** across these selected counties, helping grid operators plan for future charging demand.")

st.plotly_chart(fig, use_container_width=True)



# ── Model explanation ─────────────────────────────────────────────────────────
with st.expander("How the forecasts work", expanded=False):
    st.markdown("""
    **Prophet** (Meta) is used for counties with 24+ years of data. It handles yearly seasonality and trend changes automatically.

    **ARIMA(1,1,1)** (statsmodels) is the fallback for sparse counties (<24 data points). It's lighter and more robust with limited history.

    The shaded band is the 80% confidence interval. Wider bands = less historical data = more uncertainty.

    The model fits on cumulative annual registrations per county derived from Model Year in the 276k-record dataset.
    """)

# ── Raw forecast data table ───────────────────────────────────────────────────
if forecaster_available and st.checkbox("Show raw forecast data"):
    all_preds = []
    for county in selected_counties[:5]:
        county_ts = ts_all[ts_all["county"] == county].sort_values("date")
        if len(county_ts) >= 2:
            try:
                fc = EVForecaster().fit(county_ts, county)
                pred = fc.predict(periods=periods)
                pred["county"] = county
                pred["model"] = fc._model_name
                all_preds.append(pred[["county", "ds", "yhat", "yhat_lower", "yhat_upper", "model"]])
            except Exception:
                pass
    if all_preds:
        combined = pd.concat(all_preds)
        combined["ds"] = combined["ds"].dt.year
        combined["yhat"] = combined["yhat"].round(0).astype(int)
        combined["yhat_lower"] = combined["yhat_lower"].round(0).astype(int)
        combined["yhat_upper"] = combined["yhat_upper"].round(0).astype(int)
        combined.columns = ["County", "Year", "Forecast", "Lower", "Upper", "Model"]
        st.dataframe(combined, use_container_width=True, hide_index=True)
