import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

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
# Load CSV and Clean Text
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_clean_data():
    try:
        df = pd.read_csv("Global_USVs_Linkedin.csv", encoding="utf-8")
    except:
        df = pd.read_csv("Global_USVs_Linkedin.csv", encoding="latin1")

    # Clean non-ASCII characters
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.encode('ascii', errors='ignore').str.decode('ascii')

    # Fix country naming
    df["Country"] = df["Country"].replace({
        "UK": "United Kingdom",
        "USA": "United States",
        "UAE": "United Arab Emirates",
        "Russia": "Russian Federation",
        "Europe": "France"  # Or manually assign as needed
    })

    return df

df = load_clean_data()

# ─────────────────────────────────────────────────────────────
# Use hardcoded centroids to prevent geocoding errors
# ─────────────────────────────────────────────────────────────
country_centroids = {
    "Australia": (-25.2744, 133.7751),
    "Brazil": (-14.2350, -51.9253),
    "Canada": (56.1304, -106.3468),
    "China": (35.8617, 104.1954),
    "France": (46.2276, 2.2137),
    "Ireland": (53.1424, -7.6921),
    "Israel": (31.0461, 34.8516),
    "Netherlands": (52.1326, 5.2913),
    "Norway": (60.4720, 8.4689),
    "Sweden": (60.1282, 18.6435),
    "Turkey": (38.9637, 35.2433),
    "United Kingdom": (55.3781, -3.4360),
    "United States": (37.0902, -95.7129),
    "United Arab Emirates": (23.4241, 53.8478),
    "Russian Federation": (61.5240, 105.3188)
}

# Add lat/lon based on country
df["Latitude"] = df["Country"].map(lambda c: country_centroids.get(c, (None, None))[0])
df["Longitude"] = df["Country"].map(lambda c: country_centroids.get(c, (None, None))[1])
df = df.dropna(subset=["Latitude", "Longitude"])

# ─────────────────────────────────────────────────────────────
# Jitter: spread vessels around country centroid
# ─────────────────────────────────────────────────────────────
def jitter_data(df, jitter=1.5):
    df = df.copy()
    lat_list, lon_list = [], []

    for country, group in df.groupby("Country"):
        center_lat = group["Latitude"].iloc[0]
        center_lon = group["Longitude"].iloc[0]
        count = len(group)

        angles = np.linspace(0, 2 * np.pi, count, endpoint=False)
        lat_offsets = jitter * np.sin(angles)
        lon_offsets = jitter * np.cos(angles)

        lat_list.extend(center_lat + lat_offsets)
        lon_list.extend(center_lon + lon_offsets)

    df["Latitude"] = lat_list
    df["Longitude"] = lon_list
    return df

df = jitter_data(df)

# ─────────────────────────────────────────────────────────────
# Add vessel icon
# ─────────────────────────────────────────────────────────────
icon_url = "https://raw.githubusercontent.com/joanapaiva82/Global_UVSs/main/usv.png"
df["icon_data"] = [{
    "url": icon_url,
    "width": 512,
    "height": 512,
    "anchorY": 512
} for _ in range(len(df))]

# ─────────────────────────────────────────────────────────────
# Country Filter Dropdown
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
# Pydeck Map
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
# Data Table
# ─────────────────────────────────────────────────────────────
st.subheader("📋 Filtered USV List")
st.dataframe(df_table[["Name", "Manufacturer", "Country", "Max. Length (m)"]])

st.markdown("---")
st.caption("📍 MSc Hydrography Dissertation – Joana Paiva, University of Plymouth")
