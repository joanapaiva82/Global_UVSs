import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

# ─────────────────────────────────────────────────────────────
# Session Flags (Safe Init)
# ─────────────────────────────────────────────────────────────
for key, default in {
    "selected_country": "🌍 Show All",
    "zoom_override": False,
    "reset_dropdown": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Only Clear Filter should rerun the app
if st.session_state.reset_dropdown:
    st.session_state.reset_dropdown = False
    st.experimental_rerun()

# ─────────────────────────────────────────────────────────────
# Page Setup
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Global Survey USVs", layout="wide")
st.title("🌍 Global Survey USVs Map")

# ─────────────────────────────────────────────────────────────
# Manufacturer Banner (Preserved)
# ─────────────────────────────────────────────────────────────
with st.expander("📌 Are you a USV manufacturer visiting this page? Please read this.", expanded=False):
    st.markdown("""
    Your USV platform may already be listed here based on publicly available information.

    To ensure your technology is **accurately and fairly represented**, I kindly invite you to confirm or contribute additional details such as:

    - Technical specifications  
    - Sensor configurations  
    - Certifications and autonomy level  
    - Typical use cases and deployment examples

    📬 Please email me at **[joana.paiva82@outlook.com](mailto:joana.paiva82@outlook.com)**  
    I’ll send you a short form to review and update the displayed information.

    This supports the quality of my **MSc Hydrography dissertation** at the **University of Plymouth**, and ensures your platform is properly represented.
    """)

# ─────────────────────────────────────────────────────────────
# Disclaimer (Preserved)
# ─────────────────────────────────────────────────────────────
with st.expander("📌 Disclaimer (click to expand)"):
    st.markdown("""
    The information presented on this page has been compiled solely for **academic and research purposes** in support of a postgraduate dissertation in **MSc Hydrography at the University of Plymouth**.

    All specifications, features, and descriptions of Uncrewed Surface Vessels (USVs) are based on **publicly available sources** and **have not been independently verified**.

    **⚠️ This content is not intended to serve as an official or authoritative source.**  
    Do not rely on this data for operational, procurement, or technical decisions.  
    Please consult the original manufacturers for validated information.
    """)

# ─────────────────────────────────────────────────────────────
# Load + Jitter Data
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Global_USVs_Linkedin.csv", encoding="utf-8")
    return df.dropna(subset=["Latitude", "Longitude"])

def apply_jitter(df, jitter=0.8):
    output = []
    for country, group in df.groupby("Country"):
        n = len(group)
        if n == 1:
            output.append(group)
            continue
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        group = group.copy()
        group["Latitude"] += jitter * np.sin(angles)
        group["Longitude"] += jitter * np.cos(angles)
        output.append(group)
    return pd.concat(output, ignore_index=True)

df = apply_jitter(load_data())
df["icon_data"] = [{
    "url": "https://raw.githubusercontent.com/joanapaiva82/Global_UVSs/main/usv.png",
    "width": 512,
    "height": 512,
    "anchorY": 512
} for _ in range(len(df))]

# ─────────────────────────────────────────────────────────────
# Filter Controls (No assignment conflicts)
# ─────────────────────────────────────────────────────────────
st.subheader("🔎 Explore by Country")

countries = ["🌍 Show All"] + sorted(df["Country"].unique())
dropdown_index = 0 if st.session_state.selected_country == "🌍 Show All" else countries.index(st.session_state.selected_country)
selected_country = st.selectbox("Select a country", countries, index=dropdown_index)
st.session_state.selected_country = selected_country

# Buttons
col1, col2 = st.columns([0.15, 0.15])
with col1:
    if st.button("🔍 Zoom to All"):
        st.session_state.zoom_override = True
with col2:
    if st.button("🧹 Clear Filter"):
        st.session_state.selected_country = "🌍 Show All"
        st.session_state.zoom_override = True
        st.session_state.reset_dropdown = True

# ─────────────────────────────────────────────────────────────
# Filter Data + Zoom View Logic
# ─────────────────────────────────────────────────────────────
df_filtered = df if st.session_state.selected_country == "🌍 Show All" else df[df["Country"] == st.session_state.selected_country]
zoom_now = st.session_state.zoom_override or st.session_state.selected_country == "🌍 Show All"

map_lat = df_filtered["Latitude"].mean()
map_lon = df_filtered["Longitude"].mean()
map_zoom = 1.2 if zoom_now else 3.5

# ─────────────────────────────────────────────────────────────
# Render Map with Key to Force Reset
# ─────────────────────────────────────────────────────────────
st.subheader("🗺️ USV Map")
st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=map_lat,
            longitude=map_lon,
            zoom=map_zoom
        ),
        layers=[
            pdk.Layer(
                "IconLayer",
                data=df_filtered,
                get_icon="icon_data",
                get_position='[Longitude, Latitude]',
                size_scale=15,
                get_size=4,
                pickable=True
            )
        ],
        tooltip={
            "html": """
            <b>{Name}</b><br>
            🏭 <b>Manufacturer:</b> {Manufacturer}<br>
            🌍 <b>Country:</b> {Country}<br>
            📏 <b>Length:</b> {Max. Length (m)} m
            """,
            "style": {"backgroundColor": "white", "color": "black"}
        }
    ),
    key="map_zoom_all" if zoom_now else "map_normal"
)

# Reset zoom flag (but don’t trigger rerun)
if st.session_state.zoom_override:
    st.session_state.zoom_override = False

# ─────────────────────────────────────────────────────────────
# Table View
# ─────────────────────────────────────────────────────────────
st.subheader("📋 Filtered USV List")
st.dataframe(df_filtered[["Name", "Manufacturer", "Country", "Max. Length (m)"]])

st.markdown("---")
st.caption("📍 MSc Hydrography Dissertation – Joana Paiva, University of Plymouth")
