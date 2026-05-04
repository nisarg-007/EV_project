import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
from datetime import datetime
from src.components.sidebar import render_sidebar

try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    px = None
    go = None
    PLOTLY_AVAILABLE = False

try:
    from fpdf import FPDF
except ImportError:
    FPDF = None

PARQUET_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'Electric_Vehicle_Population_Data.parquet'))

st.set_page_config(layout="wide", page_title="EV Dashboard", page_icon="📊", initial_sidebar_state="expanded")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600;700&family=Manrope:wght@300;400;500;600;700;800&display=swap');
:root {
    --bg: #08080C;
    --surface: #0E0E14;
    --card: #121218;
    --border: #1E1E2A;
    --border2: #2A2A38;
    --volt: #CCFF00;
    --volt-dim: rgba(204,255,0,0.08);
    --volt-mid: rgba(204,255,0,0.18);
    --ember: #FF6B35;
    --ice: #2DD4BF;
    --t1: #EAEAF0;
    --t2: #B0B0C0;
    --t3: #6B6B80;
    --t4: #3A3A4E;
}
html,body,.main,[data-testid="stAppViewContainer"]{background:var(--bg)!important;font-family:'Manrope',-apple-system,sans-serif!important;}
.block-container{max-width:1440px!important;padding:0 2rem 2rem!important;}

/* Hide top navbar and sidebar nav */
header[data-testid="stHeader"]{display:none!important;}
[data-testid="stSidebarNav"]{display:none!important;}

/* Sidebar — no wasted top space */
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0A0A10 0%,#0E0E14 100%)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"]>div:first-child{padding:0!important;}
[data-testid="stSidebarContent"]{padding-top:0!important;}

/* Metrics */
[data-testid="stMetric"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:20px!important;padding:1.2rem 1.5rem!important;transition:all .25s cubic-bezier(.4,0,.2,1)!important;position:relative;overflow:hidden;}
[data-testid="stMetric"]::after{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--ice),var(--volt));}
[data-testid="stMetric"]:hover{border-color:rgba(204,255,0,.35)!important;box-shadow:0 0 0 1px rgba(204,255,0,.1),0 8px 32px rgba(0,0,0,.4)!important;transform:translateY(-2px)!important;}
[data-testid="stMetricValue"]{color:var(--volt)!important;font-size:1.75rem!important;font-weight:800!important;letter-spacing:-.5px!important;}
[data-testid="stMetricLabel"]{color:var(--t3)!important;font-size:.68rem!important;font-weight:700!important;letter-spacing:.1em!important;text-transform:uppercase!important;}
[data-testid="stMetricDelta"]{color:var(--green)!important;font-size:.75rem!important;}

/* Plotly containers */
.js-plotly-plot{border-radius:18px!important;border:1px solid var(--border)!important;box-shadow:0 4px 24px rgba(0,0,0,.4)!important;overflow:hidden!important;}

/* Streamlit form / expander overrides */
[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:14px!important;overflow:hidden!important;}
[data-testid="stExpanderDetails"]{background:var(--card)!important;}

/* Selectbox / multiselect / radio / slider */
[data-testid="stSelectbox"] div,[data-testid="stMultiSelect"] div{border-radius:10px!important;}
.stSlider [data-testid="stTickBar"]{color:var(--t3)!important;}

/* Sidebar buttons */
div[data-testid="stSidebar"] .stButton{margin-bottom:6px!important;}
div[data-testid="stSidebar"] .stButton>button{
    background:transparent!important;color:var(--t2)!important;
    border:1px solid transparent!important;border-radius:10px!important;
    padding:.6rem 1rem!important;font-weight:500!important;font-size:.88rem!important;
    text-align:left!important;width:100%!important;box-shadow:none!important;
    letter-spacing:0!important;transition:all .2s!important;
}
div[data-testid="stSidebar"] .stButton>button:hover{
    background:rgba(204,255,0,.07)!important;border-color:rgba(204,255,0,.2)!important;
    color:var(--volt)!important;transform:none!important;box-shadow:none!important;
}

