import streamlit as st
from datetime import datetime
import threading
from src.components.sidebar import render_sidebar

# ── Prometheus metrics (starts once per process on port 8502) ─────────────────
try:
    from prometheus_client import Counter, Histogram, start_http_server
    import prometheus_client

    _metrics_started = getattr(prometheus_client, "_ev_metrics_started", False)
    if not _metrics_started:
        query_counter = Counter(
            "ev_query_total", "Total user queries submitted"
        )
        chart_render_latency = Histogram(
            "ev_chart_render_latency_seconds",
            "Chart render latency in seconds",
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
        )
        agent_chain_duration = Histogram(
            "ev_agent_chain_duration_seconds",
            "LangGraph agent chain duration in seconds",
            buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0],
        )
        threading.Thread(
            target=start_http_server, args=(8502,), daemon=True
        ).start()
        prometheus_client._ev_metrics_started = True
        query_counter = prometheus_client.REGISTRY._names_to_collectors.get(
            "ev_query_total", query_counter
        )
    METRICS_AVAILABLE = True
except Exception:
    METRICS_AVAILABLE = False

st.set_page_config(
    layout="wide",
    page_title="EV Intelligence",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

:root {
    --bg: #08090F;
    --surface: #0D1117;
    --card: #111827;
    --border: #1A2236;
    --cyan: #00D4FF;
    --purple: #7C3AED;
    --pink: #F72585;
    --green: #10B981;
    --t1: #F1F5F9;
    --t2: #CBD5E1;
    --t3: #64748B;
    --t4: #334155;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .main, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* ── Remove ALL default Streamlit top padding ── */
.block-container {
    max-width: 1400px !important;
    padding: 0 2.5rem 3rem !important;
}

/* ── Hide default header and sidebar nav ── */
header[data-testid="stHeader"] {
    display: none !important;
}
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* ── Sidebar — tight, no wasted space ── */
[data-testid="stSidebar"] {
    background: #09101A !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}
/* Kill Streamlit's internal sidebar top padding */
[data-testid="stSidebarContent"] {
    padding-top: 0 !important;
}

/* ── Sidebar nav buttons — transparent ghost style ── */
div[data-testid="stSidebar"] .stButton {
    margin-bottom: 6px !important;
}
div[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: var(--t3) !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    padding: 0.55rem 0.9rem !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    text-align: left !important;
    width: 100% !important;
    box-shadow: none !important;
    letter-spacing: 0 !important;
    transition: all 0.15s ease !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0,212,255,0.07) !important;
    border-color: rgba(0,212,255,0.2) !important;
    color: var(--cyan) !important;
    transform: none !important;
    box-shadow: none !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 18px !important;
    padding: 1.25rem 1.5rem !important;
    transition: all 0.25s !important;
    position: relative; overflow: hidden;
}
[data-testid="stMetric"]::after {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--purple), var(--cyan));
}
[data-testid="stMetric"]:hover {
    border-color: rgba(0,212,255,0.3) !important;
    box-shadow: 0 0 24px rgba(0,212,255,0.08), 0 8px 32px rgba(0,0,0,0.3) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricValue"] { color: var(--cyan) !important; font-size: 1.75rem !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { color: var(--t3) !important; font-size: 0.7rem !important; font-weight: 700 !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.4); }
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar()
    
    # Dataset stats
    st.markdown(f"""
    <div style="padding:0 1.25rem;">
        <div style="color:#475569;font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.6rem;">Dataset</div>
        <div style="display:flex;flex-direction:column;gap:0.4rem;font-size:0.78rem;">
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#64748B;">Records</span><span style="color:#00D4FF;font-weight:600;">276,828</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#64748B;">State</span><span style="color:#00D4FF;font-weight:600;">Washington</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#64748B;">Updated</span><span style="color:#10B981;font-weight:600;">{datetime.now().strftime('%b %d, %Y')}</span>
            </div>
        </div>
    </div>
    <div style="height:1px;background:#1A2236;margin:0.75rem 1.25rem;"></div>
    <div style="padding:0.5rem 1.25rem 0;color:#334155;font-size:0.68rem;text-align:center;">Team 19 · EV Intelligence</div>
    """, unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    position:relative; overflow:hidden;
    background:linear-gradient(135deg,#0D0A1E 0%,#0A1628 50%,#0D1117 100%);
    border:1px solid #1A2236; border-radius:24px;
    padding:4rem 3rem; margin:1.5rem 0 2rem; text-align:center;
">
    <div style="position:absolute;top:-80px;left:-80px;width:320px;height:320px;border-radius:50%;
                background:radial-gradient(circle,rgba(124,58,237,0.18) 0%,transparent 70%);pointer-events:none;"></div>
    <div style="position:absolute;bottom:-80px;right:-80px;width:360px;height:360px;border-radius:50%;
                background:radial-gradient(circle,rgba(0,212,255,0.12) 0%,transparent 70%);pointer-events:none;"></div>
    <div style="position:relative;z-index:1;">
        <h1 style="color:#F1F5F9;font-size:3.25rem;font-weight:900;margin:0 0 0.75rem;
                   letter-spacing:-2px;line-height:1.1;">
            <span style="background:linear-gradient(90deg,#7C3AED,#00D4FF);
                         -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                         background-clip:text;">EV Intelligence</span><br/>Platform
        </h1>
        <p style="color:#64748B;font-size:1.05rem;margin:0 auto;max-width:500px;line-height:1.65;font-weight:400;">
            Real-time analytics, AI-powered insights, and interactive visualizations for Washington State electric vehicle data.
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── FEATURE CARDS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
.feat-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}
.feat-card {
    background: #0D1117;
    border: 1px solid #1A2236;
    border-radius: 16px;
    padding: 1.5rem 1.25rem 1.25rem;
    transition: all 0.2s ease;
    position: relative;
    overflow: hidden;
}
.feat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--c1, #7C3AED), var(--c2, #00D4FF));
}
.feat-card:hover {
    border-color: rgba(0,212,255,0.3);
    transform: translateY(-3px);
    box-shadow: 0 12px 32px rgba(0,0,0,0.4), 0 0 16px rgba(0,212,255,0.06);
}
.feat-badge {
    width: 40px; height: 40px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.15rem; margin-bottom: 0.85rem;
}
.feat-title { font-size: 0.9rem; font-weight: 700; color: #F1F5F9; margin-bottom: 0.35rem; }
.feat-desc  { font-size: 0.78rem; color: #64748B; line-height: 1.55; }
.feat-link  {
    display: inline-flex; align-items: center; gap: 0.25rem;
    margin-top: 0.85rem; color: #00D4FF; font-size: 0.74rem; font-weight: 600;
}
</style>
<div class="feat-grid">
    <div class="feat-card" style="--c1:#00D4FF;--c2:#10B981;">
        <div class="feat-badge" style="background:rgba(0,212,255,0.1);">📊</div>
        <div class="feat-title">Analytics Dashboard</div>
        <div class="feat-desc">County maps, adoption curves, make breakdowns — every chart has live controls.</div>
        <div class="feat-link">Open Dashboard →</div>
    </div>
    <div class="feat-card" style="--c1:#7C3AED;--c2:#00D4FF;">
        <div class="feat-badge" style="background:rgba(124,58,237,0.1);">🤖</div>
        <div class="feat-title">AI Chat</div>
        <div class="feat-desc">Ask anything — LangGraph agent with Pinecone RAG and llama3.2 running locally.</div>
        <div class="feat-link">Start Chatting →</div>
    </div>
    <div class="feat-card" style="--c1:#F72585;--c2:#7C3AED;">
        <div class="feat-badge" style="background:rgba(247,37,133,0.1);">⚡</div>
        <div class="feat-title">Charger Optimizer</div>
        <div class="feat-desc">K-Means clustering on 276k+ records to place charging stations. GeoJSON export.</div>
        <div class="feat-link">Optimize →</div>
    </div>
    <div class="feat-card" style="--c1:#10B981;--c2:#00D4FF;">
        <div class="feat-badge" style="background:rgba(16,185,129,0.1);">📈</div>
        <div class="feat-title">Forecasting</div>
        <div class="feat-desc">County-level EV growth predictions to 2030 using Prophet + ARIMA with confidence bands.</div>
        <div class="feat-link">View Forecast →</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── STATS ─────────────────────────────────────────────────────────────────────
st.markdown('<div style="color:#475569;font-size:0.65rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.75rem;">Platform Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total EV Records", "276,828",  delta="Washington State")
with c2: st.metric("Counties Covered", "39",        delta="All WA counties")
with c3: st.metric("EV Makes Tracked", "50+",       delta="Across all models")
with c4: st.metric("Cluster Segments", "4",         delta="K-Means analysis")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:3rem;padding:1.25rem 0;border-top:1px solid #1A2236;
            display:flex;align-items:center;justify-content:space-between;">
    <div style="color:#334155;font-size:0.75rem;">
        EV Intelligence Platform, Team 19
    </div>
    <div style="display:flex;align-items:center;gap:0.4rem;">
        <span style="width:6px;height:6px;border-radius:50%;background:#10B981;
                     box-shadow:0 0 7px #10B981;display:inline-block;"></span>
        <span style="color:#334155;font-size:0.72rem;">Systems operational</span>
    </div>
</div>
""", unsafe_allow_html=True)
