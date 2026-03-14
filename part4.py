import sqlite3
from datetime import datetime
from itertools import combinations
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

# Adds the parent directory to the search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Finds the database in the current folder or parent folder
def get_db_path():
    current_folder = os.path.dirname(__file__)
    candidate_1 = os.path.join(current_folder, "spotify_database.db")
    candidate_2 = os.path.join(current_folder, "..", "spotify_database.db")

    if os.path.exists(candidate_1):
        return candidate_1
    elif os.path.exists(candidate_2):
        return candidate_2
    else:
        raise FileNotFoundError("spotify_database.db was not found in the current folder or parent folder.")


# Opens a database connection
def get_connection():
    db_path = get_db_path()
    connection = sqlite3.connect(db_path)
    return connection


# Sort helper
def sort_by_count_desc(item):
    return item[1]


# Get all genre columns automatically
def get_genre_columns(df):
    cols = []
    for col in df.columns:
        if col.startswith("genre_"):
            cols.append(col)
    return cols


# Collect unique genres from one row
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


# Count genres in a subset
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


# Convert release date to decade
def to_decade(release_date):
    try:
        dt = datetime.strptime(str(release_date)[:10], "%Y-%m-%d")
        decade = (dt.year // 10) * 10
        return str(decade) + "s"
    except:
        return "Unknown"


# Part 4.1 Outliers and invalid records
def outliers_and_invalids():
    print("\n# Outliers and Invalid Records")

    con = get_connection()

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
    """, con)

    con.close()

    df_original = df.copy()

    df = df.dropna(subset=["track_id"])
    df = df[df["duration_ms"] > 0]

    features = ["danceability", "energy", "valence"]

    for col in features:
        df = df[(df[col] >= 0) & (df[col] <= 1)]

    df = df.drop_duplicates(subset=["track_id"])

    print("Original number of rows:", len(df_original))
    print("Cleaned number of rows:", len(df))
    print("Rows removed:", len(df_original) - len(df))

    feature = "danceability"
    q1 = df[feature].quantile(0.25)
    q3 = df[feature].quantile(0.75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = df[(df[feature] < lower) | (df[feature] > upper)]
    print("Danceability outliers:", len(outliers))

    pop_q1 = df["album_popularity"].quantile(0.25)
    pop_q3 = df["album_popularity"].quantile(0.75)
    pop_iqr = pop_q3 - pop_q1
    pop_lower = pop_q1 - 1.5 * pop_iqr
    pop_upper = pop_q3 + 1.5 * pop_iqr

    pop_outliers = df[(df["album_popularity"] < pop_lower) | (df["album_popularity"] > pop_upper)]
    print("Popularity outliers:", len(pop_outliers))


# Part 4.2 Album feature summary
def album_feature_summary(album_name):
    print("\n# Album Feature Summary")

    con = get_connection()

    features = [
        "danceability",
        "energy",
        "valence",
        "acousticness",
        "speechiness",
        "instrumentalness"
    ]

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
        WHERE LOWER(albums.album_name) = LOWER(?)
    """

    df_album = pd.read_sql(exact_query, con, params=(album_name,))

    if df_album.empty:
        suggest_query = """
            SELECT DISTINCT album_name
            FROM albums_data
            WHERE LOWER(album_name) LIKE LOWER(?)
            ORDER BY album_name
            LIMIT 50
        """
        related_names = pd.read_sql(suggest_query, con, params=(f"%{album_name}%",))
        con.close()

        if related_names.empty:
            print(f"No exact match for '{album_name}' and no album names contain it.")
        else:
            print(f"No exact match for '{album_name}'. Album names containing '{album_name}':")
            for name in related_names["album_name"]:
                print("-", name)

        return None

    con.close()

    num_tracks = df_album["total_tracks"].iloc[0]

    summary = df_album[features].agg(["mean", "std", "min", "max"]).T
    summary["number_of_tracks"] = num_tracks

    print(summary)

    selected_album = df_album["album_name"].iloc[0]
    safe_name = "".join(c for c in selected_album if c.isalnum() or c == " ").strip().replace(" ", "_")

    plt.figure()
    plt.bar(summary.index, summary["mean"], color="#E64A19")
    plt.title(f"Album Features (Mean) of {selected_album}")
    plt.xlabel("Feature")
    plt.ylabel("Mean value")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(f"{safe_name}_feature_profile.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved plot:", f"{safe_name}_feature_profile.png")
    return summary


# Part 4.3 Music over time
def music_over_time():
    print("\n# Music Over Time")

    con = get_connection()

    features = [
        "danceability",
        "energy",
        "valence",
        "acousticness",
        "tempo",
        "speechiness",
        "instrumentalness"
    ]

    df = pd.read_sql("""
        SELECT
            albums_data.release_date,
            albums_data.era,
            features_data.danceability,
            features_data.energy,
            features_data.valence,
            features_data.acousticness,
            features_data.tempo,
            features_data.speechiness,
            features_data.instrumentalness
        FROM albums_data
        JOIN features_data
            ON albums_data.track_id = features_data.id
        WHERE albums_data.release_date IS NOT NULL
    """, con)

    con.close()

    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df = df.dropna(subset=["release_date"])

    daily_means = df.groupby(df["release_date"].dt.date)[features].mean().reset_index().sort_values("release_date")
    print("Daily averages example:")
    print(daily_means.head())

    plt.figure()
    plt.plot(daily_means["release_date"], daily_means["energy"], linewidth=0.5)
    plt.title("Example Feature (Energy) Over Time - Daily Average")
    plt.xlabel("Release Date")
    plt.ylabel("Average Energy")
    plt.tight_layout()
    plt.savefig("Example_daily_noise.png", dpi=300, bbox_inches="tight")
    plt.close()

    yearly_means = df.groupby(df["release_date"].dt.year)[features].mean().reset_index().sort_values("release_date")

    for feature in features:
        plt.figure()
        plt.plot(yearly_means["release_date"], yearly_means[feature], color="#4C72B0")
        plt.title(f"{feature.capitalize()} Over Time - Yearly Average")
        plt.xlabel("Year")
        plt.ylabel(f"Average {feature}")
        plt.tight_layout()
        plt.savefig(f"{feature}_over_time.png", dpi=300, bbox_inches="tight")
        plt.close()

    era_means = df.groupby("era")[features].mean().sort_index()
    print("\nAverage feature values by era:")
    print(era_means)

    for feature in features:
        plt.figure()
        plt.bar(era_means.index, era_means[feature], color="#E64A19")
        plt.title(f"Average {feature} by Era")
        plt.xlabel("Era")
        plt.ylabel(f"Average {feature}")
        plt.tight_layout()
        plt.savefig(f"Era_{feature}.png", dpi=300, bbox_inches="tight")
        plt.close()


# Part 4.4 Duplicates in artist_data
def dupes_artists_data():
    print("\n# Duplicates in artist_data")

    con = get_connection()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM artist_data")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])

    con.close()

    df["name_lower"] = df["name"].str.lower().str.strip()
    df_sorted = df.sort_values(by=["name_lower", "followers"], ascending=[True, False])
    df_cleaned = df_sorted.drop_duplicates(subset=["name_lower"], keep="first").copy()
    df_cleaned["name"] = df_cleaned["name"].str.title()
    df_cleaned = df_cleaned.drop(columns=["name_lower"])

    print("Original rows:", len(df))
    print("Rows after removing duplicates:", len(df_cleaned))
    print("Duplicates removed:", len(df) - len(df_cleaned))

    print("\nExample cleaned rows:")
    print(df_cleaned.head())


# Part 4.5 Most frequent genre pairs
def most_frequent_genre_pairs():
    print("\n# Most Frequent Genre Pairs")

    con = get_connection()

    artists = pd.read_sql("""
    SELECT
        id AS artist_id,
        genre_0, genre_1, genre_2, genre_3, genre_4
    FROM artist_data
    """, con)

    con.close()

    genre_cols = get_genre_columns(artists)
    pair_counts = {}

    for i in range(len(artists)):
        row = artists.iloc[i]
        genres = collect_unique_genres(row, genre_cols)

        if len(genres) >= 2:
            for pair in combinations(genres, 2):
                if pair in pair_counts:
                    pair_counts[pair] += 1
                else:
                    pair_counts[pair] = 1

    pair_items = list(pair_counts.items())
    pair_items.sort(key=sort_by_count_desc, reverse=True)
    top_pairs = pair_items[:10]

    for pair, count in top_pairs:
        print(pair, "->", count)

    pair_labels = []
    pair_values = []

    for pair, count in top_pairs:
        label = pair[0] + " & " + pair[1]
        pair_labels.append(label)
        pair_values.append(count)

    plt.figure(figsize=(10, 6))
    plt.barh(pair_labels, pair_values, color="#E64A19")
    plt.xlabel("Frequency (artists)")
    plt.title("Top Genre Pairs Appearing Together Most Frequently")
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig("Top_Genre_Pairs.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved plot: Top_Genre_Pairs.png")


# Part 4.6 Genre frequency based on feature score
def genre_frequency_based_on_score(feature_name="danceability"):
    print("\n# Genre Frequency Based on Feature Score")

    con = get_connection()

    tracks_cols = pd.read_sql("PRAGMA table_info(tracks_data);", con)
    artists_cols = pd.read_sql("PRAGMA table_info(artist_data);", con)
    features_cols = pd.read_sql("PRAGMA table_info(features_data);", con)
    albums_cols = pd.read_sql("PRAGMA table_info(albums_data);", con)

    tracks_columns = list(tracks_cols["name"])
    artists_columns = list(artists_cols["name"])
    albums_columns = list(albums_cols["name"])

    print("# tracks_data columns:", tracks_columns)
    print("# artist_data columns:", artists_columns)
    print("# features_data columns:", list(features_cols["name"]))
    print("# albums_data columns:", albums_columns)

    track_link_col = None
    possible_track_cols = ["track_id", "tracks_id", "id_track", "track", "trackid"]

    for col in possible_track_cols:
        if col in albums_columns:
            track_link_col = col

    if track_link_col is None:
        for col in albums_columns:
            if "track" in col.lower():
                track_link_col = col
                break

    if track_link_col is None:
        con.close()
        raise ValueError("Could not find a track link column in albums_data.")

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

    if artist_link_col is None:
        for col in albums_columns:
            if "artist" in col.lower():
                artist_link_col = col
                if "name" in artists_columns:
                    artist_join_mode = "name"
                else:
                    artist_join_mode = "id"
                break

    if artist_link_col is None:
        con.close()
        raise ValueError("Could not find an artist link column in albums_data.")

    genre_select = "ar.genre_0, ar.genre_1, ar.genre_2, ar.genre_3, ar.genre_4, ar.genre_5, ar.genre_6"

    if artist_join_mode == "id":
        query = f"""
        SELECT
            t.id AS track_id,
            f.{feature_name} AS feature_value,
            {genre_select}
        FROM tracks_data t
        JOIN features_data f
            ON t.id = f.id
        JOIN albums_data al
            ON t.id = al.{track_link_col}
        JOIN artist_data ar
            ON al.{artist_link_col} = ar.id
        WHERE f.{feature_name} IS NOT NULL
        """
    else:
        query = f"""
        SELECT
            t.id AS track_id,
            f.{feature_name} AS feature_value,
            {genre_select}
        FROM tracks_data t
        JOIN features_data f
            ON t.id = f.id
        JOIN albums_data al
            ON t.id = al.{track_link_col}
        JOIN artist_data ar
            ON al.{artist_link_col} = ar.name
        WHERE f.{feature_name} IS NOT NULL
        """

    df = pd.read_sql(query, con)
    con.close()

    df = df.dropna(subset=["feature_value"])

    labels = ["very low", "low", "medium", "high", "very high"]
    df["feature_level"] = pd.qcut(df["feature_value"], q=5, labels=labels)

    genre_cols = get_genre_columns(df)
    very_low_df = df[df["feature_level"] == "very low"]
    very_high_df = df[df["feature_level"] == "very high"]

    low_counts = count_genres(very_low_df, genre_cols)[:10]
    high_counts = count_genres(very_high_df, genre_cols)[:10]

    print("\nTop genres among VERY LOW", feature_name, "tracks:")
    for g, c in low_counts:
        print(g, "->", c)

    print("\nTop genres among VERY HIGH", feature_name, "tracks:")
    for g, c in high_counts:
        print(g, "->", c)

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

    plt.subplot(1, 2, 1)
    plt.barh(low_genres, low_values, color="#4C72B0")
    plt.title("Top Genres: VERY LOW " + feature_name)
    plt.xlabel("Count")
    plt.gca().invert_yaxis()

    plt.subplot(1, 2, 2)
    plt.barh(high_genres, high_values, color="#E64A19")
    plt.title("Top Genres: VERY HIGH " + feature_name)
    plt.xlabel("Count")
    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.savefig("genres_very_low_vs_very_high.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved plot: genres_very_low_vs_very_high.png")


# Part 4.7 Popularity vs tempo
def popularity_vs_tempo():
    print("\n# Popularity vs Tempo")

    con = get_connection()
    cursor = con.cursor()

    cursor.execute("SELECT id, tempo FROM features_data")
    rows = cursor.fetchall()
    df_tempo = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])

    cursor.execute("SELECT id, track_popularity FROM tracks_data")
    rows = cursor.fetchall()
    df_tracks = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])

    df_track_pop = pd.merge(df_tempo, df_tracks, how="inner")

    cursor.execute("SELECT track_id, track_name FROM albums_data")
    rows = cursor.fetchall()
    df_song = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])

    con.close()

    df_song_pop = pd.merge(df_song, df_track_pop, left_on="track_id", right_on="id", how="inner")
    df_song_pop = df_song_pop.drop(columns=["id", "track_id"])
    df_song_pop = df_song_pop.sort_values(by=["track_popularity"], ascending=False)
    df_song_pop = df_song_pop[df_song_pop["tempo"] > 0]

    df_plot = df_song_pop.dropna(subset=["tempo", "track_popularity"])
    x = df_plot["tempo"]
    y = df_plot["track_popularity"]

    plt.figure()
    plt.scatter(x, y, s=1, alpha=0.2, color="tab:blue")
    plt.title("Correlation: Tempo vs Track Popularity")
    plt.xlabel("Tempo (BPM)")
    plt.ylabel("Popularity (0-100)")
    plt.tight_layout()
    plt.savefig("tempo_popularity.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved plot: tempo_popularity.png")


# Main
def main():
    outliers_and_invalids()
    album_feature_summary("An Innocent Man")
    music_over_time()
    dupes_artists_data()
    most_frequent_genre_pairs()
    genre_frequency_based_on_score("danceability")
    popularity_vs_tempo()


if __name__ == "__main__":
    main()