import streamlit as st
import pandas as pd
import pydeck as pdk

# ─────────────────────────────────────────────────────────────
# Page setup
# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Global USV Map", layout="wide")

st.title("🌍 Global Survey USVs")
st.markdown("Explore the global distribution of **Uncrewed Surface Vessels (USVs)** used for survey operations. Zoom in by country, hover over a marker, and interact with the data below.")

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
# Load data
# ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    try:
        return pd.read_csv("usv_map_data_final.csv", encoding="utf-8")
    except:
        return pd.read_csv("usv_map_data_final.csv", encoding="latin1")

df = load_data()

# ─────────────────────────────────────────────────────────────
# Country Filter Dropdown
# ─────────────────────────────────────────────────────────────
st.sidebar.header("🔎 Filter")
countries = df["Country"].sort_values().unique().tolist()
selected_country = st.sidebar.selectbox("Select a country to focus", ["🌍 Show All"] + countries)

if selected_country != "🌍 Show All":
    df_filtered = df[df["Country"] == selected_country]
else:
    df_filtered = df

# Center map based on selection
if selected_country != "🌍 Show All":
    lat = df_filtered["Latitude"].mean()
    lon = df_filtered["Longitude"].mean()
    zoom = 3.5
else:
    lat, lon, zoom = 10, 0, 1.3

# ─────────────────────────────────────────────────────────────
# Map Display
# ─────────────────────────────────────────────────────────────
st.subheader("🗺️ Interactive USV Map")

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=lat,
        longitude=lon,
        zoom=zoom,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=df_filtered,
            get_position='[Longitude, Latitude]',
            get_radius=50000,
            get_fill_color='[0, 100, 250, 160]',
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
        "style": {
            "backgroundColor": "white",
            "color": "#000",
            "fontSize": "14px"
        }
    }
))

# ─────────────────────────────────────────────────────────────
# Country-Specific Table & Selector
# ─────────────────────────────────────────────────────────────
if selected_country != "🌍 Show All":
    st.subheader(f"📋 USVs based in {selected_country}")
    usv_names = df_filtered["Name"].unique().tolist()
    selected_usv = st.selectbox("Jump to a specific USV", ["—"] + usv_names)

    if selected_usv != "—":
        usv_row = df_filtered[df_filtered["Name"] == selected_usv].iloc[0]
        st.success(f"Centered on **{selected_usv}** – {usv_row['Manufacturer']}, {usv_row['Max. Length (m)']} m")
        st.map(pd.DataFrame([usv_row], columns=["Latitude", "Longitude"]))
    
    st.dataframe(df_filtered[["Name", "Manufacturer", "Max. Length (m)"]].reset_index(drop=True))

# Footer
st.markdown("---")
st.caption("📍 MSc Dissertation Tool by Joana Paiva – University of Plymouth")
