import sqlite3
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
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


# Converts explicit values to 1 or 0
def convert_explicit(value):
    val_string = str(value).lower().strip()

    if val_string == "true":
        return 1
    elif val_string == "false":
        return 0
    else:
        return 0


# Checks whether a row is a collaboration
def is_collaboration(row):
    a1 = str(row["artist_1"]).strip().lower()

    if a1 != "none" and a1 != "":
        return True
    else:
        return False


# Converts release date to era
def to_decade(release_date):
    try:
        dt = datetime.strptime(str(release_date)[:10], "%Y-%m-%d")
        decade = (dt.year // 10) * 10
        return str(decade) + "s"
    except:
        return "Unknown"


# Part 3.1 Explicit tracks more popular?
def explicit_vs_popularity():
    print("\n# Explicit vs Popularity")

    con = get_connection()

    query = """
    SELECT track_popularity, explicit
    FROM tracks_data
    WHERE track_popularity IS NOT NULL
    AND explicit IS NOT NULL
    """

    df = pd.read_sql(query, con)
    con.close()

    df["explicit_num"] = df["explicit"].apply(convert_explicit)

    explicit_mean = df[df["explicit_num"] == 1]["track_popularity"].mean()
    non_explicit_mean = df[df["explicit_num"] == 0]["track_popularity"].mean()

    print("Average popularity (Explicit tracks):", round(explicit_mean, 2))
    print("Average popularity (Non-explicit tracks):", round(non_explicit_mean, 2))

    corr = df["explicit_num"].corr(df["track_popularity"])
    print("Correlation between explicit and popularity:", round(corr, 3))

    x = sm.add_constant(df["explicit_num"])
    y = df["track_popularity"]

    model = sm.OLS(y, x).fit()

    print("Regression parameters:")
    print(model.params)

    plt.figure()
    means = [non_explicit_mean, explicit_mean]
    labels = ["Non-explicit", "Explicit"]
    colors = ["#4C72B0", "#E64A19"]

    plt.bar(labels, means, color=colors)
    plt.title("Average Popularity: Explicit vs Non-explicit Tracks")
    plt.ylabel("Average Track Popularity")
    plt.tight_layout()
    plt.savefig("Explicit_vs_Popularity_barplot.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved plot: Explicit_vs_Popularity_barplot.png")


# Part 3.2 Which artists have the highest proportion of explicit tracks?
def explicit_proportion():
    print("\n# Explicit Proportion by Artist")

    con = get_connection()
    cursor = con.cursor()

    query_explicit = "SELECT id, explicit FROM tracks_data"
    cursor.execute(query_explicit)
    rows = cursor.fetchall()
    df_explicit = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])

    query_artist = "SELECT track_id, artist_0 FROM albums_data"
    cursor.execute(query_artist)
    rows = cursor.fetchall()
    df_artist = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])

    con.close()

    combined_df = pd.merge(df_explicit, df_artist, left_on="id", right_on="track_id", how="inner")
    combined_df["explicit_num"] = combined_df["explicit"].apply(convert_explicit)

    artists_stats = combined_df.groupby("artist_0")["explicit_num"].agg(["mean", "count"])
    top_artists = artists_stats[artists_stats["count"] >= 50]
    result = top_artists.sort_values(by="mean", ascending=False)

    print(result.head(10))


