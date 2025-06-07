import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

# ─────────────────────────────────────────────────────────────
# Handle rerun triggered by "Clear Filter"
# ─────────────────────────────────────────────────────────────
if "rerun" in st.session_state and st.session_state.rerun:
    st.session_state.rerun = False
    st.experimental_rerun()

# ─────────────────────────────────────────────────────────────
# Page Setup
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Global Survey USVs", layout="wide")
st.title("🌍 Global Survey USVs Map")
st.markdown("Visualize Uncrewed Surface Vessels (USVs) used for hydrographic and geophysical survey — by country and manufacturer.")

# ─────────────────────────────────────────────────────────────
# Disclaimer
# ─────────────────────────────────────────────────────────────
with st.expander("📌 Disclaimer (click to expand)"):
    st.markdown("""
    The information presented on this page has been compiled solely for **academic and research purposes** in support of a postgraduate dissertation in **MSc Hydrography at the University of Plymouth**.

    All specifications, features, and descriptions of Uncrewed Surface Vessels (USVs) are based on **publicly available sources** and **have not been independently verified**.

    **⚠️ This content is not intended to serve as an official or authoritative source.**  
    Do not rely on this data for operational, procurement, or technical decisions.  
    Please consult the original manufacturers for validated information.

    ---
    **Author:** Joana Paiva  
    **Email:** [joana.paiva82@outlook.com](mailto:joana.paiva82@outlook.com)
    """)

# ─────────────────────────────────────────────────────────────
# Load Data and Apply Jitter
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Global_USVs_Linkedin.csv", encoding="utf-8")
    df = df.dropna(subset=["Latitude", "Longitude"])
    return df

df_raw = load_data()

def apply_jitter(df, jitter_amount=0.8):
    jittered = []
    for country, group in df.groupby("Country"):
        count = len(group)
        if count == 1:
            jittered.append(group)
            continue
        angles = np.linspace(0, 2 * np.pi, count, endpoint=False)
        lat_offsets = jitter_amount * np.sin(angles)
        lon_offsets = jitter_amount * np.cos(angles)
        group = group.copy()
        group["Latitude"] += lat_offsets
        group["Longitude"] += lon_offsets
        jittered.append(group)
    return pd.concat(jittered, ignore_index=True)

df = apply_jitter(df_raw)

# Add vessel icon
icon_url = "https://raw.githubusercontent.com/joanapaiva82/Global_UVSs/main/usv.png"
df["icon_data"] = [{
    "url": icon_url,
    "width": 512,
    "height": 512,
    "anchorY": 512
} for _ in range(len(df))]

# ─────────────────────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────────────────────
if "selected_country" not in st.session_state:
    st.session_state.selected_country = "🌍 Show All"
if "zoom_override" not in st.session_state:
    st.session_state.zoom_override = False

# ─────────────────────────────────────────────────────────────
# Filter Controls
# ─────────────────────────────────────────────────────────────
st.subheader("🔎 Explore by Country")

# Dropdown
selected_country = st.selectbox(
    "Select a country",
    ["🌍 Show All"] + sorted(df["Country"].unique()),
    index=(0 if st.session_state.selected_country == "🌍 Show All"
           else sorted(df["Country"].unique()).index(st.session_state.selected_country) + 1)
)

# Update session state with selection
st.session_state.selected_country = selected_country

# Buttons side-by-side
btn_col1, btn_col2 = st.columns([0.15, 0.15])
with btn_col1:
    if st.button("🔍 Zoom to All"):
        st.session_state.zoom_override = True

with btn_col2:
    if st.button("🧹 Clear Filter"):
        st.session_state.selected_country = "🌍 Show All"
        st.session_state.zoom_override = True
        st.session_state.rerun = True  # safe trigger
        st.stop()  # pause execution until rerun happens

# ─────────────────────────────────────────────────────────────
# Filter and Map View
# ─────────────────────────────────────────────────────────────
df_table = df if st.session_state.selected_country == "🌍 Show All" else df[df["Country"] == st.session_state.selected_country]
map_lat = df_table["Latitude"].mean()
map_lon = df_table["Longitude"].mean()
map_zoom = 1.2 if st.session_state.zoom_override or st.session_state.selected_country == "🌍 Show All" else 3.5

# ─────────────────────────────────────────────────────────────
# Map Display
# ─────────────────────────────────────────────────────────────
st.subheader("🗺️ USV Map")
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=map_lat,
        longitude=map_lon,
        zoom=map_zoom,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "IconLayer",
            data=df_table,
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
))

# ─────────────────────────────────────────────────────────────
# Data Table
# ─────────────────────────────────────────────────────────────
st.subheader("📋 Filtered USV List")
st.dataframe(df_table[["Name", "Manufacturer", "Country", "Max. Length (m)"]])

st.markdown("---")
st.caption("📍 MSc Hydrography Dissertation – Joana Paiva, University of Plymouth")
