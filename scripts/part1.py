import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import sys
import os

# Adds the parent directory to the search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Load dataset
def load_data():
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'artist_data.csv'))
    return df


# Basic inspection of the dataset
def basic_data_inspection(df):
    print("# Basic Data Inspection")
    print()

    print("Columns:")
    print(df.columns)
    print()

    print("Data types:")
    print(df.dtypes)
    print()

    unique_artists = df["name"].nunique()
    print("Number of unique artists:", unique_artists)
    print()

    # Top 10 artists by popularity
    top_popularity = df.sort_values("artist_popularity", ascending=False).head(10)

    plt.figure()
    plt.bar(top_popularity["name"], top_popularity["artist_popularity"], color="#E64A19")
    plt.xticks(rotation=90)
    plt.title("Top 10 Artists by Popularity")
    plt.xlabel("Artist")
    plt.ylabel("Popularity")
    plt.tight_layout()
    plt.savefig("Top_Popularity_bar_chart.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Top 10 artists by popularity:")
    print(top_popularity[["name", "artist_popularity"]])
    print()

    # Top 10 artists by followers
    top_followers = df.sort_values("followers", ascending=False).head(10)

    plt.figure()
    plt.bar(top_followers["name"], top_followers["followers"], color="#4C72B0")
    plt.xticks(rotation=90)
    plt.title("Top 10 Artists by Followers")
    plt.xlabel("Artist")
    plt.ylabel("Followers")
    plt.tight_layout()
    plt.savefig("Top_Followers_bar_chart.png", dpi=300, bbox_inches="tight")
    plt.close()

    print("Top 10 artists by followers:")
    print(top_followers[["name", "followers"]])
    print()


# Popularity vs followers analysis
def popularity_vs_followers(df):
    print("# Popularity vs Followers")
    print()

    df_clean = df.dropna(subset=["followers", "artist_popularity"]).copy()

    # Correlation
    corr = df_clean["followers"].corr(df_clean["artist_popularity"])
    print("Correlation between followers and popularity:", corr)
    print()

    # Scatter plot
    plt.figure()
    plt.scatter(df_clean["followers"], df_clean["artist_popularity"], alpha=0.5, color="#4C72B0")
    plt.title("Followers vs Popularity")
    plt.xlabel("Followers")
    plt.ylabel("Popularity")
    plt.tight_layout()
    plt.savefig("Followers_Popularity_scatter_plot.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Linear regression model
    df_clean["followers_log"] = np.log(df_clean["followers"] + 1)
    x = sm.add_constant(df_clean["followers_log"])
    y = df_clean["artist_popularity"]

    model = sm.OLS(y, x).fit()

    print("Parameters of the model:")
    print(model.params)
    print()

    # Scatter + regression line
    plt.figure()
    plt.scatter(df_clean["followers_log"], df_clean["artist_popularity"], alpha=0.2, color="#E64A19")

    x_values = np.linspace(df_clean["followers_log"].min(), df_clean["followers_log"].max(), 100)
    y_values = model.params["const"] + model.params["followers_log"] * x_values

    plt.plot(x_values, y_values, color="black", linewidth=1)
    plt.title("Linear Regression of Popularity on log(Followers)")
    plt.xlabel("log(Followers)")
    plt.ylabel("Popularity")
    plt.tight_layout()
    plt.savefig("log_followers_popularity_scatter_plot.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Overperformers and legacy artists
    df_clean["predicted_popularity"] = model.predict(x)
    df_clean["residual"] = df_clean["artist_popularity"] - df_clean["predicted_popularity"]

    overperformers = df_clean.sort_values("residual", ascending=False).head(10)
    legacy_artists = df_clean.sort_values("residual").head(10)

    print("Top 10 overperformers (high popularity, low followers):")
    print(overperformers[["name", "followers", "artist_popularity", "residual"]])
    print()

    print("Top 10 legacy artists (low popularity, high followers):")
    print(legacy_artists[["name", "followers", "artist_popularity", "residual"]])
    print()


# Genre analysis
def top_10_by_genre(genre_name, data, genre_cols):
    matches = []

    for i in range(len(data)):
        row = data.iloc[i]
        found = False

        for col in genre_cols:
            value = row[col]

            if pd.notna(value):
                value_str = str(value).lower()
                if genre_name.lower() in value_str:
                    found = True

        matches.append(found)

    top_genre = data[matches].sort_values(by="artist_popularity", ascending=False).head(10)
    return top_genre[["name", "artist_popularity"]]


def genre_inspection(df):
    print("# Genre Inspection")
    print()

    genre_cols = ["genre_0", "genre_1", "genre_2", "genre_3", "genre_4", "genre_5", "genre_6"]

    print("Top 10 artists in Rock genre:")
    print(top_10_by_genre("Rock", df, genre_cols))
    print()

    df_genre = df.copy()

    # Count number of genres per artist
    df_genre["genre_count"] = df_genre[genre_cols].notna().sum(axis=1)

    # Distribution of number of genres per artist
    genre_freq = df_genre.groupby("genre_count").size()

    plt.figure()
    plt.bar(genre_freq.index, genre_freq.values, color="#E64A19")
    plt.title("Distribution of Number of Genres per Artist")
    plt.xlabel("Number of genres associated with artist")
    plt.ylabel("Number of artists")
    plt.tight_layout()
    plt.savefig("Distribution_genres_bar_chart.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Correlations
    correlation_genre_pop = df_genre["genre_count"].corr(df_genre["artist_popularity"])
    print("Correlation between genres per artist and artist popularity:", correlation_genre_pop)

    correlation_genre_followers = df_genre["genre_count"].corr(df_genre["followers"])
    print("Correlation between genres per artist and followers:", correlation_genre_followers)

    df_genre["followers_log"] = np.log(df_genre["followers"] + 1)
    correlation_genre_log_followers = df_genre["genre_count"].corr(df_genre["followers_log"])
    print("Correlation between genres per artist and log(followers):", correlation_genre_log_followers)
    print()

    # Boxplot: genres vs popularity
    plt.figure()
    df_genre.boxplot(column="artist_popularity", by="genre_count")
    plt.title("Artist Popularity vs Number of Genres Associated")
    plt.xlabel("Number of genres associated with artist")
    plt.ylabel("Artist popularity")
    plt.suptitle("")
    plt.grid(False)
    plt.tight_layout()
    plt.savefig("Genres_vs_Popularity_boxplot.png", dpi=300, bbox_inches="tight")
    plt.close()

    # Boxplot: genres vs followers
    plt.figure()
    df_genre.boxplot(column="followers_log", by="genre_count")
    plt.title("Number of Followers vs Number of Genres Associated")
    plt.xlabel("Number of genres associated with artist")
    plt.ylabel("Number of followers (log scale)")
    plt.suptitle("")
    plt.grid(False)
    plt.tight_layout()
    plt.savefig("Genres_vs_followers_boxplot.png", dpi=300, bbox_inches="tight")
    plt.close()


# Main program
def main():
    df = load_data()

    basic_data_inspection(df)
    popularity_vs_followers(df)
    genre_inspection(df)


if __name__ == "__main__":
    main()