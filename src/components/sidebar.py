import streamlit as st
import os
from datetime import datetime

def render_sidebar():
    """Shared sidebar component for all pages. Renders logo, Docker badge, and Navigation."""
    is_docker = os.getenv("RUNNING_IN_DOCKER", "false").lower() == "true"
    
    # Logo block
    st.markdown(f"""
    <div style="
        padding: 1.25rem 1.25rem 1rem;
        border-bottom: 1px solid #1E1E2A;
    ">
        <div style="display:flex; align-items:center; gap:0.7rem;">
            <div style="
                width:36px; height:36px; border-radius:10px; flex-shrink:0;
                background: linear-gradient(135deg,#2DD4BF,#CCFF00);
                display:flex; align-items:center; justify-content:center;
                font-size:1.1rem; box-shadow:0 4px 12px rgba(45,212,191,0.4);
            ">⚡</div>
            <div>
                <div style="color:#EAEAF0;font-weight:700;font-size:0.9rem;line-height:1.2;">EV Intelligence</div>
                <div style="color:#3A3A4E;font-size:0.6rem;font-weight:600;letter-spacing:0.07em;text-transform:uppercase;">Platform v2.0</div>
            </div>
        </div>
        {f'''<div style="margin-top: 0.75rem; padding: 0.2rem 0.5rem; background: rgba(45, 212, 191, 0.1); border: 1px solid rgba(45, 212, 191, 0.2); border-radius: 6px; display: inline-flex; align-items: center; gap: 0.35rem;">
            <span style="width: 6px; height: 6px; border-radius: 50%; background: #2DD4BF; box-shadow: 0 0 5px #2DD4BF;"></span>
            <span style="color: #2DD4BF; font-size: 0.6rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">Running in Docker</span>
        </div>''' if is_docker else ''}
    </div>
    """, unsafe_allow_html=True)

    # Nav section
    st.markdown('<div style="padding:0.75rem 1.25rem 0.25rem;"><span style="color:#3A3A4E;font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;">Navigation</span></div>', unsafe_allow_html=True)

    if st.button("🏠  Home",             key="nav_home", use_container_width=True): st.switch_page("app.py")
    if st.button("📊  Dashboard",        key="nav_dash", use_container_width=True): st.switch_page("pages/1_Dashboard.py")
    if st.button("🤖  AI Chat",          key="nav_chat", use_container_width=True): st.switch_page("pages/2_Chat.py")
    if st.button("⚡  Charger Optimizer",key="nav_opt",  use_container_width=True): st.switch_page("pages/3_Charger_Optimizer.py")
    if st.button("📈  Forecasting",      key="nav_fore", use_container_width=True): st.switch_page("pages/4_Forecast.py")

    st.markdown('<div style="height:1px;background:#1E1E2A;margin:0.75rem 1.25rem;"></div>', unsafe_allow_html=True)
