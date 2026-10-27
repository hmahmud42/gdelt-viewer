gdelt_v2_schema = {
    "GLOBALEVENTID": "int64",  # Unique event identifier
    "SQLDATE": "int64",  # Date formatted as YYYYMMDD
    "MonthYear": "int64",  # Date formatted as YYYYMM
    "Year": "int64",  # Date formatted as YYYY
    "FractionDate": "float64",  # Year + fraction of year (YYYY.FFFF)
    "Actor1Code": "string",  # CAMEO actor code
    "Actor1Name": "string",  # Name of Actor 1
    "Actor1CountryCode": "string",  # 3-character FIPS country code
    "Actor1KnownGroupCode": "string",  # 3-character group code (e.g., IGO, NGO)
    "Actor1EthnicCode": "string",  # Ethnic code
    "Actor1Religion1Code": "string",  # Primary religion code
    "Actor1Religion2Code": "string",  # Secondary religion code
    "Actor1Type1Code": "string",  # 3-character role code (e.g., GOV, MIL)
    "Actor1Type2Code": "string",  # Secondary role code
    "Actor1Type3Code": "string",  # Tertiary role code
    "Actor2Code": "string",  # CAMEO actor code
    "Actor2Name": "string",  # Name of Actor 2
    "Actor2CountryCode": "string",  # 3-character FIPS country code
    "Actor2KnownGroupCode": "string",  # 3-character group code
    "Actor2EthnicCode": "string",  # Ethnic code
    "Actor2Religion1Code": "string",  # Primary religion code
    "Actor2Religion2Code": "string",  # Secondary religion code
    "Actor2Type1Code": "string",  # 3-character role code
    "Actor2Type2Code": "string",  # Secondary role code
    "Actor2Type3Code": "string",  # Tertiary role code
    "IsRootEvent": "int64",  # Flag (1 if event is root, 0 otherwise)
    "EventCode": "string",  # Full CAMEO action code
    "EventBaseCode": "string",  # Root CAMEO code (2nd level)
    "EventRootCode": "string",  # High-level CAMEO root code (1st level)
    "QuadClass": "int64",  # Quad class (1=Verbal Coop, 2=Material Coop, 3=Verbal Conflict, 4=Material Conflict)
    "GoldsteinScale": "float64",  # Theoretical impact score (-10.0 to +10.0)
    "NumMentions": "int64",  # Total mentions across source documents
    "NumSources": "int64",  # Total distinct sources mentioning event
    "NumArticles": "int64",  # Total articles mentioning event
    "AvgTone": "float64",  # Average sentiment tone (-100 to +100)
    "Actor1Geo_Type": "int64",  # Geographic resolution type (1-5)
    "Actor1Geo_FullName": "string",  # Full location name
    "Actor1Geo_CountryCode": "string",  # 2-character FIPS country code
    "Actor1Geo_ADM1Code": "string",  # Primary administrative division code
    "Actor1Geo_ADM2Code": "string",  # Secondary administrative division code
    "Actor1Geo_Lat": "float64",  # Latitude centroid
    "Actor1Geo_Long": "float64",  # Longitude centroid
    "Actor1Geo_FeatureID": "string",  # GNS or GNIS feature ID
    "Actor2Geo_Type": "int64",  # Geographic resolution type
    "Actor2Geo_FullName": "string",  # Full location name
    "Actor2Geo_CountryCode": "string",  # 2-character FIPS country code
    "Actor2Geo_ADM1Code": "string",  # Primary administrative division code
    "Actor2Geo_ADM2Code": "string",  # Secondary administrative division code
    "Actor2Geo_Lat": "float64",  # Latitude centroid
    "Actor2Geo_Long": "float64",  # Longitude centroid
    "Actor2Geo_FeatureID": "string",  # GNS or GNIS feature ID
    "ActionGeo_Type": "int64",  # Geographic resolution type
    "ActionGeo_FullName": "string",  # Full location name
    "ActionGeo_CountryCode": "string",  # 2-character FIPS country code
    "ActionGeo_ADM1Code": "string",  # Primary administrative division code
    "ActionGeo_ADM2Code": "string",  # Secondary administrative division code
    "ActionGeo_Lat": "float64",  # Latitude centroid
    "ActionGeo_Long": "float64",  # Longitude centroid
    "ActionGeo_FeatureID": "string",  # GNS or GNIS feature ID
    "DATEADDED": "int64",  # Timestamp added formatted as YYYYMMDDHHMMSS
    "SOURCEURL": "string",  # Original news article URL
}

import pandas as pd 

df = pd.read_csv("20261025000000.export.CSV", 
                 sep="\t",
                 names=list(gdelt_v2_schema.keys()),
                 dtype=gdelt_v2_schema)


CLIMATE_REGEX = (
    r"(?i)\b("
    r"climate|global[-_]?warming|greenhouse|emissions?|carbon|flood|"
    r"decarboniz\w*|deforestation|renewable|solar|wind[-_]?power|"
    r"fossil[-_]?fuel|methane|glacier|sea[-_]?level|sustainab\w*"
    r")\b"
)

df

from IPython import embed
embed()                 
