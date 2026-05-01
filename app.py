import streamlit as st
from datetime import datetime

st.set_page_config(
    layout="wide",
    page_title="EV Intelligence",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

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

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, .main, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'Manrope', -apple-system, sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* Circuit-grid background */
[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed; top: 0; left: 0; right: 0; bottom: 0;
    background-image:
        radial-gradient(circle at 1px 1px, rgba(204,255,0,0.04) 1px, transparent 0);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
}

.block-container {
    max-width: 1380px !important;
    padding: 0 2.5rem 3rem !important;
    position: relative;
    z-index: 1;
}

header[data-testid="stHeader"] { display: none !important; }
[data-testid="stSidebarNav"] { display: none !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #0A0A10 !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebarContent"] { padding-top: 0 !important; }
section[data-testid="stSidebar"] > div > div > div > div {
    padding-top: 0 !important; gap: 0 !important;
}

/* Sidebar nav buttons */
div[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.03) !important;
    color: var(--t1) !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    padding: 0.75rem 1.1rem !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    font-family: 'Syne', sans-serif !important;
    letter-spacing: 0.03em !important;
    text-align: left !important;
    justify-content: flex-start !important;
    width: 100% !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
    margin-bottom: 12px !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: linear-gradient(90deg, rgba(204,255,0,0.1), rgba(45,212,191,0.05)) !important;
    border-color: rgba(204,255,0,0.3) !important;
    color: var(--volt) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4), 0 0 0 1px rgba(204,255,0,0.1) !important;
}
div[data-testid="stSidebar"] .stButton > button:active {
    transform: translateY(0) !important;
}

/* ── METRICS ── */
[data-testid="stMetric"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 1.2rem 1.4rem !important;
    transition: all 0.25s cubic-bezier(.4,0,.2,1) !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--volt), var(--ember));
}
[data-testid="stMetric"]:hover {
    border-color: rgba(204,255,0,0.25) !important;
    box-shadow: 0 0 20px rgba(204,255,0,0.06), 0 8px 30px rgba(0,0,0,0.35) !important;
    transform: translateY(-2px) !important;
}
[data-testid="stMetricValue"] {
    color: var(--volt) !important;
    font-size: 1.65rem !important;
    font-weight: 700 !important;
    font-family: 'IBM Plex Mono', monospace !important;
}
[data-testid="stMetricLabel"] {
    color: var(--t3) !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    font-family: 'Manrope', sans-serif !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(204,255,0,0.35); }

