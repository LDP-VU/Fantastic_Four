import pandas as pd
import sqlite3
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

# Adds the parent directory to the search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

# Finds the folder where this script is saved
script_dir = Path(__file__).resolve().parent

#finds the parent folder
parent_dir = script_dir.parent
# Joins that folder path with the database name
db_path = parent_dir / "spotify_database.db"

# Connects to the database at that specific location
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

query_tempo = f"SELECT id, tempo FROM features_data"
cursor.execute(query_tempo)

#stores the query in a dataframe
rows = cursor.fetchall()
df_tempo = pd.DataFrame(rows,
                  columns = [x[0] for x in cursor.description])

query_tracks = f"SELECT id, track_popularity FROM tracks_data"
cursor.execute(query_tracks)
rows = cursor.fetchall()
df_tracks = pd.DataFrame(rows,
                  columns = [x[0] for x in cursor.description])

df_track_pop = pd.merge(df_tempo,df_tracks,how = 'inner')

query_tracks = f"SELECT track_id, track_name FROM albums_data"
cursor.execute(query_tracks)
rows = cursor.fetchall()
df_song = pd.DataFrame(rows,
                  columns = [x[0] for x in cursor.description])

df_song_pop = pd.merge(df_song,df_track_pop, left_on = 'track_id',right_on = 'id', how = 'inner')
df_song_pop = df_song_pop.drop(columns = ['id','track_id'])
df_song_pop = df_song_pop.sort_values(by=['track_popularity'], ascending=False)
df_song_pop = df_song_pop[df_song_pop['tempo'] > 0]


#Prepare datas (dropping NaNs ensures the trend line calculation works)
df_plot = df_song_pop.dropna(subset=['tempo', 'track_popularity'])
x = df_plot['tempo']
y = df_plot['track_popularity']

# Creates the Scatter Plot
plt.scatter(x, y, s=1, alpha=0.2, color='tab:blue')


# 4. Adds Labels and Formatting
plt.title('Correlation: Tempo vs. Track Popularity')
plt.xlabel('Tempo ($BPM$)')
plt.ylabel('Popularity ($0-100$)')

# 5. Save the result
plt.tight_layout()
plt.savefig('tempo_popularity.png')




