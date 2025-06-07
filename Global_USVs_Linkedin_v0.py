import streamlit as st
import pandas as pd
import pydeck as pdk

# ─────────────────────────────────────────────────────────────
# Page setup
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="🌍 Global Survey USVs Map", layout="wide")

st.title("🌍 Global Survey USVs")
st.markdown("""
An interactive map showing **Uncrewed Surface Vessels (USVs)** used in the **hydrographic, geophysical, and environmental survey industry** around the world.
Hover over a marker to explore specs like **name, manufacturer, country, and length**.
""")

# ─────────────────────────────────────────────────────────────
# Disclaimer Section
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
# Data Loader with Encoding Fallback
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        return pd.read_csv("usv_map_data_ready.csv", encoding="utf-8")
    except UnicodeDecodeError:
        return pd.read_csv("usv_map_data_ready.csv", encoding="latin1")

df = load_data()

# ─────────────────────────────────────────────────────────────
# Interactive Map
# ─────────────────────────────────────────────────────────────
st.subheader("📍 Global USV Distribution Map")

map = pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=10,
        longitude=0,
        zoom=1.2,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=df,
            get_position='[Longitude, Latitude]',
            get_fill_color='[0, 105, 255, 180]',
            get_radius=50000,
            pickable=True,
        )
    ],
    tooltip={
        "html": """
        <b>{Name}</b><br>
        🏭 <b>Manufacturer:</b> {Manufacturer}<br>
        🌍 <b>Country:</b> {Country}<br>
        📏 <b>Length:</b> {`Max. Length (m)`} m
        """,
        "style": {
            "backgroundColor": "white",
            "color": "#000",
            "fontSize": "14px"
        }
    }
)

st.pydeck_chart(map)

# Footer
st.markdown("---")
st.caption("🛰️ Last updated as part of Joana Paiva's MSc Hydrography Dissertation – University of Plymouth.")
