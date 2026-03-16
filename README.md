# Spotify Database Data Analysis and Visualization Dashboard
This project analyses a dataset provided by **Spotify (2023)** containing information about artists, albums, tracks, and audio features. A python-based analysis is carried out to explore relationships between variables, and create statistical analyses and visualizations. The final outcome is a dashboard showing key figures, statistics and insights from the Spotify dataset.

## Table of contents 
1. [Repository Structure](#repository-structure)  
2. [Data Source](#data-source)  
3. [Tools and Packages Used](#tools-and-packages-used)  
4. [How to Run the Dashboard](#how-to-run-the-dashboard)  
5. [Dashboard Walkthrough](#dashboard-walkthrough)  
6. [Notes](#notes)  
7. [Contact](#contact)

## Repository Structure 
 weird dash thing EDIT
│
├── Data/
│ ├── complete.csv
│ ├── covid_database.db
│ ├── day_wise.csv
│ 
├── Scripts/
│ ├── partOne.py
│ ├── query_database.py
│ ├── partThree.py
│ ├── partFour.py
│ ├── dashboard.py
│ 
├── README.md
├── requirements.txt # Vereiste Python-pakketten
- **data/** contains the Spotify database used for the analysis  
- **scripts/** contains Python scripts used for analysis and visualization  
- **dashboard/** contains the dashboard application  
- **figures/** stores generated visualizations  

## Data source
Data from the SQLite database file "spotify_database.db" is used and analysed. 
This database contains the following tabular datasets:

**artist_data**
Data provided by Spotify containing information collected in 2023.
Main variables include:
- artist name  
- popularity score *(scaled from 0–100)*  
- number of followers  
- genres associated with the artist *(six genre columns)*  

**albums_data**
Tracks are listed by track_id together with information about the album they appear on.

**tracks_data**
Contains metadata about tracks including:
- track ID  
- track popularity  
- whether the track is marked as explicit

**features_data**
Contains audio features describing musical properties of tracks, indexed by track ID.
Examples features include:
- danceability  
- energy  
- loudness  
- tempo  

## Tools and Packages used
**Git** and **Github**. Also **Python** was used to analyse the data set and the following packages were installed:
- **pandas** – data manipulation and cleaning  
- **numpy** – numerical computations  
- **matplotlib** – static data visualizations  
- **plotly** – interactive visualizations used in the dashboard  
- **streamlit** – building the interactive dashboard  
- **sqlite3** – connecting to and querying the SQLite database  
- **os** – handling file paths
- **sys** – accessing system-specific parameters 
- **itertools** – iteration tools 
- **datetime** – working with dates in the dataset  
- **pathlib** – handling of file system paths

## How to Run the Dashboard
1. Clone the repository 
2. Install all required packages. 
    Run this in your terminal: pip install streamlit pandas matplotlib plotly numpy 
3. Navigate to the `Scripts` directory in your terminal.
4. Run the following command:
   ```bash
   streamlit run dashboard.py
5. The app will open in your default browser at http://localhost:8501.


## Dashboard Walkthrough
The Dashboard consists of a homepage and .... interactive 

### General results
- Key summary metrics (KPI cards) of mean, median, total, etc.
- Histogram showing distribution of artist popularity
- Bar chart of top 10 artists by followers
- Interactive scatter plot of relationship between artist popularity vs follower count
- Descriptive statistics table
- Top 10 genres bar chart
- Artist popularity by number of genres associated boxplot

### Artists search filter



### Trends over time
- Select a year range using the slider to focus on a specific time period.
- Choose an audio feature (e.g., danceability, energy, valence, acousticness, tempo, speechiness, instrumentalness) from the dropdown menu.
- Displays the yearly average value of the selected feature across all tracks in year range.
- Includes a 10-year rolling average to reduce noise


### Features filter

## Additional Functionality
The dashboard uses cached data loading so that the dataset does not need to be reloaded every time the website is refreshed.

## Notes
This project was created as part of the Data Engineering course for the Bachelor Mathematics (Applied Mathematics: Data Science track) Vrije Universiteit Amsterdam.
All code and analyses are educational and exploratory in nature.


## Contact
Leonidas du Preez
Email: l.dupreez@student.vu.nl

Paula Lotz
Email: p.c.lotz@student.vu.nl

Tytti Ojala
Email: t.e.ojala@student.vu.nl

Thomas Schukken
Email: t.f.k.schukken@student.vu.nl




