import pandas as pd
import numpy as np
import sqlite3

conn = sqlite3.connect("spotify_database.db")


df = pd.read_sql("""
SELECT 
    albums_data.track_id,
    albums_data.track_name,
    albums_data.duration_ms,
    albums_data.album_popularity,
    features_data.danceability,
    features_data.energy,
    features_data.valence
FROM albums_data
JOIN features_data
ON albums_data.track_id = features_data.id
""", conn)



#Let's start by making a copy of our to save the original file
df_original = df.copy()

# We delete all empty ID's and negatve or zero duration
df = df.dropna(subset=["track_id"])
df = df[df["duration_ms"] > 0]


# We make sure all features are with correct values
features = [
    "danceability", "energy", "valence"
]

for col in features:
    df = df[(df[col] >= 0) & (df[col] <= 1)]

# Then we remove duplicates
df = df.drop_duplicates(subset=["track_id"])

# Now we look for ourliers. We start with detecting outliers in different features with IQR method
feature = "danceability"

Q1 = df[feature].quantile(0.25)
Q3 = df[feature].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
outliers = df[(df[feature] < lower) | (df[feature] > upper)]
print("Danceability outliers:", len(outliers))



# Then outliers in popularity with IQR method
pop_Q1 = df["album_popularity"].quantile(0.25)
pop_Q3 = df["album_popularity"].quantile(0.75)
pop_IQR = pop_Q3 - pop_Q1

pop_lower = pop_Q1 - 1.5 * pop_IQR
pop_upper = pop_Q3 + 1.5 * pop_IQR
pop_outliers = df[(df["album_popularity"] < pop_lower) | (df["album_popularity"] > pop_upper)]
print("Popularity outliers:", len(pop_outliers))
# Printing these outliers makes us see that none are found

