"""Streamlit app that pulls climate change news coverage from the GDELT Project
DOC API and displays it."""

import streamlit as st
import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import math
from gdelt_export_csv_analysis import get_URL_lat_long_from_csv

# from load_gdelt import format_gdelt_date, load_climate_articles, load_climate_timeline

st.set_page_config(page_title="GDELT Climate Change Tracker", page_icon="🌍", layout="wide")

TIMESPAN_OPTIONS = ["24h", "7d", "30d", "90d", "180d"]

st.title("🌍 GDELT Climate Change Tracker")
st.caption(
    "News coverage of climate change from the "
    "[GDELT Project](https://www.gdeltproject.org/) DOC API"
)

with st.sidebar:
    st.header("Data Retreival Settings (data from local download only)")
    st.date_input("Select date range to display", ("2026-06-01", "2026-10-25"))



# st.title("Map Selection Sidebar Updates")


url_objects = get_URL_lat_long_from_csv("20261025000000.export.csv")

url_list  = [url_dct["url"] for url_dct in url_objects]
rev_url_map = { tuple(coord): url_dct["url"] for url_dct in url_objects for coord in url_dct["coords"]}


# Build the map
m = folium.Map(location=[35.0, -40.0], zoom_start=2)

for coord, url in rev_url_map.items():
    folium.Marker(location=list(coord), tooltip=f"News from {url}",).add_to(m)


# Render the map and catch the output state
map_output = st_folium(m, width=700, height=400, key="main_map")
# print("\n*********\n")
# print(json.dumps(map_output, indent=4))
# clicked_loc = map_output["last_object_clicked"] 


# # 5. Extract the click information and update the sidebar dynamically
# with st.sidebar:
#     st.header("📍 Location Details")
    
#     if clicked_loc is not None:
#         object_clicked = find_loc_object(clicked_loc, location_objects)
#         if object_clicked is not None:
#             st.info(f"The {object_clicked["name"]} office is {object_clicked["value"]["desc"]}.")
#         else:
#             st.info("ERROR: Information about clicked object not found! Something went wrong, we are on it.")
            
#     else:
#         # Default fallback view before any marker is clicked
#         st.info("Click a marker on the map to see its details and resource links over here.")



