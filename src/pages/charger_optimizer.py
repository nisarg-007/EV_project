"""
Charger Placement Optimizer — Streamlit multipage module.
Run as: pages/3_Charger_Optimizer.py (symlinked or copied).
"""

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import time
from src.components.sidebar import render_sidebar
import json
import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium  # type: ignore
from sklearn.cluster import MiniBatchKMeans  # type: ignore

PARQUET_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "processed",
    "Electric_Vehicle_Population_Data.parquet"
)

# Washington State county approximate centroids (lat, lon)
COUNTY_CENTROIDS: dict[str, tuple[float, float]] = {
    "King": (47.49, -122.01), "Pierce": (47.04, -122.27),
    "Snohomish": (47.98, -121.98), "Clark": (45.77, -122.48),
    "Spokane": (47.66, -117.43), "Thurston": (47.00, -122.81),
    "Kitsap": (47.62, -122.64), "Whatcom": (48.84, -122.30),
    "Benton": (46.26, -119.31), "Yakima": (46.54, -120.51),
    "Skagit": (48.45, -121.89), "Cowlitz": (46.09, -122.70),
    "Grant": (47.22, -119.55), "Franklin": (46.50, -118.92),
    "Lewis": (46.55, -122.31), "Island": (48.17, -122.56),
    "Chelan": (47.84, -120.43), "Grays Harbor": (47.06, -123.81),
    "Mason": (47.35, -123.13), "Okanogan": (48.56, -119.62),
    "Walla Walla": (46.12, -118.36), "Clallam": (48.15, -124.01),
    "Jefferson": (47.88, -123.06), "San Juan": (48.55, -123.05),
    "Whitman": (46.87, -117.42), "Douglas": (47.74, -119.70),
    "Stevens": (48.34, -117.86), "Pend Oreille": (48.54, -117.32),
    "Lincoln": (47.57, -118.42), "Ferry": (48.66, -118.49),
    "Adams": (47.01, -118.56), "Asotin": (46.22, -117.17),
    "Columbia": (46.30, -118.00), "Garfield": (46.48, -117.49),
    "Wahkiakum": (46.29, -123.41), "Klickitat": (45.88, -120.79),
    "Skamania": (45.86, -121.91), "Pacific": (46.56, -123.82),
    "Kittitas": (47.19, -120.72),
}


@st.cache_data(ttl=3600)
def load_ev_data() -> pd.DataFrame:
    df = pd.read_parquet(PARQUET_PATH)
    df.columns = [c.strip() for c in df.columns]
    return df


def enrich_with_coords(df: pd.DataFrame) -> pd.DataFrame:
    """Attach centroid lat/lon per county (proxy for geospatial density)."""
    df = df.copy()
    df["lat"] = df["County"].map(lambda c: COUNTY_CENTROIDS.get(c, (None, None))[0])
    df["lon"] = df["County"].map(lambda c: COUNTY_CENTROIDS.get(c, (None, None))[1])
    # Add small jitter so clustering isn't trivial for same-county records
    rng = np.random.default_rng(42)
    df["lat"] += rng.normal(0, 0.15, len(df))
    df["lon"] += rng.normal(0, 0.20, len(df))
    return df.dropna(subset=["lat", "lon"])


def run_kmeans(df: pd.DataFrame, k: int) -> tuple[pd.DataFrame, np.ndarray]:
    t0 = time.perf_counter()
    X = df[["lat", "lon"]].values
    km = MiniBatchKMeans(n_clusters=k, random_state=42, batch_size=min(10_000, len(X)))
    labels = km.fit_predict(X)
    elapsed = time.perf_counter() - t0
    return km.cluster_centers_, labels, elapsed


