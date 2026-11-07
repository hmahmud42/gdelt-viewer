"""Generate local test GDELT export CSV + ZIP files for offline end-to-end testing.

Creates tab-separated CSV files named <YYYYMMDDHHMMSS>.export.CSV (one geo-located
climate news event per file, in the column format defined by gdelt_export_columns)
plus their corresponding <YYYYMMDDHHMMSS>.export.CSV.zip into the output directory,
so a local HTTP server can serve them and the full GDELT data_getter -> get_csvs ->
app pipeline can be tested without accessing the real GDELT servers.

Run example:
    python scripts/generate_test_gdelt_data.py --output-dir tests/mock_gdelt
    python -m http.server 8099 --directory tests/mock_gdelt
"""

import argparse
import sys
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from gdelt_export_columns import gdelt_v2_export_columns  # noqa: E402

COLUMNS = list(gdelt_v2_export_columns.keys())

_DEFAULTS: dict = {
    "GLOBALEVENTID": 1000,
    "SQLDATE": 20261105,
    "MonthYear": 202611,
    "Year": 2026,
    "FractionDate": 2026.25,
    "Actor1Code": "ENV",
    "Actor1Name": "Climate Action NGO",
    "Actor1CountryCode": "99",
    "Actor1KnownGroupCode": "",
    "Actor1EthnicCode": "",
    "Actor1Religion1Code": "",
    "Actor1Religion2Code": "",
    "Actor1Type1Code": "",
    "Actor1Type2Code": "",
    "Actor1Type3Code": "",
    "Actor2Code": "GOV",
    "Actor2Name": "Government",
    "Actor2CountryCode": "99",
    "Actor2KnownGroupCode": "",
    "Actor2EthnicCode": "",
    "Actor2Religion1Code": "",
    "Actor2Religion2Code": "",
    "Actor2Type1Code": "",
    "Actor2Type2Code": "",
    "Actor2Type3Code": "",
    "IsRootEvent": 1,
    "EventCode": "ECO",
    "EventBaseCode": "ECO",
    "EventRootCode": "ECO",
    "QuadClass": 2,
    "GoldsteinScale": -5.0,
    "NumMentions": 2,
    "NumSources": 1,
    "NumArticles": 2,
    "AvgTone": -9.5,
    "Actor1Geo_Type": 1,
    "Actor1Geo_FullName": "Europe",
    "Actor1Geo_CountryCode": "99",
    "Actor1Geo_ADM1Code": "",
    "Actor1Geo_ADM2Code": "",
    "Actor1Geo_Lat": 50.0,
    "Actor1Geo_Long": 10.0,
    "Actor1Geo_FeatureID": "",
    "Actor2Geo_Type": 0,
    "Actor2Geo_FullName": "",
    "Actor2Geo_CountryCode": "",
    "Actor2Geo_ADM1Code": "",
    "Actor2Geo_ADM2Code": "",
    "Actor2Geo_Lat": 0.0,
    "Actor2Geo_Long": 0.0,
    "Actor2Geo_FeatureID": "",
    "ActionGeo_Type": 1,
    "ActionGeo_FullName": "Europe",
    "ActionGeo_CountryCode": "99",
    "ActionGeo_ADM1Code": "",
    "ActionGeo_ADM2Code": "",
    "ActionGeo_Lat": 50.0,
    "ActionGeo_Long": 10.0,
    "ActionGeo_FeatureID": "",
    "DATEADDED": 20261105000000,
    "SOURCEURL": "",
}


