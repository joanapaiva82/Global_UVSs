import streamlit as st
import pandas as pd
import pydeck as pdk

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
# Load Preprocessed CSV with Coordinates
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("Global_USVs_Linkedin.csv", encoding="utf-8")
    return df

df = load_data()

# ─────────────────────────────────────────────────────────────
# Add Vessel Icon
# ─────────────────────────────────────────────────────────────
icon_url = "https://raw.githubusercontent.com/joanapaiva82/Global_UVSs/main/usv.png"
df["icon_data"] = [{
    "url": icon_url,
    "width": 512,
    "height": 512,
    "anchorY": 512
} for _ in range(len(df))]

# ─────────────────────────────────────────────────────────────
# Country Filter
# ─────────────────────────────────────────────────────────────
st.subheader("🔎 Select a country")
countries = sorted(df["Country"].dropna().unique())
selected_country = st.selectbox("Choose a country to explore", ["🌍 Show All"] + countries)

if selected_country != "🌍 Show All":
    df_table = df[df["Country"] == selected_country]
    map_lat = df_table["Latitude"].mean()
    map_lon = df_table["Longitude"].mean()
    map_zoom = 3.5
else:
    df_table = df
    map_lat = df["Latitude"].mean()
    map_lon = df["Longitude"].mean()
    map_zoom = 1.2

# ─────────────────────────────────────────────────────────────
# Map: USV Locations
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
