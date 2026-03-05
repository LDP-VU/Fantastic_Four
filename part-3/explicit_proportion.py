import sqlite3
import pandas as pd
import sys
import os

# Adds the parent directory to the search path
db_path = os.path.join(os.path.dirname(__file__), "..", "spotify_database.db")

# connecting to the database and creating a cursor
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

# finds all explicit tracks
query_explicit = f"SELECT id, explicit FROM tracks_data"
cursor.execute(query_explicit)

#stores the query in a dataframe
rows = cursor.fetchall()
df_explicit = pd.DataFrame(rows,
                  columns = [x[0] for x in cursor.description])

#fetches all artist names and track id from albums data
query_artist = f"SELECT track_id, artist_0 FROM albums_data"
cursor.execute(query_artist)

#stores all track_id and artist_id into one df
rows = cursor.fetchall()
df_artist = pd.DataFrame(rows,
                  columns = [x[0] for x in cursor.description])

#creates a df with variables explicit, track_id, artist name
combined_df = pd.merge(df_explicit,df_artist, left_on='id',right_on = 'track_id', how='inner')

# function that converts true or false to 1 or 0
def convert_explicit(value):

    val_string = str(value).lower().strip()

    if val_string == 'true':
        return 1
    elif val_string == 'false':
        return 0
    else:
        return 0

#adds a column that represents explicit with 1 or 0
combined_df['explicit_num'] = combined_df['explicit'].apply(convert_explicit)

#calculates the proportion of explicit songs and the amount of songs
artists_stats = combined_df.groupby('artist_0')['explicit_num'].agg(['mean','count'])

#sorts for artist with more than 10 songs to get a ranking
top_artists = artists_stats[artists_stats['count']>=50]

#sorts the artist by proportion of explicit songs
result = top_artists.sort_values(by = 'mean', ascending = False)

print(result.head())