def _row(ts: str, source_url: str, lat: float, lng: float) -> list:
    """Build a single GDELT export row (tab-separated values) for a climate news event."""
    values = dict(_DEFAULTS)
    values.update(
        {
            "GLOBALEVENTID": 1000 + int(ts[8:10]),
            "SQLDATE": int(ts[0:8]),
            "MonthYear": int(f"{int(ts[0:4])}{int(ts[4:6])}"),
            "Year": int(ts[0:4]),
            "FractionDate": float(f"{int(ts[0:4])}.25"),
            "Actor1Code": "ENV",
            "Actor1Name": "Climate Action NGO",
            "Actor1CountryCode": "99",
            "Actor2Code": "GOV",
            "Actor2Name": "Government",
            "Actor2CountryCode": "99",
            "IsRootEvent": 1,
            "EventCode": "ECO",
            "EventBaseCode": "ECO",
            "EventRootCode": "ECO",
            "QuadClass": 2,
            "GoldsteinScale": -5.0,
            "NumMentions": 2,
            "NumSources": 1,
            "NumArticles": 2,
            "AvgTone": -9.5,
            "Actor1Geo_Type": 1,
            "Actor1Geo_FullName": "Europe",
            "Actor1Geo_CountryCode": "99",
            "Actor1Geo_ADM1Code": "",
            "Actor1Geo_ADM2Code": "",
            "Actor1Geo_Lat": lat,
            "Actor1Geo_Long": lng,
            "Actor1Geo_FeatureID": "",
            "Actor2Geo_Type": 0,
            "Actor2Geo_FullName": "",
            "Actor2Geo_CountryCode": "",
            "Actor2Geo_ADM1Code": "",
            "Actor2Geo_ADM2Code": "",
            "Actor2Geo_Lat": 0.0,
            "Actor2Geo_Long": 0.0,
            "Actor2Geo_FeatureID": "",
            "ActionGeo_Type": 1,
            "ActionGeo_FullName": "Europe",
            "ActionGeo_CountryCode": "99",
            "ActionGeo_ADM1Code": "",
            "ActionGeo_ADM2Code": "",
            "ActionGeo_Lat": lat,
            "ActionGeo_Long": lng,
            "ActionGeo_FeatureID": "",
            "DATEADDED": int(ts),
            "SOURCEURL": source_url,
        }
    )
    return [values[col] for col in COLUMNS]


def generate(output_dir: str, cutoff_time: str = "080000") -> list:
    """Generate GDELT export CSV + ZIP files for the daily batch up to a cutoff time.

    The cutoff time is expected in HHMMSS format (eg. "080000" for 08:00 AM) and the
    batch starts at the beginning of the current day (UTC).

    Returns the list of generated file names (<YYYYMMDDHHMMSS>.export.CSV.zip).
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    tz = timezone.utc
    cutoff_dt = datetime.now(tz).replace(
        hour=int(cutoff_time[0:2]),
        minute=int(cutoff_time[2:4]),
        second=int(cutoff_time[4:6]),
        microsecond=0,
    )
    batch_start = cutoff_dt - timedelta(hours=24)

    generated = []
    current = batch_start
    while current <= cutoff_dt:
        ts = current.strftime("%Y%m%d%H%M%S")
        source_url = f"https://www.climate-news.example.com/{ts}"
        lat = round(35.0 + (current.minute % 60) * 0.1, 2)
        lng = round(-40.0 - (current.minute % 60) * 0.1, 2)
        csv_name = f"{ts}.export.CSV"
        zip_name = f"{ts}.export.CSV.zip"
        content = "\n".join("\t".join(str(v) for v in _row(ts, source_url, lat, lng)) for _ in range(1)) + "\n"
        with zipfile.ZipFile(out / zip_name, "w") as z:
            z.writestr(csv_name, content)
        generated.append(zip_name)
        current += timedelta(seconds=900)
    return generated


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate local test GDELT export CSV + ZIP files.")
    parser.add_argument("--output-dir", default="tests/mock_gdelt", help="Directory to write test zip files into.")
    parser.add_argument("--cutoff-time", default="080000", help='Daily batch cutoff time in HHMMSS (default "080000").')
    args = parser.parse_args()
    files = generate(args.output_dir, args.cutoff_time)
    print(f"Generated {len(files)} test GDELT files in {args.output_dir}:")
    for f in files:
        print(" -", f)