/* Chart control buttons (inline above charts) */
div.ctrl-btn .stButton>button{
    background:var(--card2)!important;color:var(--t2)!important;
    border:1px solid var(--border2)!important;border-radius:8px!important;
    padding:.35rem .9rem!important;font-size:.78rem!important;font-weight:500!important;
    box-shadow:none!important;letter-spacing:0!important;transition:all .15s!important;
}
div.ctrl-btn .stButton>button:hover{
    border-color:rgba(204,255,0,.4)!important;color:var(--volt)!important;
    background:rgba(204,255,0,.06)!important;transform:none!important;box-shadow:none!important;
}

/* Section divider label */
.sec-label{color:var(--t3);font-size:.65rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.6rem;margin-top:.1rem;}

/* Chart card wrapper */
.chart-wrap{background:var(--card);border:1px solid var(--border);border-radius:20px;padding:1.25rem 1.5rem 0.5rem;margin-bottom:1.5rem;}

::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border2);border-radius:3px;}
::-webkit-scrollbar-thumb:hover{background:var(--volt);}

@media (max-width: 1040px) {
    .block-container{padding:0 1rem 2rem!important;}
    .stButton>button{font-size:.82rem!important;}
    .chart-wrap{padding:1rem!important;}
}
</style>
""", unsafe_allow_html=True)

# ── Data ───────────────────────────────────────────────────────────────────────
@st.cache_data
def load_main():
    return pd.read_parquet(PARQUET_PATH)

@st.cache_data
def parse_locations(df_hash):
    df = load_main()
    parsed = df['Vehicle Location'].dropna().str.extract(r'POINT \(([^ ]+) ([^)]+)\)')
    parsed.columns = ['lon','lat']
    return df.join(parsed.astype(float))

if not PLOTLY_AVAILABLE:
    st.error(
        'Plotly is not installed in this Python environment.\n'
        'Please install it with `pip install plotly` and restart the app.'
    )
    st.stop()

# ── Theme helper ───────────────────────────────────────────────────────────────
SCALES = {
    "Cyan → Purple": [[0,"#CCFF00"],[1,"#2DD4BF"]],
    "Purple → Pink": [[0,"#2DD4BF"],[1,"#FF6B35"]],
    "Green → Cyan":  [[0,"#2DD4BF"],[1,"#CCFF00"]],
    "Amber → Pink":  [[0,"#FF6B35"],[1,"#FF6B35"]],
}

def dt(fig, h=430, ml=55, mr=20, mt=52, mb=38):
    fig.update_layout(
        paper_bgcolor="#0A0D14", plot_bgcolor="#0E0E14",
        font=dict(family="'Manrope','IBM Plex Mono',sans-serif", size=11, color="#B0B0C0"),
        margin=dict(l=ml,r=mr,t=mt,b=mb), height=h,
        xaxis=dict(gridcolor="#1E1E2A", zeroline=False, linecolor="#1E1E2A"),
        yaxis=dict(gridcolor="#1E1E2A", zeroline=False, linecolor="#1E1E2A"),
        legend=dict(bgcolor="rgba(10,13,20,.9)", bordercolor="#1E1E2A", borderwidth=1),
        hoverlabel=dict(bgcolor="#121218", bordercolor="#1E1E2A", font_color="#B0B0C0"),
    )
    return fig


def generate_dashboard_report(df: pd.DataFrame, sel_county, yr, ev_type) -> tuple[bytes | str, str]:
    title = "EV Dashboard Report"
    summary_lines = [
        f"EV Dashboard Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Selected counties: {', '.join(sel_county) if sel_county else 'All counties'}",
        f"Model year range: {yr[0]}-{yr[1]}",
        f"EV type filter: {ev_type}",
        f"Total EVs: {len(df):,}",
        f"BEV registrations: {df['Electric Vehicle Type'].str.contains('BEV', na=False).sum():,}",
        f"PHEV registrations: {df['Electric Vehicle Type'].str.contains('PHEV', na=False).sum():,}",
        f"Average electric range: {df[df['Electric Range'] > 0]['Electric Range'].mean():.1f} mi",
    ]
    content = "\n".join(summary_lines)

    if FPDF is None:
        return content.encode('utf-8'), "text/plain"

    pdf = FPDF()
    pdf.set_auto_page_break(True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(pdf.epw, 10, title, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    for line in summary_lines[1:]:
        pdf.multi_cell(pdf.epw, 8, line)
    pdf.ln(4)
    pdf.multi_cell(pdf.epw, 8, "This report summarizes current dashboard filter selections and EV adoption insights for Washington State.")
    return bytes(pdf.output()), "application/pdf"


def section(label):
    st.markdown(f'<div class="sec-label">{label}</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    render_sidebar()

    st.markdown('<div style="height:1px;background:#1E1E2A;margin:.75rem 1.2rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 1.2rem;"><div style="color:#6B6B80;font-size:.62rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.6rem;">Global Filters</div></div>', unsafe_allow_html=True)

    df_raw = load_main()
    all_counties = sorted(df_raw['County'].dropna().unique())
    sel_county = st.multiselect("County", all_counties, placeholder="All counties")
    min_y, max_y = int(df_raw['Model Year'].min()), int(df_raw['Model Year'].max())
    yr = st.slider("Model Year", min_y, max_y, (2010, max_y))
    ev_type = st.radio("EV Type", ["All","BEV","PHEV"], horizontal=True)

    st.markdown('<div style="height:1px;background:#1E1E2A;margin:.75rem 1.2rem;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="padding:0 1.2rem;"><div style="color:#6B6B80;font-size:.62rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.6rem;">Map Style</div></div>', unsafe_allow_html=True)
    map_choice = st.radio("Map theme", ["🌑 Dark","☀️ Light","🛰️ Street"], label_visibility="collapsed")
    MAP_STYLES = {"🌑 Dark":"carto-darkmatter","☀️ Light":"carto-positron","🛰️ Street":"open-street-map"}
    map_style = MAP_STYLES[map_choice]

    st.markdown('<div style="height:1px;background:#1E1E2A;margin:.75rem 1.2rem;"></div>', unsafe_allow_html=True)
    with st.expander("⚙️  Chart appearance"):
        chart_scale = st.selectbox("Color scale", list(SCALES.keys()), index=0)
        chart_h = st.slider("Chart height", 300, 700, 430, step=10)

# ── Apply global filters ───────────────────────────────────────────────────────
df = df_raw.copy()
if sel_county:  df = df[df['County'].isin(sel_county)]
df = df[(df['Model Year'] >= yr[0]) & (df['Model Year'] <= yr[1])]
if ev_type == "BEV":  df = df[df['Electric Vehicle Type'].str.contains('BEV', na=False)]
elif ev_type == "PHEV": df = df[df['Electric Vehicle Type'].str.contains('PHEV', na=False)]

scale = SCALES[chart_scale]

# ── Page header ────────────────────────────────────────────────────────────────
bev_n  = int(df['Electric Vehicle Type'].str.contains('BEV',  na=False).sum())
phev_n = int(df['Electric Vehicle Type'].str.contains('PHEV', na=False).sum())
zip_n  = df['Postal Code'].nunique()
cty_n  = df['County'].nunique()
city_n = df['City'].nunique()
avg_rng = df[df['Electric Range']>10]['Electric Range'].mean()

pct_bev = bev_n / max(len(df),1) * 100

st.markdown(f"""
<div style="display:flex;align-items:flex-start;justify-content:space-between;margin:1.5rem 0 1.75rem;">
    <div>
        <div style="color:#6B6B80;font-size:.62rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:.3rem;">Real-time Analytics</div>
        <h1 style="color:#EAEAF0;font-size:1.85rem;font-weight:900;margin:0;letter-spacing:-.5px;line-height:1.1;">EV Analytics Dashboard</h1>
        <p style="color:#6B6B80;margin:.3rem 0 0;font-size:.85rem;">Washington State &nbsp;·&nbsp; <strong style="color:#CCFF00;">{len(df):,}</strong> vehicles &nbsp;·&nbsp; {ev_type} filtered</p>
    </div>
    <div style="display:flex;align-items:center;gap:.5rem;background:#0E0E14;border:1px solid #1E1E2A;border-radius:12px;padding:.55rem 1rem;font-size:.75rem;color:#6B6B80;margin-top:.25rem;">
        <span style="width:7px;height:7px;border-radius:50%;background:#2DD4BF;box-shadow:0 0 8px #2DD4BF;display:inline-block;flex-shrink:0;"></span>
        Live · {datetime.now().strftime('%b %d, %Y')}
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5,k6 = st.columns(6)
with k1: st.metric("⚡ Total EVs",   f"{len(df):,}")
with k2: st.metric("🔋 BEV",         f"{bev_n:,}",  delta=f"{pct_bev:.0f}% of fleet")
with k3: st.metric("🔌 PHEV",        f"{phev_n:,}")
with k4: st.metric("🏙️ Cities",      f"{city_n:,}")
with k5: st.metric("🗺️ Counties",    f"{cty_n:,}")
with k6: st.metric("⚡ Avg Range",   f"{avg_rng:.0f} mi" if not pd.isna(avg_rng) else "N/A")

