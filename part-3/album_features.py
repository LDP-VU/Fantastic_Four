import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Adds the parent directory to the search path
db_path = os.path.join(os.path.dirname(__file__), "..", "spotify_database.db")
connection = sqlite3.connect(db_path)

#Find most popular albums, print 15 most popular ones
print(pd.read_sql("""
SELECT DISTINCT album_name, album_popularity FROM albums_data
ORDER BY album_popularity DESC
LIMIT 15;
""", connection))


# We choose the most popular album Nadie Sabe Lo Que Va A Pasar Mañana
album_name = "Nadie Sabe Lo Que Va A Pasar Mañana"

# We'll find the album id of the album
album_id_df = pd.read_sql(f"""
SELECT DISTINCT album_id
FROM albums_data
WHERE album_name = '{album_name}'
""", connection)
album_id = album_id_df.iloc[0,0]

# Now we will find the features of the tracks in the album and
# combine the information about the tracks and their features in one dataframe
df_album = pd.read_sql(f"""
SELECT albums_data.track_name,
       features_data.danceability,
       features_data.energy,
       features_data.loudness,
       features_data.valence,
       features_data.tempo
FROM albums_data
JOIN features_data ON albums_data.track_id = features_data.id
WHERE albums_data.album_id = '{album_id}'
""", connection)

print(df_album.describe())

# We'll then vizualize the features danceability and loudness of the tracks
df_album.set_index("track_name")[["danceability", "loudness"]].plot(kind="bar", figsize=(12,6))
plt.title(f"Feature Variation Across Tracks in '{album_name}'")
plt.ylabel("Feature Value")
plt.savefig(f"feature_variation_{album_name.replace(' ', '_')}.png")
plt.close()















