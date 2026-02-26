import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# Settings
DB_FILE = "spotify_database.db"
FEATURE_NAME = "danceability"   # Change to: energy, loudness, valence, etc.
TOP_K_GENRES = 10

# Helper
def sort_by_count_desc(item):
    return item[1]

def get_genre_columns(df):
    cols = []
    for col in df.columns:
        if col.startswith("genre_"):
            cols.append(col)
    return cols

def count_genres(subset_df, genre_cols):
    counts = {}

    for i in range(len(subset_df)):
        row = subset_df.iloc[i]
        for col in genre_cols:
            g = row[col]
            if pd.notna(g):
                g = str(g).strip()
                if g != "":
                    if g in counts:
                        counts[g] += 1
                    else:
                        counts[g] = 1

    items = list(counts.items())
    items.sort(key=sort_by_count_desc, reverse=True)
    return items

# Connect
con = sqlite3.connect(DB_FILE)

# Inspect columns so we can find the join keys
tracks_cols = pd.read_sql("PRAGMA table_info(tracks_data);", con)
artists_cols = pd.read_sql("PRAGMA table_info(artist_data);", con)
features_cols = pd.read_sql("PRAGMA table_info(features_data);", con)
albums_cols = pd.read_sql("PRAGMA table_info(albums_data);", con)

tracks_columns = list(tracks_cols["name"])
artists_columns = list(artists_cols["name"])
features_columns = list(features_cols["name"])
albums_columns = list(albums_cols["name"])

print("# tracks_data columns:", tracks_columns)
print("# artist_data columns:", artists_columns)
print("# features_data columns:", features_columns)
print("# albums_data columns:", albums_columns)
print()

# Step 1: Find track id column in albums_data
# We need albums_data.<something> = tracks_data.id
track_link_col = None
possible_track_cols = ["track_id", "tracks_id", "id_track", "track", "trackid"]

for col in possible_track_cols:
    if col in albums_columns:
        track_link_col = col

# If not found, try a generic search for a column containing "track"
if track_link_col is None:
    for col in albums_columns:
        if "track" in col.lower():
            track_link_col = col
            break

if track_link_col is None:
    con.close()
    raise ValueError("Could not find a track link column in albums_data (e.g., track_id).")

print("# Using albums_data track link column:", track_link_col)

# Step 2: Find artist link column in albums_data
# Option A: albums_data has artist_id -> join to artist_data.id
# Option B: albums_data has artist name -> join to artist_data.name
artist_link_col = None
artist_join_mode = None

if "artist_id" in albums_columns:
    artist_link_col = "artist_id"
    artist_join_mode = "id"
elif "artists_id" in albums_columns:
    artist_link_col = "artists_id"
    artist_join_mode = "id"
elif "artist" in albums_columns and "name" in artists_columns:
    artist_link_col = "artist"
    artist_join_mode = "name"
elif "artists" in albums_columns and "name" in artists_columns:
    artist_link_col = "artists"
    artist_join_mode = "name"

# If still not found, try searching for columns containing "artist"
if artist_link_col is None:
    for col in albums_columns:
        if "artist" in col.lower():
            artist_link_col = col
            # If artist_data has name, try name join; otherwise assume id join
            if "name" in artists_columns:
                artist_join_mode = "name"
            else:
                artist_join_mode = "id"
            break

if artist_link_col is None:
    con.close()
    raise ValueError("Could not find an artist link column in albums_data (e.g., artist_id or artist name).")

print("# Using albums_data artist link column:", artist_link_col)
print("# Artist join mode:", artist_join_mode)
print()

# Step 3: Build query using albums_data as the bridge
genre_select = "ar.genre_0, ar.genre_1, ar.genre_2, ar.genre_3, ar.genre_4, ar.genre_5, ar.genre_6"

if artist_join_mode == "id":
    query = f"""
    SELECT
        t.id AS track_id,
        f.{FEATURE_NAME} AS feature_value,
        {genre_select}
    FROM tracks_data t
    JOIN features_data f
        ON t.id = f.id
    JOIN albums_data al
        ON t.id = al.{track_link_col}
    JOIN artist_data ar
        ON al.{artist_link_col} = ar.id
    WHERE f.{FEATURE_NAME} IS NOT NULL
    """
else:
    query = f"""
    SELECT
        t.id AS track_id,
        f.{FEATURE_NAME} AS feature_value,
        {genre_select}
    FROM tracks_data t
    JOIN features_data f
        ON t.id = f.id
    JOIN albums_data al
        ON t.id = al.{track_link_col}
    JOIN artist_data ar
        ON al.{artist_link_col} = ar.name
    WHERE f.{FEATURE_NAME} IS NOT NULL
    """

df = pd.read_sql(query, con)
con.close()

# Step 4: Bin feature into very low ... very high
df = df.dropna(subset=["feature_value"])

labels = ["very low", "low", "medium", "high", "very high"]
df["feature_level"] = pd.qcut(df["feature_value"], q=5, labels=labels)

genre_cols = get_genre_columns(df)

very_low_df = df[df["feature_level"] == "very low"]
very_high_df = df[df["feature_level"] == "very high"]

low_counts = count_genres(very_low_df, genre_cols)[:TOP_K_GENRES]
high_counts = count_genres(very_high_df, genre_cols)[:TOP_K_GENRES]

print("# Top genres among VERY LOW", FEATURE_NAME, "tracks:")
for g, c in low_counts:
    print(g, "->", c)

print("\n# Top genres among VERY HIGH", FEATURE_NAME, "tracks:")
for g, c in high_counts:
    print(g, "->", c)

# Step 5: Plot comparison
low_genres = []
low_values = []
for g, c in low_counts:
    low_genres.append(g)
    low_values.append(c)

high_genres = []
high_values = []
for g, c in high_counts:
    high_genres.append(g)
    high_values.append(c)

plt.figure(figsize=(12, 6))

# Very low plot
plt.subplot(1, 2, 1)
plt.barh(low_genres, low_values, color="#4C72B0")
plt.title("Top Genres: VERY LOW " + FEATURE_NAME)
plt.xlabel("Count")
plt.gca().invert_yaxis()

# Very high plot
plt.subplot(1, 2, 2)
plt.barh(high_genres, high_values, color="#E64A19")
plt.title("Top Genres: VERY HIGH " + FEATURE_NAME)
plt.xlabel("Count")
plt.gca().invert_yaxis()

plt.tight_layout()
plt.savefig("genres_very_low_vs_very_high.png", dpi=300, bbox_inches="tight")
plt.close()
