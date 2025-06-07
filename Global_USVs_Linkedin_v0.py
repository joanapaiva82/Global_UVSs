import streamlit as st
import pandas as pd
import pydeck as pdk
from geopy.geocoders import Nominatim
import numpy as np
import time

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
# Load + Geocode + Safe Merge
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data_and_centroids():
    try:
        df = pd.read_csv("Global_USVs_Linkedin.csv", encoding="utf-8")
    except:
        df = pd.read_csv("Global_USVs_Linkedin.csv", encoding="latin1")

    # Normalize common country names
    country_fix = {
        "UK": "United Kingdom",
        "USA": "United States",
        "UAE": "United Arab Emirates",
        "Russia": "Russian Federation"
    }
    df["Country"] = df["Country"].replace(country_fix)

    # Geocode unique countries
    geolocator = Nominatim(user_agent="usv_geocoder")
    coords = {}
    for country in df["Country"].dropna().unique():
        try:
            loc = geolocator.geocode(country)
            coords[country] = (loc.latitude, loc.longitude) if loc else (None, None)
            time.sleep(1)
        except:
            coords[country] = (None, None)

    # Build lookup DataFrame
    coord_df = pd.DataFrame.from_dict(coords, orient="index", columns=["Latitude", "Longitude"])
    coord_df = coord_df.reset_index().rename(columns={"index": "Country"})

    # Merge with original DataFrame safely
    df = df.merge(coord_df, on="Country", how="left")
    centroids = {row["Country"]: (row["Latitude"], row["Longitude"]) for _, row in coord_df.iterrows() if pd.notnull(row["Latitude"])}

    return df.dropna(subset=["Latitude", "Longitude"]), centroids

df_raw, country_centroids = load_data_and_centroids()

# ─────────────────────────────────────────────────────────────
# Apply jitter for USVs per country
# ─────────────────────────────────────────────────────────────
def jitter_data(df, jitter=1.5):
    df = df.copy()
    lat_list, lon_list = [], []
    grouped = df.groupby("Country")

    for _, group in grouped:
        count = len(group)
        angles = np.linspace(0, 2 * np.pi, count, endpoint=False)
        lat_offsets = jitter * np.sin(angles)
        lon_offsets = jitter * np.cos(angles)

        lat_list.extend(group["Latitude"].values + lat_offsets)
        lon_list.extend(group["Longitude"].values + lon_offsets)

    df["Latitude"] = lat_list
    df["Longitude"] = lon_list
    return df

df = jitter_data(df_raw)

# ─────────────────────────────────────────────────────────────
# Add your USV icon
# ─────────────────────────────────────────────────────────────
icon_url = "https://raw.githubusercontent.com/joanapaiva82/Global_UVSs/main/usv.png"
df["icon_data"] = [{
    "url": icon_url,
    "width": 512,
    "height": 512,
    "anchorY": 512
} for _ in range(len(df))]

# ─────────────────────────────────────────────────────────────
# Country filter for zoom and table
# ─────────────────────────────────────────────────────────────
st.subheader("🔎 Select a country")
countries = sorted(df["Country"].unique())
selected_country = st.selectbox("Choose a country to explore", ["🌍 Show All"] + countries)

if selected_country != "🌍 Show All":
    df_table = df[df["Country"] == selected_country]
    map_lat, map_lon = country_centroids[selected_country]
    map_zoom = 3.5
else:
    df_table = df
    map_lat, map_lon, map_zoom = 10, 0, 1.2

# ─────────────────────────────────────────────────────────────
# Map Display (always show all USVs)
# ─────────────────────────────────────────────────────────────
st.subheader("🗺️ USV Map (all countries)")
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
            data=df,
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
# USV Table (filtered)
# ─────────────────────────────────────────────────────────────
if selected_country != "🌍 Show All":
    st.subheader(f"📋 USVs in {selected_country}")
else:
    st.subheader("📋 All USVs")

st.dataframe(df_table[["Name", "Manufacturer", "Country", "Max. Length (m)"]])

# Footer
st.markdown("---")
st.caption("📍 MSc Hydrography Dissertation – Joana Paiva, University of Plymouth")
