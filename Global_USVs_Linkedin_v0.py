import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

st.set_page_config(page_title="Global Survey USVs", layout="wide")
st.title("🌍 Global Survey USVs Map")

# ─────────────────────────────────────────────────────────────
# Initialize session_state
# ─────────────────────────────────────────────────────────────
for key, default in {
    "selected_country": "🌍 Show All",
    "zoom_override": False,
    "rerun_trigger": False,
    "clear_filter_trigger": False
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────────────────────
# Safe rerun if clear_filter was triggered
# ─────────────────────────────────────────────────────────────
if st.session_state.clear_filter_trigger:
    st.session_state.clear_filter_trigger = False
    st.experimental_rerun()

# ─────────────────────────────────────────────────────────────
# Manufacturer Banner
# ─────────────────────────────────────────────────────────────
with st.expander("📌 Are you a USV manufacturer visiting this page? Please read this.", expanded=False):
    st.markdown("""
    Your USV platform may already be listed here based on publicly available information.

    To ensure your technology is **accurately and fairly represented**, I kindly invite you to confirm or contribute details such as:
    - Specifications
    - Sensor suite
    - Use cases and certifications

    📬 [joana.paiva82@outlook.com](mailto:joana.paiva82@outlook.com)
    """)

# ─────────────────────────────────────────────────────────────
# Disclaimer
# ─────────────────────────────────────────────────────────────
with st.expander("📌 Disclaimer (click to expand)"):
    st.markdown("""
    This dashboard is built from public sources to support an **MSc Hydrography dissertation** at the **University of Plymouth**.
    """)

# ─────────────────────────────────────────────────────────────
# Load and jitter data
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Global_USVs_Linkedin.csv")
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
    "width": 512, "height": 512, "anchorY": 512
} for _ in range(len(df))]

# ─────────────────────────────────────────────────────────────
# Filters + Buttons
# ─────────────────────────────────────────────────────────────
st.subheader("🔎 Explore by Country")

countries = ["🌍 Show All"] + sorted(df["Country"].unique())
selected = st.selectbox("Select a country", countries, index=countries.index(st.session_state.selected_country), key="selected_country")

btn1, btn2 = st.columns([0.15, 0.15])
with btn1:
    if st.button("🔍 Zoom to All"):
        st.session_state.zoom_override = True
with btn2:
    if st.button("🧹 Clear Filter"):
        st.session_state.update({
    "selected_country": "🌍 Show All"
})
        st.session_state.zoom_override = True
        st.session_state.clear_filter_trigger = True  # trigger full rerun

# ─────────────────────────────────────────────────────────────
# Filter data + determine zoom
# ─────────────────────────────────────────────────────────────
filtered_df = df if st.session_state.selected_country == "🌍 Show All" else df[df["Country"] == st.session_state.selected_country]

zoom_to_all = st.session_state.zoom_override or st.session_state.selected_country == "🌍 Show All"
map_center_lat = filtered_df["Latitude"].mean()
map_center_lon = filtered_df["Longitude"].mean()
map_zoom = 1.2 if zoom_to_all else 3.5

# ─────────────────────────────────────────────────────────────
# Map Display (with dynamic key)
# ─────────────────────────────────────────────────────────────
st.subheader("🗺️ USV Map")
st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v9",
        initial_view_state=pdk.ViewState(
            latitude=map_center_lat,
            longitude=map_center_lon,
            zoom=map_zoom
        ),
        layers=[
            pdk.Layer(
                "IconLayer",
                data=filtered_df,
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
    key="map_zoom_all" if zoom_to_all else "map_normal"
)

# Reset zoom after render
if st.session_state.zoom_override:
    st.session_state.zoom_override = False

# ─────────────────────────────────────────────────────────────
# Table View
# ─────────────────────────────────────────────────────────────
st.subheader("📋 Filtered USV List")
st.dataframe(filtered_df[["Name", "Manufacturer", "Country", "Max. Length (m)"]])

st.markdown("---")
st.caption("📍 MSc Hydrography Dissertation – Joana Paiva, University of Plymouth")