st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)

# ── Dynamic Summary ───────────────────────────────────────────────────────────
# Generate insights based on current filters
if len(df) > 0:
    # Top insights
    top_county = df['County'].value_counts().idxmax() if not df['County'].isna().all() else "N/A"
    top_make = df['Make'].value_counts().idxmax() if not df['Make'].isna().all() else "N/A"
    year_range = f"{yr[0]}-{yr[1]}" if yr[0] != yr[1] else str(yr[0])
    county_count = len(sel_county) if sel_county else "all"
    
    insight_text = f"""
    **Dynamic Insight:** You're currently analyzing **{len(df):,}** electric vehicles 
    from **{county_count}** counties, focusing on model years **{year_range}**. 
    The data reveals that **{top_county}** has the highest concentration of EVs in your selection, 
    with **{top_make}** being the most popular make. 
    This represents **{pct_bev:.1f}%** battery electric vehicles in the filtered dataset.
    """
    
    st.info(insight_text)
    report_bytes, report_mime = generate_dashboard_report(df, sel_county, yr, ev_type)
    if report_mime == "application/pdf":
        st.download_button(
            label="⬇ Download Dashboard Report",
            data=report_bytes,
            file_name="ev_dashboard_report.pdf",
            mime=report_mime,
            use_container_width=False,
        )
    else:
        st.download_button(
            label="⬇ Download Dashboard Report (text fallback)",
            data=report_bytes,
            file_name="ev_dashboard_report.txt",
            mime=report_mime,
            use_container_width=False,
        )
