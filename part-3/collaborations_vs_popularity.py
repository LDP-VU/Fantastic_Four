import sqlite3
import pandas as pd
import sys
import os

# Adds the parent directory to the search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

from explicit_proportion import combined_df

# connecting to the database and creating a cursor
connection = sqlite3.connect("spotify_database.db")
cursor = connection.cursor()

# finds all explicit tracks
query_popularity = f"SELECT id, track_popularity FROM tracks_data"
cursor.execute(query_popularity)

#stores the query in a dataframe
rows = cursor.fetchall()
df_track_popularity = pd.DataFrame(rows,
                  columns = [x[0] for x in cursor.description])

# finds the track id and number of artists that worked on the track
query_collab = f"SELECT track_id, artist_0, artist_1 FROM albums_data "
cursor.execute(query_collab)

#stores the query in a dataframe
rows = cursor.fetchall()
df_collab = pd.DataFrame(rows,
                  columns = [x[0] for x in cursor.description])

# merges df_collab with df_track_popularity
df_collab_pop = pd.merge(df_collab,df_track_popularity, left_on='track_id',right_on ='id', how = 'inner')

#checks if a song is a collaboration
def is_Collaboration(row):
    a1 = str(row['artist_1']).lower().strip()
    if a1 != 'none' and a1 != 'None' and a1 != '':
        return True
    else:
        return False


# applies the is_Collaboration function to the df, since axis = 1 the df gives input per row
df_collab_pop['is_collab'] = df_collab_pop.apply(is_Collaboration, axis=1)

# groups the collaboration tracks vs the solo track and calculates the mean popularity of both groups
results = df_collab_pop.groupby('is_collab')['track_popularity'].mean()

# collaboration are on average around 4% more popular
print(results)