def build_map(df: pd.DataFrame, centers: np.ndarray, labels: np.ndarray) -> folium.Map:
    fmap = folium.Map(location=[47.5, -120.5], zoom_start=7, tiles="CartoDB dark_matter")

    # Cluster heatmap layer
    county_counts = df.groupby("County").size().reset_index(name="count")
    for _, row in county_counts.iterrows():
        coords = COUNTY_CENTROIDS.get(row["County"])
        if coords:
            folium.CircleMarker(
                location=[float(coords[0]), float(coords[1])],
                radius=float(max(4, min(30, row["count"] / 500))),
                color="#00D4FF",
                fill=True,
                fill_color="#00D4FF",
                fill_opacity=0.35,
                popup=f"{row['County']} County: {row['count']:,} EVs",
                tooltip=f"{row['County']}: {row['count']:,}",
            ).add_to(fmap)

    # Cluster centroids — proposed charger locations
    for i, (lat, lon) in enumerate(centers):
        folium.Marker(
            location=[float(lat), float(lon)],
            icon=folium.DivIcon(
                html=(
                    '<div style="background:#7C3AED;color:white;border-radius:50%;'
                    'width:28px;height:28px;display:flex;align-items:center;'
                    'justify-content:center;font-size:14px;font-weight:bold;'
                    'box-shadow:0 0 8px rgba(124,58,237,.7);">⚡</div>'
                ),
                icon_size=(28, 28),
                icon_anchor=(14, 14),
            ),
            popup=f"Proposed Charger #{i+1}",
            tooltip=f"Cluster {i+1} centroid",
        ).add_to(fmap)

    return fmap


def evs_within_radius(df: pd.DataFrame, lat: float, lon: float, radius_mi: float = 10) -> int:
    R = 3958.8  # Earth radius in miles
    lat_r, lon_r = np.radians(lat), np.radians(lon)
    df_r = np.radians(df[["lat", "lon"]].values)
    dlat = df_r[:, 0] - lat_r
    dlon = df_r[:, 1] - lon_r
    a = np.sin(dlat / 2) ** 2 + np.cos(lat_r) * np.cos(df_r[:, 0]) * np.sin(dlon / 2) ** 2
    dist = 2 * R * np.arcsin(np.sqrt(a))
    return int((dist <= radius_mi).sum())


def centroids_to_geojson(centers: np.ndarray) -> dict:
    features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [lon, lat]},
            "properties": {"id": i + 1},
        }
        for i, (lat, lon) in enumerate(centers)
    ]
    return {"type": "FeatureCollection", "features": features}


# ── Streamlit page ─────────────────────────────────────────────────────────────