else:
    st.warning("No data matches your current filter criteria. Try adjusting the filters above.")

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1 — MAP  +  COUNTY BAR
# ══════════════════════════════════════════════════════════════════════════════
col_map, col_county = st.columns([6,4], gap="medium")

with col_map:
    section("EV Registration Hotspots")
    mc1, mc2, mc3, mc4, mc5 = st.columns([2, 1, 2, 2, 2])
    with mc1:
        map_color_by = st.selectbox("Color by", ["EV Type","Make","Model Year"], key="map_col", label_visibility="collapsed")
    with mc2:
        map_opacity = st.slider("Opacity", 0.2, 1.0, 0.65, 0.05, key="map_op", label_visibility="collapsed")
    with mc3:
        map_sample = st.slider("Max points (k)", 5, 50, 25, 5, key="map_samp", label_visibility="collapsed")
    with mc4:
        map_zoom = st.slider("Zoom level", 4, 12, 6, key="map_zoom", label_visibility="collapsed",
                              help="4 = whole state, 10 = city level")
    with mc5:
        pt_size = st.slider("Point size", 2, 12, 5, key="pt_sz", label_visibility="collapsed")

    color_col_map = {
        "EV Type":    "Electric Vehicle Type",
        "Make":       "Make",
        "Model Year": "Model Year",
    }
    color_col = color_col_map[map_color_by]

    with st.spinner("Rendering map…"):
        df_coords = load_main().copy()
        if sel_county: df_coords = df_coords[df_coords['County'].isin(sel_county)]
        df_coords = df_coords[(df_coords['Model Year']>=yr[0])&(df_coords['Model Year']<=yr[1])]
        if ev_type=="BEV":  df_coords = df_coords[df_coords['Electric Vehicle Type'].str.contains('BEV',na=False)]
        elif ev_type=="PHEV": df_coords = df_coords[df_coords['Electric Vehicle Type'].str.contains('PHEV',na=False)]
        parsed = df_coords['Vehicle Location'].dropna().str.extract(r'POINT \(([^ ]+) ([^)]+)\)')
        if not parsed.empty:
            parsed.columns=['lon','lat']; parsed=parsed.astype(float)
            df_coords = df_coords.join(parsed)
            valid = df_coords.dropna(subset=['lat','lon'])
            samp = valid.sample(n=min(map_sample*1000, len(valid)), random_state=42)
            # Auto-center on selection
            center_lat = samp['lat'].mean() if sel_county else 47.5
            center_lon = samp['lon'].mean() if sel_county else -120.5
            is_dark = "dark" in map_style or "matter" in map_style
            fig_map = px.scatter_mapbox(
                samp, lat='lat', lon='lon',
                color=color_col,
                color_discrete_sequence=['#CCFF00','#2DD4BF','#FF6B35','#2DD4BF','#FF6B35'],
                color_continuous_scale='Viridis' if color_col=="Model Year" else None,
                zoom=map_zoom, center={"lat": center_lat, "lon": center_lon},
                mapbox_style=map_style,
                hover_data=['County','Make','Model'],
                opacity=map_opacity, size_max=pt_size,
            )
            fig_map.update_layout(
                paper_bgcolor="#0A0D14" if is_dark else "#EAEAF0",
                font_color="#B0B0C0" if is_dark else "#1E1E2A",
                margin=dict(l=0,r=0,t=10,b=0), height=500,
                legend=dict(bgcolor="rgba(10,13,20,.88)",bordercolor="#1E1E2A",borderwidth=1,font=dict(color="#B0B0C0",size=10)),
            )
            st.plotly_chart(fig_map, use_container_width=True, config={"scrollZoom": True})
        else:
            st.info("No location data available for current filter.")

