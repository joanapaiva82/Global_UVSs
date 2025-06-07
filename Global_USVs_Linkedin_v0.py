import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim
import time

# ─────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Global Survey USVs Map", layout="wide")

st.title("🌍 Global Survey USVs")
st.markdown("An interactive map of **Uncrewed Surface Vessels (USVs)** used for hydrographic, geophysical, and environmental survey.")

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
# Load and Geocode
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data_and_coords():
    # Load CSV
    try:
        df = pd.read_csv("Global_USVs_Linkedin.csv", encoding="utf-8")
    except:
        df = pd.read_csv("Global_USVs_Linkedin.csv", encoding="latin1")

    # Check for lat/lon
    if "Latitude" not in df.columns or "Longitude" not in df.columns:
        geolocator = Nominatim(user_agent="usv_map_geo")
        coords = {}
        for country in df["Country"].dropna().unique():
            try:
                loc = geolocator.geocode(country)
                coords[country] = (loc.latitude, loc.longitude) if loc else (None, None)
                time.sleep(1)  # be respectful to Nominatim
            except:
                coords[country] = (None, None)
        df["Latitude"] = df["Country"].map(lambda x: coords.get(x, (None, None))[0])
        df["Longitude"] = df["Country"].map(lambda x: coords.get(x, (None, None))[1])

    df = df.dropna(subset=["Latitude", "Longitude"])
    return df

df = load_data_and_coords()

# ─────────────────────────────────────────────────────────────
# Sidebar filters
# ─────────────────────────────────────────────────────────────
st.sidebar.header("🔎 Filter")
countries = sorted(df["Country"].unique())
selected_country = st.sidebar.selectbox("Select a country", ["🌍 Show All"] + countries)

# Filter dataset
if selected_country != "🌍 Show All":
    df_filtered = df[df["Country"] == selected_country]
    map_lat = df_filtered["Latitude"].mean()
    map_lon = df_filtered["Longitude"].mean()
    map_zoom = 3.5
else:
    df_filtered = df
    map_lat, map_lon, map_zoom = 10, 0, 1.2

# ─────────────────────────────────────────────────────────────
# Map
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
            "ScatterplotLayer",
            data=df_filtered,
            get_position='[Longitude, Latitude]',
            get_fill_color='[30, 144, 255, 180]',
            get_radius=50000,
            pickable=True
        )
    ],
    tooltip={
        "html": """
        <b>{Name}</b><br>
        🏭 <b>Manufacturer:</b> {Manufacturer}<br>
        🌍 <b>Country:</b> {Country}<br>
        📏 <b>Length:</b> {`Max. Length (m)`} m
        """,
        "style": {"backgroundColor": "white", "color": "black"}
    }
))

# ─────────────────────────────────────────────────────────────
# Table and Jump-to-USV
# ─────────────────────────────────────────────────────────────
if selected_country != "🌍 Show All":
    st.subheader(f"📋 USVs in {selected_country}")
    usv_names = df_filtered["Name"].unique().tolist()
    selected_usv = st.selectbox("Jump to USV", ["—"] + usv_names)
    if selected_usv != "—":
        usv_row = df_filtered[df_filtered["Name"] == selected_usv].iloc[0]
        st.success(f"Focusing on **{usv_row['Name']}** – {usv_row['Manufacturer']}")
        st.map(pd.DataFrame([usv_row], columns=["Latitude", "Longitude"]))

    st.dataframe(df_filtered[["Name", "Manufacturer", "Max. Length (m)"]])

# Footer
st.markdown("---")
st.caption("📍 Joana Paiva | MSc Hydrography – University of Plymouth")