# Part 3.3 Are collaborations more popular?
def collaborations_vs_popularity():
    print("\n# Collaborations vs Popularity")

    con = get_connection()
    cursor = con.cursor()

    query_popularity = "SELECT id, track_popularity FROM tracks_data"
    cursor.execute(query_popularity)
    rows = cursor.fetchall()
    df_track_popularity = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])

    query_collab = "SELECT track_id, artist_0, artist_1 FROM albums_data"
    cursor.execute(query_collab)
    rows = cursor.fetchall()
    df_collab = pd.DataFrame(rows, columns=[x[0] for x in cursor.description])

    con.close()

    df_collab_pop = pd.merge(df_collab, df_track_popularity, left_on="track_id", right_on="id", how="inner")
    df_collab_pop["is_collab"] = df_collab_pop.apply(is_collaboration, axis=1)

    results = df_collab_pop.groupby("is_collab")["track_popularity"].mean()

    print(results)

    mean_solo = results[False]
    mean_collab = results[True]

    plt.figure()
    labels = ["Solo", "Collaboration"]
    values = [mean_solo, mean_collab]
    colors = ["#4C72B0", "#E64A19"]

    plt.bar(labels, values, color=colors)
    plt.title("Average Track Popularity: Solo vs Collaboration")
    plt.ylabel("Average Track Popularity")
    plt.tight_layout()
    plt.savefig("Collaboration_vs_Popularity_barplot.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved plot: Collaboration_vs_Popularity_barplot.png")


# Part 3.4 Relationship between album popularity and artist popularity
def album_popularity_vs_artist_popularity():
    print("\n# Album Popularity vs Artist Popularity")

    con = get_connection()

    query = """
    SELECT 
        a.album_name,
        a.album_popularity,
        ar.name AS artist_name,
        ar.artist_popularity
    FROM albums_data AS a
    JOIN artist_data AS ar
        ON a.artist_id = ar.id
    WHERE a.album_popularity IS NOT NULL
    AND ar.artist_popularity IS NOT NULL
    """

    df = pd.read_sql(query, con)
    con.close()

    corr = df["album_popularity"].corr(df["artist_popularity"])
    print("Correlation between album popularity and artist popularity:", round(corr, 3))

    x = sm.add_constant(df["artist_popularity"])
    y = df["album_popularity"]

    model = sm.OLS(y, x).fit()

    print("Regression parameters:")
    print(model.params)

    plt.figure()
    plt.scatter(df["artist_popularity"], df["album_popularity"], alpha=0.3)

    x_values = np.linspace(df["artist_popularity"].min(), df["artist_popularity"].max(), 100)
    y_values = model.params["const"] + model.params["artist_popularity"] * x_values

    plt.plot(x_values, y_values, color="black", linewidth=2)
    plt.title("Album Popularity vs Artist Popularity")
    plt.xlabel("Artist Popularity")
    plt.ylabel("Album Popularity")
    plt.tight_layout()
    plt.savefig("Album_vs_Artist_regression_plot.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved plot: Album_vs_Artist_regression_plot.png")


# Part 3.5 Top 10% of a chosen feature
def best_features(feature="danceability"):
    print("\n# Best Tracks by Feature:", feature)

    con = get_connection()

    query = f"""
    SELECT albums_data.track_name,
           albums_data.artist_0,
           albums_data.artist_1,
           albums_data.artist_2,
           features_data.{feature}
    FROM albums_data
    JOIN features_data
        ON albums_data.track_id = features_data.id
    """

    df = pd.read_sql(query, con)
    con.close()

    top_10_percent = df[feature].quantile(0.9)
    most_featured_tracks = df[df[feature] >= top_10_percent]

    print("Top 20 tracks in top 10% for", feature)
    print(most_featured_tracks[["track_name", "artist_0", feature]].sort_values(by=feature, ascending=False).head(20))

    all_artists = []

    for i in range(len(most_featured_tracks)):
        row = most_featured_tracks.iloc[i]

        for col in ["artist_0", "artist_1", "artist_2"]:
            artist_name = row[col]

            if pd.notna(artist_name):
                artist_name = str(artist_name).strip()

                if artist_name != "" and artist_name.lower() != "none":
                    all_artists.append(artist_name)

    artist_counts = pd.Series(all_artists).value_counts()

    print("\nArtists that appear most in the top 10% of", feature)
    print(artist_counts.head(20))


