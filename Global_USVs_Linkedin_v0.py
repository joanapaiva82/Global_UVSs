import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Global Survey USVs", layout="wide")

st.title("🌍 Global Survey USVs – Interactive Map")
st.markdown("This map displays commercially available **Uncrewed Surface Vessels (USVs)** used in the **survey industry**, grouped by country and manufacturer.\n\n📍 Hover over a marker to see details.\n\n")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("usv_map_data_ready.csv")
    return df

df = load_data()

# Display map
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state=pdk.ViewState(
        latitude=10,
        longitude=0,
        zoom=1.3,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position='[Longitude, Latitude]',
            get_fill_color='[30, 144, 255, 160]',
            get_radius=50000,
            pickable=True,
        )
    ],
    tooltip={
        "html": "<b>{Name}</b><br>Manufacturer: {Manufacturer}<br>Country: {Country}<br>Length: {Max. Length (m)} m",
        "style": {"backgroundColor": "white", "color": "black"}
    }
))

st.markdown("---")
st.caption("Built for MSc Hydrography research. Feedback and contributions welcome.")
