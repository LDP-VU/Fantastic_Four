import sqlite3
import pandas as pd
import sys
import os



def get_top_artists_by_feature(feature, top_percent=10):
   
    # Adds the parent directory to the search path
    db_path = os.path.join(os.path.dirname(__file__), "..", "spotify_database.db")
    conn = sqlite3.connect(db_path)

    # We'll look at feature danceability
    feature = feature

    # We'll take every track in albums and join them to one DataFrame
    # with info of artists and danceability
    df = pd.read_sql(f"""
            SELECT albums_data.track_name,
            albums_data.artist_0,
            albums_data.artist_1,
            albums_data.artist_2,
            features_data.{feature}
            FROM albums_data
            JOIN features_data
            ON albums_data.track_id = features_data.id
            """, conn)  


    # We find top 10% of tracks with the highest danceability
    top_10_percent = df[feature].quantile(0.9)
    most_danceable_tracks = df[df[feature] >= top_10_percent]
    print(most_danceable_tracks[["track_name", "artist_0", feature]].sort_values(by=feature, ascending=False).head(20))

    # We combine these top 10% artists into one column 
    artists_df = most_danceable_tracks[["artist_0", "artist_1", "artist_2"]]
    artists_no_nan = artists_df.apply(lambda row: row.dropna(), axis=1)
    artists_joined = artists_no_nan.apply(lambda row: ", ".join(row), axis=1)

    # We split collaborations into separate rows
    most_danceable_tracks["artists"] = artists_joined
    expanded = most_danceable_tracks.assign(
        artist=most_danceable_tracks["artists"].str.split(", ")
    ).explode("artist")

    # Let's see artists with most dancable songs
    artist_counts = expanded.groupby("artist").size().sort_values(ascending=False)
    print(artist_counts.head(20))


    # Let's then print the artists in the top 10% of most danceable tracks
    artist_stats = expanded.groupby("artist").agg(
        avg_feature=(feature, "mean"),
        num_tracks=(feature, "count")
    ).sort_values(by="avg_feature", ascending=False)

    print(artist_stats.head(20))
    
    conn.close()
    
    return {
        'most_danceable_tracks': most_danceable_tracks,
        'artist_counts': artist_counts,
        'artist_stats': artist_stats,
        'expanded': expanded
    }