# Part 3.6 Era analysis
def eras_analysis():
    print("\n# Era Analysis")

    con = get_connection()
    cursor = con.cursor()

    query = "SELECT * FROM albums_data LIMIT 1"
    cursor.execute(query)
    columns = [c[0] for c in cursor.description]
    row = cursor.fetchone()
    row_dict = dict(zip(columns, row))

    print("Sample columns and values:")
    for col, value in row_dict.items():
        print(col, ":", value)

    try:
        query_add = "ALTER TABLE albums_data ADD COLUMN era TEXT"
        cursor.execute(query_add)
        con.commit()
        print("Added column: era")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column 'era' already exists")
        else:
            raise

    cursor.execute("SELECT rowid, release_date FROM albums_data")
    rows = cursor.fetchall()

    decades = []

    for row in rows:
        rowid = row[0]
        release_date = row[1]
        era = to_decade(release_date)
        decades.append((era, rowid))

    for row in decades:
        cursor.execute("UPDATE albums_data SET era = ? WHERE rowid = ?", row)

    con.commit()

    query = """
    SELECT era, AVG(album_popularity) AS avg_album_popularity
    FROM albums_data
    WHERE era != 'Unknown'
    GROUP BY era
    ORDER BY era
    """
    df_pop_era = pd.read_sql(query, con)

    plt.figure()
    plt.plot(df_pop_era["era"], df_pop_era["avg_album_popularity"], marker="o")
    plt.xticks(rotation=45)
    plt.title("Average Album Popularity by Era")
    plt.ylabel("Average Popularity")
    plt.xlabel("Era")
    plt.tight_layout()
    plt.savefig("Era_vs_avgPop.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved plot: Era_vs_avgPop.png")

    query = """
    SELECT era, AVG(duration_ms) / 60000.0 AS avg_minutes
    FROM albums_data
    WHERE era != 'Unknown'
    GROUP BY era
    ORDER BY era
    """
    df_duration_era = pd.read_sql(query, con)

    plt.figure()
    plt.plot(df_duration_era["era"], df_duration_era["avg_minutes"], marker="o")
    plt.xticks(rotation=45)
    plt.title("Average Album Duration by Era")
    plt.ylabel("Average Duration (minutes)")
    plt.xlabel("Era")
    plt.tight_layout()
    plt.savefig("Era_vs_avgDuration.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved plot: Era_vs_avgDuration.png")

    con.close()


# Part 3.7 Album feature summary
def album_features(album_name="Nadie Sabe Lo Que Va A Pasar Mañana"):
    print("\n# Album Feature Summary")

    con = get_connection()

    print("Most popular albums:")
    print(pd.read_sql("""
    SELECT DISTINCT album_name, album_popularity
    FROM albums_data
    ORDER BY album_popularity DESC
    LIMIT 15;
    """, con))

    album_id_df = pd.read_sql(f"""
    SELECT DISTINCT album_id
    FROM albums_data
    WHERE album_name = '{album_name}'
    """, con)

    album_id = album_id_df.iloc[0, 0]

    df_album = pd.read_sql(f"""
    SELECT albums_data.track_name,
           features_data.danceability,
           features_data.energy,
           features_data.loudness,
           features_data.valence,
           features_data.tempo
    FROM albums_data
    JOIN features_data
        ON albums_data.track_id = features_data.id
    WHERE albums_data.album_id = '{album_id}'
    """, con)

    con.close()

    print("Feature summary for album:", album_name)
    print(df_album.describe())

    df_album.set_index("track_name")[["danceability", "loudness"]].plot(kind="bar", figsize=(12, 6))
    plt.title("Feature Variation Across Tracks in " + album_name)
    plt.ylabel("Feature Value")
    file_name = "feature_variation_" + album_name.replace(" ", "_") + ".png"
    plt.tight_layout()
    plt.savefig(file_name, dpi=300, bbox_inches="tight")
    plt.close()

    print("Saved plot:", file_name)


# Main function
def main():
    explicit_vs_popularity()
    explicit_proportion()
    collaborations_vs_popularity()
    album_popularity_vs_artist_popularity()
    best_features("danceability")
    eras_analysis()
    album_features("Nadie Sabe Lo Que Va A Pasar Mañana")


if __name__ == "__main__":
    main()