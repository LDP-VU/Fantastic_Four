import sqlite3
import pandas as pd
from itertools import combinations
import matplotlib.pyplot as plt
import sys
import os

# Adds the parent directory to the search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

# Settings
DB_FILE = "spotify_database.db"
TOP_K_PAIRS = 10

def sort_by_count_desc(item):
    return item[1]

def get_genre_columns(df):
    cols = []
    for col in df.columns:
        if col.startswith("genre_"):
            cols.append(col)
    return cols

def collect_unique_genres(row, genre_cols):
    genres = []
    for col in genre_cols:
        g = row[col]
        if pd.notna(g):
            g = str(g).strip()
            if g != "" and g not in genres:
                genres.append(g)
    genres.sort()
    return genres

# Connect
con = sqlite3.connect(DB_FILE)

query = """
SELECT
    id AS artist_id,
    genre_0, genre_1, genre_2, genre_3, genre_4
FROM artist_data
"""
artists = pd.read_sql(query, con)
con.close()

genre_cols = get_genre_columns(artists)

pair_counts = {}

for i in range(len(artists)):
    row = artists.iloc[i]
    genres = collect_unique_genres(row, genre_cols)

    # Only create pairs if at least 2 genres exist
    if len(genres) >= 2:
        for pair in combinations(genres, 2):
            if pair in pair_counts:
                pair_counts[pair] += 1
            else:
                pair_counts[pair] = 1

pair_items = list(pair_counts.items())
pair_items.sort(key=sort_by_count_desc, reverse=True)

top_pairs = pair_items[:TOP_K_PAIRS]

# pairing using &
pair_labels = []
pair_values = []

for pair, count in top_pairs:
    label = pair[0] + " & " + pair[1]
    pair_labels.append(label)
    pair_values.append(count)

# Plot
plt.figure(figsize=(10, 6))
plt.barh(pair_labels, pair_values, color="#E64A19")
plt.xlabel("Frequency (artists)")
plt.title("Top Genre Pairs Appearing Together Most Frequently")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("Top_Genre_Pairs.png")
plt.close()