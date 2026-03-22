# Spotify Database Data Analysis and Visualization Dashboard
This project analyses a dataset provided by **Spotify (2023)** containing information about artists, albums, tracks, and audio features. A python-based analysis is carried out to explore relationships between variables, and create statistical analyses and visualizations. The final outcome is a dashboard showing key figures, statistics and insights from the Spotify dataset.

## Repository Structure
```
.                  
├── scripts/
│   ├── dashboard.py        
│   ├── part1.py
│   ├── part3.py
│   └── part4.py   
├── artist_data.csv
├── README.md
├── requirements.txt        
├── spotify_database.db    
└── .gitignore
```
- **scripts/** contains Python scripts used for analysis and visualization.
- **.gitignore** excludes unnecessary files like temporary files, logs, or sensitive information.
- **requirements.txt** indicates package dependencies. 
  
## Data Source
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
2. Install all required packages. Run this in your terminal:
   ```bash
   pip install streamlit pandas matplotlib plotly numpy
   ```
4. Navigate to the `Scripts` directory in your terminal.
5. Run the following command:
   ```bash
   streamlit run dashboard.py
   ```
6. The app will open in your default browser at http://localhost:8501.

## Dashboard Walkthrough
### Navigation
The dashboard is organized into four main sections, accessible via the sidebar:
- **Home**
- **Feature & Genre Analysis**
- **Artist Search**
- **Trends Over Time**

### Home
Provides an overview of the dataset and key summary statistics.

#### Key Elements:
- KPI metrics (e.g., average popularity, number of artists, average followers)
- Distribution of artist popularity histogram
- Top 10 artists by followers bar chart
- Scatter plot of followers vs artist popularity (log-scaled)
- Genre distribution and genre diversity analysis
- Comparison of explicit vs non-explicit tracks
- Comparison of solo vs collaborative tracks

### Feature & Genre Analysis
#### Genre Analysis
- Select a genre (e.g., pop, rock, jazz)
- Output:
  - Top 10 artists in that genre
  - Average popularity within the genre
  - Total number of artists associated with the genre

#### Feature Analysis
- Select an audio feature (e.g., danceability, energy, valence)
- Adjust the percentage threshold for “top tracks”
- Output:
  - Top tracks for feature
  - Top artist by feature
  - Distribution of the selected feature
  - Genres associated with very low vs very high feature values

### Artist Search
Exploring individual artists
#### Key Elements:
- Search and select an artist from a cleaned dataset
- Display:
  - Artist popularity
  - Number of followers
  - Number of associated genres
  - Explicit content ratio
- View top 5 tracks by artist ranked by popularity
  
### Trends Over Time
Analyzes how audio features evolve over time.
#### Key Elements:
- Year range slider
- Feature selection dropdown
- Outputs:
  - Yearly average values of selected feature
  - Smoothed trend (rolling average)

## Additional Functionality
The dashboard uses cached data loading so that the dataset does not need to be reloaded every time the website is refreshed.

## Notes
This project was created as part of the Data Engineering course for the Bachelor Mathematics (Applied Mathematics: Data Science track) Vrije Universiteit Amsterdam.
All code and analyses are educational and exploratory in nature.

## Contact
Leo Du Preez
Email: l.dupreez@student.vu.nl

Paula Lotz
Email: p.c.lotz@student.vu.nl

Tytti Ojala
Email: t.e.ojala@student.vu.nl

Thomas Schukken
Email: t.f.k.schukken@student.vu.nl




