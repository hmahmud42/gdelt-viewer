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
import warnings


# import streamlit as st
from datetime import datetime, timezone
from typing import Optional, List
from pathlib import Path



from consts import (
    GDELT_DATA_BASE_URL,
    GDELT_LATEST_FILES_URL,
    GDELT_FILE_INTERVAL_SECONDS,
    LAST_DOWNLOADED_FN_TS_PATH,
    UPDATE_CHECK_INTERVAL_SECONDS,
    DATA_FILES_LOC,
    REL_RAW_ZIP_FILES_LOC,
    REL_RAW_CSV_FILES_LOC,
    LAST_DOWNLOADED_FN_TS_KEY,
    DOWNLOAD_LOG_PATH,
)


def _fetch_gdelt_latest_file_names() -> list[str]:
    """
    Fetch the names of the latest GDELT data files from the 
    GDELT data server

    The file list is expected to return one entry per line in the format:
        <ID> <HASH> <ZIP-FILENAME>
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
        filename = parts[-1].split('/')[-1]
        if filename and filename not in filenames and 'export' in filename:
            filenames.append(filename)
    return filenames


def _get_last_downloaded_fn_ts() -> Optional[str]:
    """
    Get the time-stamp of the filename that was last downloaded
    from stored locally in YYYYMMDDHHMMSS format.

    Returns None when the state file is missing or unreadable (first run).
    """
    try:
        with open(LAST_DOWNLOADED_FN_TS_PATH, "r") as f:
            state = json.load(f)
        ldfnts = state.get(LAST_DOWNLOADED_FN_TS_KEY)[-1] if isinstance(state, dict) else state
        return str(ldfnts) if ldfnts is not None else None
    except (OSError, ValueError, TypeError):
        # Missing or corrupt state file -> treat as a first run.
        return None

# {
# "last_downloaded_fn_ts": "20261103150000"
# }

def _save_last_downloaded_fn_ts(ldfnts: str) -> None:
    """Persist the last retrieval date (YYYYMMDDHHMMSS) to local state."""
    os.makedirs(os.path.dirname(LAST_DOWNLOADED_FN_TS_PATH) or ".", exist_ok=True)
    with open(LAST_DOWNLOADED_FN_TS_PATH, "r") as f:
        try:
            data = json.load(f)
        except JSONDecodeError:
            data = None

        with open(LAST_DOWNLOADED_FN_TS_PATH, "w") as f:
            if data is None:
                json.dump({LAST_DOWNLOADED_FN_TS_KEY: [ldfnts]}, f)
            else:
                print(LAST_DOWNLOADED_FN_TS_KEY)
                data[LAST_DOWNLOADED_FN_TS_KEY].append(ldfnts)
                json.dump(data, f)


def _extract_filename_timestamp(filename: str) -> Optional[float]:
    """Extract the publish time (unix seconds) from a GDELT data file name.

    Assumes the file name format: YYYYMMDDHHMMSS.export.CSV.zip
    """
    match = re.match(r"^(\d{14})", filename)
    if not match:
        raise ValueError(f"Filename {filename} did not match format YYYYMMDDHHMMSS.export.CSV.zip")
    return datetime.strptime(
        match.group(1), "%Y%m%d%H%M%S"
    ).replace(tzinfo=timezone.utc).timestamp()


def _ts_to_gdelt_filename(timestamp: float) -> str:
    """Format a unix timestamp as a GDELT data file name.

    Assumes the file name format: YYYYMMDDHHMMSS.export.CSV.zip
    """
    return (
        datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y%m%d%H%M%S")
        + ".export.CSV.zip"
    )


def infer_filenames_to_download() -> list[str]:
    """
    Generates a list of file-names to retrieve from GDELT. These are files which were added since the
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
    latest_files = _fetch_gdelt_latest_file_names()
    if not latest_files:
        return []
    
    last_retrieved_str = _get_last_downloaded_fn_ts()
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
        (ts for ts in (_extract_filename_timestamp(f) for f in latest_files) if ts is not None),
        default=None,
    )

    if latest_ts is None:
        return []

    new_filenames = []
    candidate_ts = last_retrieved_ts
    while candidate_ts <= latest_ts:
        if candidate_ts > last_retrieved_ts:
            new_filenames.append(_ts_to_gdelt_filename(candidate_ts))
        candidate_ts += GDELT_FILE_INTERVAL_SECONDS

    return new_filenames


def _get_gdelt_export_csv_fn_from_zip_fn(file_name: str) -> str:
    """Return the CSV file name from a GDELT data file name.

    Strips the trailing ".zip" suffix, eg.
    "20240115120000.export.CSV.zip" -> "20240115120000.export.CSV"
    """
    return file_name[: -len(".zip")] if file_name.endswith(".zip") else file_name


