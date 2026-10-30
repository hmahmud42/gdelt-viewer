"""
Functions to get raw data files from gdelt, run analysis to get the file locations, so that they can be displayed in the app.
"""

import os
import json
import re
import time
import httpx
from json.decoder import JSONDecodeError
import urllib.request
import zipfile


# import streamlit as st
from datetime import datetime, timezone
from typing import Optional, List
from pathlib import Path



from consts import (
    GDELT_FILE_INTERVAL_SECONDS,
    GDELT_LATEST_FILES_URL,
    LAST_RETRIEVED_PATH,
    UPDATE_CHECK_INTERVAL_SECONDS,
    GDELT_DATA_BASE_URL,
    DATA_FILES_LOC,
    REL_RAW_ZIP_FILES_LOC,
    REL_RAW_CSV_FILES_LOC,
    LAST_RETRIEVED_KEY
)


def _fetch_latest_file_names() -> list[str]:
    """Fetch the names of the latest GDELT data files.

    The file list is expected to return one entry per line in the format:
        <ID> <HASH> <FILENAME>
    """
    try:
        response = httpx.get(GDELT_LATEST_FILES_URL, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError as e:
        # st.error(f"Network error accessing the GDELT file list: {e}")
        return []

    filenames: list[str] = []
    for line in response.text.splitlines():
        parts = line.split()
        if len(parts) < 3:
            # Malformed / blank lines are skipped.
            continue
        filename = parts[-1]
        if filename and filename not in filenames and 'export' in filename:
            filenames.append(filename)
    return filenames


def _read_last_retrieved() -> Optional[str]:
    """Read the last retrieval date (YYYYMMDDHHMMSS) from local state.

    Returns None when the state file is missing or unreadable (first run).
    """
    try:
        with open(LAST_RETRIEVED_PATH, "r") as f:
            state = json.load(f)
        last_retrieved = state.get("last_retrieved") if isinstance(state, dict) else state
        return str(last_retrieved) if last_retrieved is not None else None
    except (OSError, ValueError, TypeError):
        # Missing or corrupt state file -> treat as a first run.
        return None


def _write_last_retrieved(last_retrieved_ts: str) -> None:
    """Persist the last retrieval date (YYYYMMDDHHMMSS) to local state."""
    os.makedirs(os.path.dirname(LAST_RETRIEVED_PATH) or ".", exist_ok=True)
    with open(LAST_RETRIEVED_PATH, "r") as f:
        try:
            data = json.load(f)
        except JSONDecodeError:
            data = None

        with open(LAST_RETRIEVED_PATH, "w") as f:
            if data is None:
                json.dump({LAST_RETRIEVED_KEY: last_retrieved_ts}, f)
            else:
                data[LAST_RETRIEVED_KEY] = data["last_retrieved"].append(last_retrieved_ts)
                json.dump(data, f)


def _filename_timestamp(filename: str) -> Optional[float]:
    """Extract the publish time (unix seconds) from a GDELT data file name.

    Assumes the file name format: YYYYMMDDHHMMSS.export.CSV.zip
    """
    match = re.match(r"^(\d{14})", filename)
    if not match:
        return None
    return datetime.strptime(
        match.group(1), "%Y%m%d%H%M%S"
    ).replace(tzinfo=timezone.utc).timestamp()


def _format_gdelt_filename(timestamp: float) -> str:
    """Format a unix timestamp as a GDELT data file name.

    Assumes the file name format: YYYYMMDDHHMMSS.export.CSV.zip
    """
    return (
        datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y%m%d%H%M%S")
        + ".export.CSV.zip"
    )


def get_update_filenames() -> list[str]:
    """
    Generates a list of file-names to retrieve GDELT. These are files which were added since the
    last time GDELT was checked. 

    **Steps In detail:**

    GDELT updates its file list every 15 minutes, and makes the names of the latest files available
    at a single location.
    
    Begin by retrieve the names of the latest files from GDELT. 
    
    Check the time-stamp of the last time the data was retrieved from GDELT raw data service, which
    is stored locally in @data/last_retrieved.json (which may be absent).

    - If the @data/last_retrieved.json file is absent, return the latest file.
    - If the time-stamp is less than 20 minutes, return an empty list.
    - Otherwise, infer the names of all the files up to the latest since the time of the last update
      and return the list of files.

    **URLs:**
    - Assume the URL of the list of latest files is 
    http://gdelt-data/latest-files

    **Filelist format"

    <ID> <HASH> <FILENAME> 

    **Filename format:** 

    Assume data files have the format 
        YYYYMMDDHHMMSS.export.CSV.zip
    """
    latest_files = _fetch_latest_file_names()
    if not latest_files:
        return []
    

    last_retrieved_str = _read_last_retrieved()
    last_retrieved_ts = (
        datetime.strptime(last_retrieved_str, "%Y%m%d%H%M%S")
        .replace(tzinfo=timezone.utc)
        .timestamp()
        if last_retrieved_str is not None
        else None
    )
    now = time.time()

    if last_retrieved_ts is not None and (now - last_retrieved_ts) < UPDATE_CHECK_INTERVAL_SECONDS:
        # We checked very recently, so the listing is unlikely to have changed.

        return []

    # The latest file list only contains the most recent file, so regenerate the
    # names of all files since the last retrieval by incrementing the last known
    # file name by the GDELT publication interval (15 minutes) up to the latest file.

    # If no prior retrieval is known, fall back to just the latest file.
    if last_retrieved_ts is None:
        return [latest_files[-1]]

    latest_ts = max(
        (ts for ts in (_filename_timestamp(f) for f in latest_files) if ts is not None),
        default=None,
    )

    if latest_ts is None:
        return []

    new_filenames = []
    candidate_ts = last_retrieved_ts
    while candidate_ts <= latest_ts:
        if candidate_ts > last_retrieved_ts:
            new_filenames.append(_format_gdelt_filename(candidate_ts))
        candidate_ts += GDELT_FILE_INTERVAL_SECONDS

    return new_filenames


def get_csvs(file_names: List[str]) -> List[str]:
    """
    Given the set of filenames returned by get_update_filenames(), retrieves
    the corresponding zip files from a fixed GDELT location using a simple
    http request (like wget) puts them under data/raw_zips, unzips the zip files
    and extracts them into data/csvs, and updates the data/last_retrieved.json 
    file to the timestamp of the last file. Returns the names of the csv files
    actually found and downloaded.
    """
    if not file_names:
        return []

    # Define path directories
    base_dir = Path(DATA_FILES_LOC)
    zips_dir = base_dir / REL_RAW_ZIP_FILES_LOC
    csvs_dir = base_dir / REL_RAW_CSV_FILES_LOC

    # Ensure output directories exist
    zips_dir.mkdir(parents=True, exist_ok=True)
    csvs_dir.mkdir(parents=True, exist_ok=True)

    extracted_csv_files = []
    timestamps = []

    for file_name in file_names:
        url = GDELT_DATA_BASE_URL + file_name
        zip_path = zips_dir / file_name

        try:
            # 1. Download the ZIP file via HTTP GET
            urllib.request.urlretrieve(url, zip_path)

            # 2. Unzip and extract contents into data/csvs
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(csvs_dir)
                extracted_csv_files.extend(zip_ref.namelist())

            # Track timestamp (GDELT files typically start with a 14-digit YYYYMMDDHHMMSS timestamp)
            match = re.match(r"^(\d{14})", file_name)
            if match: timestamps.append(match.group(1))

        except Exception as e:
            print(f"Failed to process {file_name}: {e}")
            # Clean up partial download if failed
            if zip_path.exists():
                zip_path.unlink()

    # 3. Update last_retrieved.json with the timestamp of the last successful file

    _write_last_retrieved(max(timestamps))

    return extracted_csv_files


if __name__ == '__main__':
    fns  = get_update_filenames()
    for fn in fns:
        print(fn)
