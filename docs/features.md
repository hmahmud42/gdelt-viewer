# App v0.1 Description

## App Overview

The browers based app shows geo-located news-items related to climate change. 

## Data Source and Download Cadence

- The data for the maps is obtained from the GDELT project. 
- The data is raw CSV, specifically "<YYYYMMDDHHMMSS>.export.csv" files for GDELT data format v2.0.  
- These files are updated every fifteen minutes starting from on the hour. 
- The files are downloaded in batches, with one batch every day corresponding ot 24 * 15 = 360 files for the previous day.
- The above also means the maps are updated once a day.
- Since GDELT is a public source, we need to be respectful and not overload it with requests.
    - We will never make more than 10 request per second to the server. 
    - We will cache the files whenever possible.
        - The download zip files are very small - 16KB - so years worth of zip file takes up about 5GB.
    
## Data Processing And Information Display

- Each row in the data corresponds to a single news item with contains the sourceurl and lat/long of where the story occurs.
- The app identifies the rows corresponding to climate related news based on simple keyword matching. 
- The app then shows a map with a location pin for each news-item. 
- Clicking on a pin takes the user to the corresponding news item in a new tab in the browser.

## Basic User Journey

- When the app is opened for the first time in the day, it downloads all the latest files (showing the progress in a popup) and then shows the map.

- If not for the first time in the day, it does not do anything.


# Ideas for future versions

- Create a knowledge graph from the downloaded information. 
    - The purpose of the knowledge graph is to give the users a coherent picture of exactly what's happening in terms of climate, both good and bad around the world. 
    - A small sampling of these are: new renewable installtions, addition of new renewable capacity, climate related weather phenomena, new climate related findings, increased use of non-renewables, digging for new oil fields, energy prices rising, etc.
    - The KG can be created using either classical NLP (like NER + NL) or using LLMs - both should expolored
- Support complex queries like "what is the aggregate amount of new solar power that has come online during the last year"
    - This is a more complex use case, requireing sophistacted use of ML and agenitc systems - and creation of a well structured knoweldge base/graph that supports this kind of behavior. 