/* Staggered reveal animation */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="
        padding: 1.25rem 1.25rem 1rem;
        border-bottom: 1px solid #1E1E2A;
    ">
        <div style="display:flex; align-items:center; gap:0.7rem;">
            <div style="
                width:36px; height:36px; border-radius:8px; flex-shrink:0;
                background: linear-gradient(135deg,#CCFF00,#2DD4BF);
                display:flex; align-items:center; justify-content:center;
                font-size:1rem; box-shadow:0 4px 14px rgba(204,255,0,0.3);
            ">⚡</div>
            <div>
                <div style="color:#EAEAF0;font-weight:700;font-size:0.88rem;line-height:1.2;font-family:'Syne',sans-serif;">EV Intelligence</div>
                <div style="color:#6B6B80;font-size:0.58rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;font-family:'IBM Plex Mono',monospace;">Platform v2.0</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="padding:0.75rem 1.25rem 0.25rem;"><span style="color:#6B6B80;font-size:0.58rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;font-family:\'IBM Plex Mono\',monospace;">Navigation</span></div>', unsafe_allow_html=True)

    if st.button("◈  Home",      key="nav_home", use_container_width=True): st.switch_page("app.py")
    if st.button("▣  Dashboard", key="nav_dash", use_container_width=True): st.switch_page("pages/1_Dashboard.py")
    if st.button("◉  AI Chat",   key="nav_chat", use_container_width=True): st.switch_page("pages/2_Chat.py")

    st.markdown(f"""
    <div style="height:1px;background:#1E1E2A;margin:0.75rem 1.25rem;"></div>
    <div style="padding:0 1.25rem;">
        <div style="color:#6B6B80;font-size:0.58rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.6rem;font-family:'IBM Plex Mono',monospace;">Dataset</div>
        <div style="display:flex;flex-direction:column;gap:0.4rem;font-size:0.78rem;">
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#6B6B80;">Records</span><span style="color:#CCFF00;font-weight:600;font-family:'IBM Plex Mono',monospace;">276,828</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#6B6B80;">State</span><span style="color:#CCFF00;font-weight:600;">Washington</span>
            </div>
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#6B6B80;">Updated</span><span style="color:#2DD4BF;font-weight:600;font-family:'IBM Plex Mono',monospace;">{datetime.now().strftime('%b %d, %Y')}</span>
            </div>
        </div>
    </div>
    <div style="height:1px;background:#1E1E2A;margin:0.75rem 1.25rem;"></div>
    <div style="padding:0.5rem 1.25rem 0;color:#3A3A4E;font-size:0.68rem;text-align:center;font-family:'IBM Plex Mono',monospace;">Team 19 · EV Intelligence</div>
    """, unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown('<div style="position:relative;overflow:hidden;background:linear-gradient(145deg,#0C0C12 0%,#0A0E16 40%,#0E0D10 100%);border:1px solid #1E1E2A;border-radius:20px;padding:4.5rem 3rem;margin:1.5rem 0 2rem;text-align:center;">'
    '<div style="position:absolute;top:-60px;left:-40px;width:280px;height:280px;border-radius:50%;background:radial-gradient(circle,rgba(204,255,0,0.08) 0%,transparent 70%);pointer-events:none;"></div>'
    '<div style="position:absolute;bottom:-60px;right:-40px;width:300px;height:300px;border-radius:50%;background:radial-gradient(circle,rgba(45,212,191,0.06) 0%,transparent 70%);pointer-events:none;"></div>'
    '<div style="position:relative;z-index:1;">'
    '<div style="display:inline-flex;align-items:center;gap:0.5rem;background:rgba(204,255,0,0.06);border:1px solid rgba(204,255,0,0.15);border-radius:100px;padding:0.3rem 1rem;margin-bottom:1.5rem;">'
    '<span style="width:6px;height:6px;border-radius:50%;background:#CCFF00;box-shadow:0 0 10px #CCFF00;display:inline-block;flex-shrink:0;"></span>'
    '<span style="color:#CCFF00;font-size:0.7rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;font-family:IBM Plex Mono,monospace;">Live Washington State Data</span>'
    '</div>'
    '<h1 style="color:#EAEAF0;font-size:3.5rem;font-weight:800;margin:0 0 0.75rem;letter-spacing:-2.5px;line-height:1.05;font-family:Syne,sans-serif;">'
    '<span style="background:linear-gradient(90deg,#CCFF00,#2DD4BF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;">EV Intelligence</span><br/>Platform</h1>'
    '<p style="color:#6B6B80;font-size:1rem;margin:0 auto;max-width:520px;line-height:1.7;font-weight:400;">Real-time analytics, AI-powered policy insights, and interactive visualizations for Washington State electric vehicle registration data.</p>'
    '</div></div>', unsafe_allow_html=True)


# ── FEATURE CARDS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
.feat-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1.25rem; margin-bottom:2rem; }
.feat-card {
    background:#0E0E14; border:1px solid #1E1E2A; border-radius:16px;
    padding:1.75rem; transition:all 0.3s cubic-bezier(0.4,0,0.2,1);
    position:relative; overflow:hidden;
    animation: fadeSlideUp 0.6s ease-out backwards;
}
.feat-card:nth-child(1) { animation-delay: 0.1s; }
.feat-card:nth-child(2) { animation-delay: 0.2s; }
.feat-card:nth-child(3) { animation-delay: 0.3s; }
.feat-card:hover {
    border-color: rgba(204,255,0,0.3);
    transform: translateY(-4px);
    box-shadow: 0 16px 40px rgba(0,0,0,0.5), 0 0 20px rgba(204,255,0,0.04);
}
.feat-badge {
    width:44px;height:44px;border-radius:10px;display:flex;align-items:center;
    justify-content:center;font-size:1.3rem;margin-bottom:1rem;
}
.feat-title { font-size:1rem;font-weight:700;color:#EAEAF0;margin-bottom:0.45rem;font-family:'Syne',sans-serif; }
.feat-desc  { font-size:0.84rem;color:#6B6B80;line-height:1.65; }
.feat-link  { display:inline-flex;align-items:center;gap:0.3rem;margin-top:1rem;
              color:#CCFF00;font-size:0.76rem;font-weight:600;letter-spacing:0.02em;
              font-family:'IBM Plex Mono',monospace; }
</style>
<div class="feat-grid">
    <div class="feat-card">
        <div class="feat-badge" style="background:rgba(204,255,0,0.08);">📊</div>
        <div class="feat-title">Interactive Dashboard</div>
        <div class="feat-desc">Explore EV hotspots, adoption curves, and county-level breakdowns with live Plotly charts and global filters.</div>
        <div class="feat-link">Open Dashboard →</div>
    </div>
    <div class="feat-card">
        <div class="feat-badge" style="background:rgba(45,212,191,0.08);">◉</div>
        <div class="feat-title">AI Assistant</div>
        <div class="feat-desc">Ask questions naturally — backed by Pinecone vector search + llama3.2 running locally via Ollama RAG pipeline.</div>
        <div class="feat-link">Start Chatting →</div>
    </div>
    <div class="feat-card">
        <div class="feat-badge" style="background:rgba(255,107,53,0.08);">⚡</div>
        <div class="feat-title">Real-time Insights</div>
        <div class="feat-desc">276,000+ vehicle registrations across all WA counties with K-Means cluster analysis and range statistics.</div>
        <div class="feat-link">View Data →</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── STATS ─────────────────────────────────────────────────────────────────────
st.markdown('<div style="color:#6B6B80;font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.75rem;font-family:\'IBM Plex Mono\',monospace;">Platform Overview</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total EV Records", "276,828",  delta="Washington State")
with c2: st.metric("Counties Covered", "39",        delta="All WA counties")
with c3: st.metric("EV Makes Tracked", "50+",       delta="Across all models")
with c4: st.metric("Cluster Segments", "4",         delta="K-Means analysis")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:3rem;padding:1.25rem 0;border-top:1px solid #1E1E2A;
            display:flex;align-items:center;justify-content:space-between;">
    <div style="color:#3A3A4E;font-size:0.73rem;font-family:'IBM Plex Mono',monospace;">
        EV Intelligence Platform · Team 19
    </div>
    <div style="display:flex;align-items:center;gap:0.4rem;">
        <span style="width:6px;height:6px;border-radius:50%;background:#2DD4BF;
                     box-shadow:0 0 7px #2DD4BF;display:inline-block;"></span>
        <span style="color:#3A3A4E;font-size:0.72rem;font-family:'IBM Plex Mono',monospace;">Systems operational</span>
    </div>
</div>
""", unsafe_allow_html=True)
