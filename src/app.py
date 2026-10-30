"""Streamlit app that pulls climate change news coverage from the GDELT Project
DOC API and displays it."""

import streamlit as st
import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import math


# from load_gdelt import format_gdelt_date, load_climate_articles, load_climate_timeline

st.set_page_config(page_title="GDELT Climate Change Tracker", page_icon="🌍", layout="wide")

TIMESPAN_OPTIONS = ["24h", "7d", "30d", "90d", "180d"]

st.title("🌍 GDELT Climate Change Tracker")
st.caption(
    "News coverage of climate change from the "
    "[GDELT Project](https://www.gdeltproject.org/) DOC API"
)

with st.sidebar:
    st.header("Query settings")
    keyword = st.text_input("Search keyword", value="climate change")
    timespan = st.selectbox("Time window", TIMESPAN_OPTIONS, index=2)
    max_records = st.slider("Max articles to fetch", 10, 50, 25, step=5)
    if st.button("Refresh data"):
        st.cache_data.clear()




# st.title("Map Selection Sidebar Updates")

# 1. Setup mock data with coordinates, descriptions, and dynamic URLs
# NOTE: coordinates are in [lat, lng] format
location_objects = [
    {"name": "London Office",
     "value": {
        "coords": [51.5074, -0.1278],
        "desc": "the main headquarters located in central London.",
        "links": ["https://google.com", "https://wikipedia.org"]
        },
    },
    {
    "name": "New York Hub",
    "value": {
        "coords": [ 40.7128, -0.0060],
        "desc": "is the US east coast tech and innovation hub.",
        "links": ["https://github.com", "https://stackoverflow.com"]
        },
    }
]

loc_names = [loc_dct["name"] for loc_dct in location_objects]


def find_loc_object(coords, loc_objects):
    for loc_dct in location_objects:
        if math.isclose(loc_dct["value"]["coords"][0], coords["lat"]) and \
            math.isclose(loc_dct["value"]["coords"][1], coords["lng"]):
            return loc_dct
    return None


# 2. Build the baseline map
m = folium.Map(location=[35.0, -40.0], zoom_start=2)


# 3. Add markers with unique layer IDs
for loc_dct in location_objects:
    folium.Marker(
        location=loc_dct["value"]["coords"],
        tooltip=f"Click to inspect {loc_dct["name"]}",
        # Set layer_id so st_folium can tell us exactly which marker was clicked
        layer_id=loc_dct["name"]
    ).add_to(m)


# 4. Render the map and catch the output state
map_output = st_folium(m, width=700, height=400, key="main_map")
print("\n*********\n")
print(json.dumps(map_output, indent=4))
clicked_loc = map_output["last_object_clicked"] 


# 5. Extract the click information and update the sidebar dynamically
with st.sidebar:
    st.header("📍 Location Details")
    
    if clicked_loc is not None:
        object_clicked = find_loc_object(clicked_loc, location_objects)
        if object_clicked is not None:
            st.info(f"The {object_clicked["name"]} office is {object_clicked["value"]["desc"]}.")
        else:
            st.info("ERROR: Information about clicked object not found! Something went wrong, we are on it.")
            
    else:
        # Default fallback view before any marker is clicked
        st.info("Click a marker on the map to see its details and resource links over here.")



# @st.cache_data(ttl=300)
# def fetch_articles(keyword: str, timespan: str, max_records: int):
#     return load_climate_articles(
#         keyword=keyword, timespan=timespan, max_records=max_records
#     )


# @st.cache_data(ttl=300)
# def fetch_timeline(keyword: str, timespan: str):
#     return load_climate_timeline(keyword=keyword, timespan=timespan)


# try:
#     articles = fetch_articles(keyword=keyword, timespan=timespan, max_records=max_records)
#     timeline = fetch_timeline(keyword=keyword, timespan=timespan)
# except Exception as e:
#     st.error(f"Failed to load data from the GDELT API: {e}")
#     st.error(
#         "The GDELT API may be rate limiting requests right now. "
#         "Please wait a moment and hit 'Refresh data' again."
#     )
#     st.stop()

# st.divider()

# if articles.empty:
#     st.info(
#         "No climate articles were found for this query. Try a broader time window "
#         "or a different keyword."
#     )
#     st.stop()

# Metrics row
# col_1, col_2, col_3 = st.columns(3)
# with col_1:
#     st.metric(label="Articles in window", value=len(articles))
# with col_2:
#     peak_intensity = (
#         float(timeline["Volume Intensity"].max()) if not timeline.empty else None
#     )
#     st.metric(
#         label="Peak coverage intensity",
#         value=f"{peak_intensity:.4f}" if peak_intensity is not None else "N/A",
#     )
# with col_3:
#     sources = articles["domain"].fillna("").nunique()
#     st.metric(label="Sources reporting", value=int(sources))

# st.divider()

# # Coverage timeline chart
# st.subheader("News coverage volume over time")
# if timeline.empty:
#     st.info("No timeline data available for this query.")
# else:
#     st.area_chart(
#         timeline,
#         x="datetime",
#         y="Volume Intensity",
#         x_label="Date",
#         y_label="Volume intensity (share of total monitored coverage)",
#     )

# st.divider()

# # Top sources bar chart
# st.subheader("Top sources in this window")
# top_sources = (
#     articles["domain"].fillna("unknown").value_counts().head(10).reset_index()
# )
# top_sources.columns = ["Source", "Articles"]
# st.bar_chart(top_sources, x="Articles", y="Source", horizontal=True)

# st.divider()

# # Latest articles
# st.subheader(f"Latest climate coverage ({len(articles)} articles)")

# for _, row in articles.iterrows():
#     title = str(row.get("title") or "Untitled")
#     url = str(row.get("url") or "#")
#     domain = str(row.get("domain") or "unknown")
#     seendate = format_gdelt_date(row.get("seendate"))
#     language = str(row.get("language") or "")
#     source_country = str(row.get("sourcecountry") or "")

#     with st.expander(f"{domain} · {seendate}"):
#         st.markdown(f"[{title}]({url})")
#         st.caption(
#             f"{domain} | Language: {language} | Source country: {source_country}"
#         )