def render():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html,body,.main,[data-testid="stAppViewContainer"]{background:#08090F!important;font-family:'Inter',sans-serif!important;}
    .block-container{max-width:1400px!important;padding:0 2rem 3rem!important;}
    header[data-testid="stHeader"]{display:none!important;}
    [data-testid="stSidebarNav"]{display:none!important;}
    [data-testid="stSidebar"]{background:#09101A!important;border-right:1px solid #1A2236!important;}
    [data-testid="stSidebarContent"]{padding-top:0!important;}
    [data-testid="stMetricValue"]{color:#00D4FF!important;font-weight:800!important;}
    [data-testid="stMetricLabel"]{color:#64748B!important;font-size:0.7rem!important;text-transform:uppercase!important;letter-spacing:.08em!important;}
    [data-testid="stMetric"]{background:#111827!important;border:1px solid #1A2236!important;border-radius:16px!important;padding:1rem 1.25rem!important;}
    </style>
    """, unsafe_allow_html=True)

    # Sidebar nav
    with st.sidebar:
        render_sidebar()
        st.markdown('<div style="padding:0.75rem 1.25rem 0.25rem;"><span style="color:#475569;font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;">Simulation Controls</span></div>', unsafe_allow_html=True)

    # Page header
    st.markdown("""
    <div style="padding:1.75rem 0 1rem;">
        <h1 style="color:#F1F5F9;font-size:2rem;font-weight:800;margin:0 0 .3rem;letter-spacing:-.5px;">
            ⚡ Charger Placement Optimizer
        </h1>
        <p style="color:#64748B;font-size:.9rem;margin:0;">
            K-Means clustering on 276k+ EV registrations to identify optimal fast-charger locations across Washington State.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Controls
    col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([1, 1, 2])
    with col_ctrl1:
        k = st.slider("Charger Stations", min_value=5, max_value=100, value=20, step=5,
                      help="Number of proposed charger locations (cluster centroids)")
    with col_ctrl2:
        min_density = st.slider("Min EV Count Filter", min_value=0, max_value=5000, value=0, step=100,
                                help="Exclude counties with fewer EVs than this threshold")
    with col_ctrl3:
        all_counties = sorted(COUNTY_CENTROIDS.keys())
        selected_counties = st.multiselect("County Filter", options=all_counties,
                                           default=[], placeholder="All counties")

    # Load & filter data
    with st.spinner("Loading EV data…"):
        df_raw = load_ev_data()

    df = enrich_with_coords(df_raw)

    if selected_counties:
        df = df[df["County"].isin(selected_counties)]

    if min_density > 0:
        county_counts = df.groupby("County").size()
        valid_counties = county_counts[county_counts >= min_density].index
        df = df[df["County"].isin(valid_counties)]

    if len(df) < k:
        st.warning(f"Only {len(df):,} records after filtering — reduce k or loosen filters.")
        return

    # Run clustering
    t0 = time.perf_counter()
    centers, labels, elapsed = run_kmeans(df, k)
    elapsed_total = time.perf_counter() - t0

    # KPI row
    st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("EVs Analyzed", f"{len(df):,}")
    with m2: st.metric("Proposed Stations", k)
    with m3: st.metric("Counties Included", df["County"].nunique())
    with m4: st.metric("Optimizer Runtime", f"{elapsed_total:.2f}s")

    st.markdown("<div style='height:.75rem'></div>", unsafe_allow_html=True)
    c_list = "all counties" if not selected_counties else ", ".join(selected_counties)
    st.info(f"**Insight:** You are analyzing {len(df):,} EVs across {c_list} to find the {k} most optimal locations for new fast-chargers. The algorithm has placed these {k} stations at the center of the densest EV population clusters to minimize driving distance for the maximum number of EV owners.")

    # Map + What-if panel
    map_col, panel_col = st.columns([3, 1])

    with map_col:
        st.markdown('<div style="color:#94A3B8;font-size:.78rem;margin-bottom:.4rem;">Click any point on the map to run the What-If radius analysis.</div>', unsafe_allow_html=True)
        fmap = build_map(df, centers, labels)
        map_data = st_folium(fmap, use_container_width=True, height=520, key="optimizer_map")

    with panel_col:
        st.markdown("""
        <div style="background:#111827;border:1px solid #1A2236;border-radius:16px;padding:1.25rem;">
            <div style="color:#F1F5F9;font-weight:700;font-size:.9rem;margin-bottom:.75rem;">What-If Panel</div>
        """, unsafe_allow_html=True)

        clicked = map_data.get("last_clicked") if map_data else None
        if clicked:
            lat_c, lon_c = clicked["lat"], clicked["lng"]
            nearby = evs_within_radius(df, lat_c, lon_c, radius_mi=10)
            st.markdown(f"""
            <div style="margin-bottom:.6rem;">
                <div style="color:#64748B;font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;">Selected Location</div>
                <div style="color:#00D4FF;font-weight:600;font-size:.85rem;">{lat_c:.4f}, {lon_c:.4f}</div>
            </div>
            <div style="background:rgba(0,212,255,.07);border:1px solid rgba(0,212,255,.2);border-radius:10px;padding:.8rem;text-align:center;margin-bottom:0.8rem;">
                <div style="color:#64748B;font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;">EVs within 10 mi</div>
                <div style="color:#00D4FF;font-size:1.75rem;font-weight:800;">{nearby:,}</div>
            </div>
            <div style="color:#E2E8F0;font-size:.8rem;line-height:1.4;">
                <strong>Simulation Summary:</strong> If you build a new charging station at these exact coordinates, it will immediately serve <strong>{nearby:,}</strong> electric vehicles within a 10-mile radius based on current registrations.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="color:#475569;font-size:.8rem;text-align:center;padding:1rem 0;">
                Click a location on the map to see estimated EVs within 10-mile radius.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # GeoJSON export
        st.markdown("<div style='height:.5rem'></div>", unsafe_allow_html=True)
        geojson_data = json.dumps(centroids_to_geojson(centers), indent=2)
        st.download_button(
            label="⬇ Export Locations (GeoJSON)",
            data=geojson_data,
            file_name="proposed_charger_locations.geojson",
            mime="application/geo+json",
            use_container_width=True,
        )

    # Cluster summary table
    with st.expander("Cluster Summary", expanded=False):
        cluster_df = df.copy()
        cluster_df["cluster"] = labels
        summary = (
            cluster_df.groupby("cluster")
            .agg(ev_count=("County", "count"), top_make=("Make", lambda x: x.mode()[0] if len(x) else "N/A"))
            .reset_index()
        )
        summary["centroid_lat"] = centers[summary["cluster"], 0].round(4)
        summary["centroid_lon"] = centers[summary["cluster"], 1].round(4)
        summary.columns = ["Cluster", "EV Count", "Top Make", "Centroid Lat", "Centroid Lon"]
        st.dataframe(summary, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    render()
