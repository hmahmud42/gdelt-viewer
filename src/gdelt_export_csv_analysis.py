"""
Analyses the export csv files and provides necessary information.
"""
from pathlib import Path
import pandas as pd
from consts import DATA_FILES_LOC, REL_RAW_CSV_FILES_LOC
from gdelt_export_columns import gdelt_v2_export_columns


def get_url_lat_long_dict(grouped_df):
    return {
            "url": grouped_df.name,
            "coords": grouped_df[["ActionGeo_Lat", "ActionGeo_Long"]].values
    }


def get_URL_lat_long_from_csv(csv_name):
    """
    Given a CSV file returns a dictionary of the form
    {"url": <URL>,
     "coords": [[<lat>, <lng>], [<lat>, <lng>],... ]]
     }
    """
    base_dir = Path(DATA_FILES_LOC)
    csvs_dir = base_dir / REL_RAW_CSV_FILES_LOC
    df = pd.read_csv(csvs_dir / csv_name, 
                     sep="\t",
                     names=list(gdelt_v2_export_columns.keys()),
                     dtype=gdelt_v2_export_columns)
    

    
    return list(df[['SOURCEURL', 'ActionGeo_Lat', 'ActionGeo_Long']].dropna().drop_duplicates().groupby('SOURCEURL').apply(get_url_lat_long_dict).values)