def _read_download_log() -> dict:
    """Read the download log from local state.

    Returns a mapping of file name -> download record (with the keys "Download URL",
    "Download Timestamp" and "download-status"), or an empty dict when the log is
    missing or unreadable (first run / no downloads recorded yet).
    """
    try:
        with open(DOWNLOAD_LOG_PATH, "r") as f:
            log = json.load(f)
        return log if isinstance(log, dict) else {}
    except (OSError, ValueError, TypeError):
        # Missing or corrupt log -> treat as a first run with no downloads yet.
        return {}


def _write_download_log(log: dict) -> None:
    """Persist the download log to local state."""
    os.makedirs(os.path.dirname(DOWNLOAD_LOG_PATH) or ".", exist_ok=True)
    with open(DOWNLOAD_LOG_PATH, "w") as f:
        json.dump(log, f, indent=2)


def get_csvs(file_names: List[str], download_if_missing: bool = True) -> List[str]:
    """
    Given the set of filenames returned by infer_filenames_to_download(), retrieves
    the corresponding zip files from a fixed GDELT location using a simple
    http request (like wget) puts them under data/raw_zips, unzips the zip files
    and extracts them into data/csvs, and updates the data/last_retrieved.json 
    file to the timestamp of the last file. Returns the names of the csv files
    actually found and downloaded.

    Each download attempt is recorded in a local JSON download log (keyed by file
    name, under @data/download_log.json) containing the download URL, the download
    timestamp and the download status ("Success" | "Failed"). Failed attempts also
    record the failure reason.

    Files that the download log marks as "Success" and that exist in the raw zip
    directory are skipped. If `download_if_missing` is True, files that are not
    present on disk (or whose log status is not "Success") are downloaded.

    If the download log and the physical file system disagree, a warning is raised
    for the affected file(s).

    Failed download attempts record the failure reason, and files that failed due
    to being missing are not retried on subsequent runs.
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

    download_log = _read_download_log()
    log_updates: dict = {}
    extracted_csv_files = []
    timestamps = []

    for file_name in file_names:
        url = GDELT_DATA_BASE_URL + "/" + file_name
        zip_path = zips_dir / file_name

        csv_fn = _get_gdelt_export_csv_fn_from_zip_fn(file_name)
        log_entry = download_log.get(csv_fn) or {}
        log_status = log_entry.get("download-status")
        file_exists = zip_path.exists()

        # Warn when the download log and the physical file system are out of agreement.
        if log_status == "Success" and not file_exists:
            warnings.warn(
                f"Download log reports success for {csv_fn} but the file is missing from {zip_path}."
            )
        elif log_status is not None and log_status != "Success" and file_exists:
            warnings.warn(
                f"Download log reports status '{log_status}' for {csv_fn} but the file exists at {zip_path}."
            )

        already_downloaded = log_status == "Success" and file_exists

        skip = already_downloaded
        if not skip and log_status == "Failed":
            # If the failure was due to the file being missing, do not retry it.
            failure_reason = log_entry.get("failure-reason")
            failure_mentions_missing_file = failure_reason is not None and (
                "404" in failure_reason or "not found" in failure_reason.lower()
            )
            if failure_mentions_missing_file:
                skip = True

        if skip or not download_if_missing:
            # Already retrieved and confirmed by log + disk, failure already recorded
            # as a missing-file error, or downloads have been disabled.
            continue

        # Download the file and update the log dictionary
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        try:
            # 1. Download the ZIP file via HTTP GET
            urllib.request.urlretrieve(url, zip_path)

            # 2. Unzip and extract contents into data/csvs
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(csvs_dir)
                extracted_csv_files.extend(zip_ref.namelist())

            # Track timestamp (GDELT files typically start with a 14-digit YYYYMMDDHHMMSS timestamp)
            match = re.match(r"^(\d{14})", file_name)
            if match:
                timestamps.append(match.group(1))

            log_updates[csv_fn] = {
                "Download URL": url,
                "Download Timestamp": timestamp,
                "Download Status": "Success",
            }

        except Exception as e:
            print(f"Failed to process {file_name}: {e}")
            # Clean up partial download if failed
            if zip_path.exists():
                zip_path.unlink()
            log_updates[csv_fn] = {
                "Download URL": url,
                "Download Timestamp": timestamp,
                "Download Status": "Failed",
                "Failure Reason": str(e),
            }

    # Persist any download log updates collected during this run in a single write.
    if log_updates:
        download_log.update(log_updates)
        _write_download_log(download_log)

    # 3. Update last_retrieved.json with the timestamp of the last successful file
    if timestamps:
        _save_last_downloaded_fn_ts(max(timestamps))

    return extracted_csv_files


if __name__ == '__main__':
    from IPython import embed
    embed()

 
