import streamlit as st

st.set_page_config(
    layout="wide",
    page_title="Charger Optimizer",
    page_icon="⚡",
    initial_sidebar_state="expanded",
)

from src.pages.charger_optimizer import render
render()
