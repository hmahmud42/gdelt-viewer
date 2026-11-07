"""Streamlit app that pulls climate change news coverage from the GDELT Project
DOC API and displays it."""

import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import math
from data_getter import get_daily_batch, _get_gdelt_export_csv_fn_from_zip_fn
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


daily_files = get_daily_batch()

url_objects: list[dict] = []
for file_name in daily_files:
    csv_name = _get_gdelt_export_csv_fn_from_zip_fn(file_name)
    url_objects.extend(get_URL_lat_long_from_csv(csv_name))

# Stand-in for the keyword based climate filter - replace with real implementation later.
def _filter_climate_relevant(items: list) -> list:
    return items

url_objects = _filter_climate_relevant(url_objects)

unique_objects: dict = {}
for obj in url_objects:
    unique_objects[obj.get("url")] = obj
url_objects = list(unique_objects.values())

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
clicked_loc = None
if isinstance(map_output, dict):
    clicked_loc = map_output.get("last_object_clicked")

if clicked_loc is not None:
    clicked_lat = float(clicked_loc.get("lat") or 0)
    clicked_lng = float(clicked_loc.get("lng") or 0)
    article_url = None
    for obj in url_objects:
        coords = obj.get("coords")
        if coords is None:
            continue
        for coord in coords:
            if abs(float(coord[0]) - clicked_lat) < 1e-6 and abs(float(coord[1]) - clicked_lng) < 1e-6:
                article_url = obj.get("url")
                break
        if article_url is not None:
            break
    if article_url is not None:
        st.link_button("Open article", article_url)


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