with col_county:
    section("Counties")
    cc1, cc2 = st.columns(2)
    with cc1:
        top_n_county = st.slider("Show top N", 5, 39, 15, key="cn", label_visibility="collapsed")
    with cc2:
        county_orient = st.radio("Orientation", ["Horizontal","Vertical"], key="co", horizontal=True, label_visibility="collapsed")

    cdata = df.groupby('County').size().reset_index(name='EV Count').nlargest(top_n_county,'EV Count')
    if county_orient == "Horizontal":
        fig_cty = px.bar(cdata, x='EV Count', y='County', orientation='h',
                         color='EV Count', color_continuous_scale=scale)
        fig_cty.update_layout(yaxis=dict(categoryorder='total ascending'), coloraxis_showscale=False)
    else:
        fig_cty = px.bar(cdata.sort_values('EV Count',ascending=False), x='County', y='EV Count',
                         color='EV Count', color_continuous_scale=scale)
        fig_cty.update_layout(xaxis=dict(tickangle=-35), coloraxis_showscale=False)
    dt(fig_cty, h=490)
    st.plotly_chart(fig_cty, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 2 — ADOPTION TREND (full width, interactive)
# ══════════════════════════════════════════════════════════════════════════════
section("EV Adoption Trend")
ac1, ac2, ac3, ac4 = st.columns([2,2,2,2])
with ac1:
    adopt_mode = st.radio("View", ["Annual + Cumulative","Annual only","Cumulative only"], key="am", label_visibility="collapsed")
with ac2:
    adopt_from = st.slider("From year", min_y, max_y-1, 2010, key="af", label_visibility="collapsed")
with ac3:
    smooth = st.checkbox("Smooth lines", value=False, key="sm")
with ac4:
    show_markers = st.checkbox("Show markers", value=True, key="mk")

yearly = df.groupby('Model Year').size().reset_index(name='Registrations')
yearly = yearly[yearly['Model Year']>=adopt_from].sort_values('Model Year')
yearly['Cumulative'] = yearly['Registrations'].cumsum()
mode_str = 'lines' + ('+markers' if show_markers else '')
lshape = 'spline' if smooth else 'linear'

fig_trend = go.Figure()
if adopt_mode in ("Annual + Cumulative","Annual only"):
    fig_trend.add_trace(go.Scatter(
        x=yearly['Model Year'], y=yearly['Registrations'],
        name='Annual', mode=mode_str,
        line=dict(color='#CCFF00', width=2.5, shape=lshape),
        marker=dict(size=6, color='#CCFF00'),
        fill='tozeroy', fillcolor='rgba(204,255,0,.07)',
    ))
if adopt_mode in ("Annual + Cumulative","Cumulative only"):
    fig_trend.add_trace(go.Scatter(
        x=yearly['Model Year'], y=yearly['Cumulative'],
        name='Cumulative', mode='lines',
        line=dict(color='#2DD4BF', width=2.5, dash='dot', shape=lshape),
        yaxis='y2',
    ))
    fig_trend.update_layout(
        yaxis2=dict(overlaying='y', side='right', gridcolor="#1E1E2A", zeroline=False,
                    title=dict(text="Cumulative", font=dict(color="#2DD4BF", size=10)),
                    tickfont=dict(color="#2DD4BF", size=10)),
    )
fig_trend.update_layout(hovermode='x unified', title=None)
dt(fig_trend, h=chart_h)
st.plotly_chart(fig_trend, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 3 — BEV vs PHEV stacked area  +  CAFV donut
# ══════════════════════════════════════════════════════════════════════════════
col_area, col_cafv = st.columns([3,2], gap="medium")

with col_area:
    section("BEV vs PHEV Over Time")
    ba1, ba2 = st.columns(2)
    with ba1: area_from = st.slider("From year", min_y, max_y-1, 2011, key="baf", label_visibility="collapsed")
    with ba2: area_pct = st.checkbox("Show as % share", value=False, key="bap")

    ydf = df[df['Model Year']>=area_from].copy()
    ydf['Type'] = ydf['Electric Vehicle Type'].apply(lambda x:'BEV' if 'BEV' in str(x) else 'PHEV')
    grp = ydf.groupby(['Model Year','Type']).size().reset_index(name='Count')
    if area_pct:
        tot = grp.groupby('Model Year')['Count'].transform('sum')
        grp['Count'] = grp['Count']/tot*100
    years = sorted(grp['Model Year'].unique())
    bev_d = grp[grp['Type']=='BEV'].set_index('Model Year')['Count']
    phev_d= grp[grp['Type']=='PHEV'].set_index('Model Year')['Count']

    fig_area = go.Figure()
    fig_area.add_trace(go.Scatter(x=years, y=[bev_d.get(y,0) for y in years], name='BEV',
        stackgroup='one', mode='lines', line=dict(color='#CCFF00',width=1.5), fillcolor='rgba(204,255,0,.3)'))
    fig_area.add_trace(go.Scatter(x=years, y=[phev_d.get(y,0) for y in years], name='PHEV',
        stackgroup='one', mode='lines', line=dict(color='#2DD4BF',width=1.5), fillcolor='rgba(45,212,191,.3)'))
    fig_area.update_layout(hovermode='x unified', yaxis_title="% share" if area_pct else "Registrations")
    dt(fig_area, h=chart_h)
    st.plotly_chart(fig_area, use_container_width=True)

with col_cafv:
    section("CAFV Eligibility")
    cafv_style = st.radio("Chart type", ["Donut","Bar"], key="cs", horizontal=True, label_visibility="collapsed")
    lmap = {
        'Clean Alternative Fuel Vehicle Eligible':'CAFV Eligible',
        'Not eligible due to low battery range':'Not Eligible',
        'Eligibility unknown as battery range has not been researched':'Unknown',
    }
    cafv = df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'].map(lmap).value_counts().reset_index()
    cafv.columns=['Status','Count']
    if cafv_style == "Donut":
        fig_cafv = px.pie(cafv, values='Count', names='Status', hole=.52,
                          color_discrete_sequence=['#2DD4BF','#FF6B35','#3A3A4E'])
        fig_cafv.update_traces(textfont=dict(color='#B0B0C0',size=11),
                                marker=dict(line=dict(color='#0A0D14',width=3)))
        fig_cafv.update_layout(paper_bgcolor="#0A0D14", font_color="#B0B0C0",
                                legend=dict(bgcolor="rgba(10,13,20,.9)",bordercolor="#1E1E2A",borderwidth=1),
                                height=chart_h, margin=dict(l=20,r=20,t=20,b=20))
    else:
        fig_cafv = px.bar(cafv, x='Status', y='Count',
                          color='Status', color_discrete_sequence=['#2DD4BF','#FF6B35','#3A3A4E'])
        fig_cafv.update_layout(showlegend=False)
        dt(fig_cafv, h=chart_h)
    st.plotly_chart(fig_cafv, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 4 — EV TYPE PIE  +  MAKES BAR
# ══════════════════════════════════════════════════════════════════════════════
col_pie, col_makes = st.columns(2, gap="medium")

with col_pie:
    section("EV Type Split")
    pie_style = st.radio("Style", ["Donut","Pie","Bar"], key="ps", horizontal=True, label_visibility="collapsed")
    counts = df['Electric Vehicle Type'].value_counts().reset_index()
    counts.columns=['Type','Count']
    counts['Type'] = counts['Type'].str.replace('Battery Electric Vehicle','BEV').str.replace('Plug-in Hybrid Electric Vehicle','PHEV')
    if pie_style in ("Donut","Pie"):
        fig_pie = px.pie(counts, values='Count', names='Type', hole=.5 if pie_style=="Donut" else 0,
                         color_discrete_sequence=['#CCFF00','#2DD4BF'])
        fig_pie.update_traces(textfont=dict(color='#B0B0C0',size=12),
                               marker=dict(line=dict(color='#0A0D14',width=3)))
        fig_pie.update_layout(paper_bgcolor="#0A0D14", font_color="#B0B0C0", height=chart_h,
                               legend=dict(bgcolor="rgba(10,13,20,.9)",bordercolor="#1E1E2A",borderwidth=1),
                               margin=dict(l=20,r=20,t=20,b=20))
    else:
        fig_pie = px.bar(counts, x='Type', y='Count', color='Type',
                         color_discrete_sequence=['#CCFF00','#2DD4BF'])
        fig_pie.update_layout(showlegend=False)
        dt(fig_pie, h=chart_h)
    st.plotly_chart(fig_pie, use_container_width=True)

with col_makes:
    section("Top EV Makes")
    pm1, pm2 = st.columns(2)
    with pm1: top_n_make = st.slider("Show top N", 3, 47, 12, key="mk2", label_visibility="collapsed")
    with pm2: make_orient = st.radio("Axis", ["Vertical","Horizontal"], key="mo", horizontal=True, label_visibility="collapsed")
    mdata = df.groupby('Make').size().reset_index(name='Count').nlargest(top_n_make,'Count')
    if make_orient == "Vertical":
        fig_make = px.bar(mdata.sort_values('Count',ascending=False), x='Make', y='Count',
                          color='Count', color_continuous_scale=scale)
        fig_make.update_layout(xaxis=dict(tickangle=-35),coloraxis_showscale=False)
    else:
        fig_make = px.bar(mdata, x='Count', y='Make', orientation='h',
                          color='Count', color_continuous_scale=scale)
        fig_make.update_layout(yaxis=dict(categoryorder='total ascending'),coloraxis_showscale=False)
    dt(fig_make, h=chart_h)
    st.plotly_chart(fig_make, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — TOP CITIES
# ══════════════════════════════════════════════════════════════════════════════
section("Top Cities by EV Registrations")
ci1, ci2, ci3 = st.columns([2,2,3])
with ci1: top_n_city = st.slider("Top N cities", 5, 50, 20, key="tc", label_visibility="collapsed")
with ci2: city_type = st.radio("Chart", ["Bar","Treemap"], key="ct", horizontal=True, label_visibility="collapsed")
with ci3: city_scale = st.selectbox("Color", list(SCALES.keys()), index=0, key="cs2", label_visibility="collapsed")

cdata2 = df.groupby('City').size().reset_index(name='EV Count').nlargest(top_n_city,'EV Count')
if city_type == "Bar":
    fig_city = px.bar(cdata2.sort_values('EV Count',ascending=False), x='City', y='EV Count',
                      color='EV Count', color_continuous_scale=SCALES[city_scale])
    fig_city.update_layout(xaxis=dict(tickangle=-40), coloraxis_showscale=False)
    dt(fig_city, h=chart_h)
else:
    fig_city = px.treemap(cdata2, path=['City'], values='EV Count',
                          color='EV Count', color_continuous_scale=SCALES[city_scale])
    fig_city.update_layout(paper_bgcolor="#0A0D14", font_color="#B0B0C0", height=chart_h,
                            margin=dict(l=0,r=0,t=10,b=0))
st.plotly_chart(fig_city, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — ELECTRIC RANGE DISTRIBUTION (BEV)
# ══════════════════════════════════════════════════════════════════════════════
section("Electric Range Distribution (BEV only)")
rd1, rd2, rd3 = st.columns([2,2,3])
with rd1: top_n_rng = st.slider("Top N makes", 3, 20, 8, key="rn", label_visibility="collapsed")
with rd2: rng_chart = st.radio("Chart", ["Box","Violin","Strip"], key="rc", horizontal=True, label_visibility="collapsed")
with rd3: rng_min = st.slider("Min range filter (mi)", 0, 100, 10, key="rm", label_visibility="collapsed")

bev_df = df[df['Electric Vehicle Type'].str.contains('BEV',na=False) & (df['Electric Range']>rng_min)].copy()
top_makes_rng = bev_df.groupby('Make').size().nlargest(top_n_rng).index.tolist()
bev_df = bev_df[bev_df['Make'].isin(top_makes_rng)]
PALETTE = ['#CCFF00','#2DD4BF','#FF6B35','#2DD4BF','#FF6B35','#FF6B35','#06B6D4','#8B5CF6','#EC4899','#14B8A6','#A855F7','#F97316']

if rng_chart == "Box":
    fig_rng = px.box(bev_df, x='Make', y='Electric Range', color='Make',
                     color_discrete_sequence=PALETTE, points="outliers")
elif rng_chart == "Violin":
    fig_rng = px.violin(bev_df, x='Make', y='Electric Range', color='Make',
                        color_discrete_sequence=PALETTE, box=True)
else:
    fig_rng = px.strip(bev_df, x='Make', y='Electric Range', color='Make',
                       color_discrete_sequence=PALETTE)
fig_rng.update_layout(showlegend=False, xaxis=dict(tickangle=-30),
                       yaxis=dict(title='Electric Range (mi)'))
dt(fig_rng, h=chart_h)
st.plotly_chart(fig_rng, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — MAKE × MODEL YEAR HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
section("Make × Model Year Registration Heatmap")
hm1, hm2 = st.columns([2,3])
with hm1: hm_n = st.slider("Top N makes", 3, 20, 10, key="hm", label_visibility="collapsed")
with hm2: hm_yr = st.slider("Year range", min_y, max_y, (2015, max_y), key="hmyr", label_visibility="collapsed")

hm_df = df[(df['Model Year']>=hm_yr[0])&(df['Model Year']<=hm_yr[1])]
top_hm = hm_df.groupby('Make').size().nlargest(hm_n).index.tolist()
hm_df = hm_df[hm_df['Make'].isin(top_hm)]
pivot = hm_df.groupby(['Make','Model Year']).size().reset_index(name='Count')
pivot_wide = pivot.pivot(index='Make', columns='Model Year', values='Count').fillna(0)

fig_hm = px.imshow(pivot_wide, color_continuous_scale='Blues',
                    labels=dict(x="Model Year",y="Make",color="Registrations"),
                    aspect="auto")
fig_hm.update_layout(paper_bgcolor="#0A0D14", plot_bgcolor="#0E0E14", font_color="#B0B0C0",
                      height=max(250, hm_n*36+60),
                      coloraxis_colorbar=dict(tickfont=dict(color="#B0B0C0"),title=dict(font=dict(color="#B0B0C0"))),
                      margin=dict(l=90,r=20,t=20,b=40))
fig_hm.update_xaxes(side="bottom", tickangle=-30, gridcolor="#1E1E2A")
fig_hm.update_yaxes(gridcolor="#1E1E2A")
st.plotly_chart(fig_hm, use_container_width=True)
