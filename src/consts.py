"""Shared constants for the GDELT data pipeline."""

GDELT_DATA_BASE_URL = "http://0.0.0.0:8000"
GDELT_LATEST_FILES_URL = "http://0.0.0.0:8000/lastupdate.txt"
# GDELT_DATA_BASE_URL = "http://data.gdeltproject.org/gdeltv2/"
# GDELT_LATEST_FILES_URL = "https://data.gdeltproject.org/gdeltv2/lastupdate.txt"

LAST_DOWNLOADED_FN_TS_PATH = "../data/last_downloaded_fn_ts.json"
DOWNLOAD_LOG_PATH = "../data/download_log.json"
UPDATE_CHECK_INTERVAL_SECONDS = 20 * 60  # GDELT refreshes its file listing every 15 minutes
GDELT_FILE_INTERVAL_SECONDS = 15 * 60  # GDELT publishes new data files every 15 minutes
DATA_FILES_LOC = "../data"
REL_RAW_ZIP_FILES_LOC = "raw_zips"
REL_RAW_CSV_FILES_LOC = "raw_csvs"
LAST_DOWNLOADED_FN_TS_KEY = "last_downloaded_fn_ts"
