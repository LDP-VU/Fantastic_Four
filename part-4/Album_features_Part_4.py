import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Adds the parent directory to the search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

features = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "speechiness",
    "instrumentalness"
]

# Function to summarize features for a given album
def album_feature_summary(album_name):

    connection = sqlite3.connect("spotify_database.db")

    # seeing if there is an exact match for album name
    exact_query = """
        SELECT
            albums.album_name,
            albums.track_id,
            albums.total_tracks,
            features.danceability,
            features.energy,
            features.valence,
            features.acousticness,
            features.speechiness,
            features.instrumentalness
        FROM albums_data AS albums
        JOIN features_data AS features
            ON albums.track_id = features.id
        WHERE LOWER(albums.album_name) = LOWER(?) """
    df_album = pd.read_sql(exact_query, connection, params=(album_name,))

    # If no exact match the output a list of relateed suggestions
    if df_album.empty:
        suggest_query = """
            SELECT DISTINCT album_name
            FROM albums_data
            WHERE LOWER(album_name) LIKE LOWER(?)
            ORDER BY album_name
            LIMIT 50 """
        related_names = pd.read_sql(
            suggest_query,
            connection,
            params=(f"%{album_name}%",)
        )
        connection.close()

        if related_names.empty:
            print(f"No exact match for '{album_name}' and no album names contain it.")
        else:
            print(f"No exact match for '{album_name}'. Album names containing '{album_name}':")
            for name in related_names["album_name"]:
                print("-", name)
        return None

    connection.close()

    # Number of tracks in the album
    num_tracks = df_album["total_tracks"].iloc[0]

    # Summary statistics of features for album
    summary = (df_album[features].agg(["mean", "std", "min", "max"]).T)
    summary["number_of_tracks"] = num_tracks

    # Plotting mean value for each feature in album
    selected_album = df_album["album_name"].iloc[0]
    safe_name = "".join(c for c in selected_album if c.isalnum() or c in (" ")).strip().replace(" ", "_")

    plt.figure()
    plt.bar(summary.index, summary["mean"])
    plt.title(f"Album features (mean) of {selected_album}")
    plt.xlabel("Feature")
    plt.ylabel("Mean value")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(f"{safe_name}_feature_profile.png")
    plt.close()
    
    return summary

# Working Example usage  
print("\nAlbum name: An Innocent Man")
print(album_feature_summary("An Innocent Man"))

# Error example usage 
print("\nAlbum name: Goodbye Yellow Brick Road")
print(album_feature_summary("Goodbye Yellow Brick Road"))

# Single song on album example usage
print("\nAlbum name: Queen")
print(album_feature_summary("Queen"))
