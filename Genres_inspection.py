import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# loading dataset
df = pd.read_csv('artist_data.csv')
# Genre columns
genre_cols = ["genre_0", "genre_1", "genre_2", "genre_3", "genre_4", "genre_5", "genre_6"]


# Top 10 artists by genre
def top_10_by_genre(genre_name, data):
    
    # Function to check if any genre column contains the specified genre
    def row_contains_genre(row):
        row_as_str = row.astype(str)
        contains_genre = row_as_str.str.contains(genre_name, case=False)
        return contains_genre.any()
    
    # Applying row_contains_genre to each row
    matches_genre = data[genre_cols].apply(row_contains_genre, axis=1)
    
    # Sorting by popularity
    top_genre = data[matches_genre].sort_values(by='artist_popularity', ascending=False).head(10)

    return top_genre[["name", "artist_popularity"]]

# Example:
print("Top 10 artists in Rock genre: ")
print(top_10_by_genre('Rock', df))


# Number of genres an artist is associated with

# Adding a column in dataset to represent this
df["genre_count"] = df[genre_cols].notna().sum(axis=1)

# Barchart showing distribution of number of genres per artist
genre_freq = df.groupby("genre_count").size()
plt.figure()
plt.bar(genre_freq.index, genre_freq.values)
plt.title("Distribution of Number of Genres per Artist")
plt.xlabel("Number of genres associated with artist")
plt.ylabel("Number of artists")
plt.tight_layout()
plt.savefig("Distribution_genres_bar_chart.png")
plt.close()

# Calculating correlations between number of genres and popularity
correlation_genre_pop = df["genre_count"].corr(df["artist_popularity"])
print("Correlation between genres per artist and artist popularity: ", correlation_genre_pop)

# Calculating correlation between number of genres and number of followers
correlation_genre_followers = df["genre_count"].corr(df["followers"])
print("Correlation between genres per artist and followers: ", correlation_genre_followers)

# adding column for log of followers since number of followers can vary widely and has skewed distribution from extremely popular artists
    # Adding 1 to avoid log(0) (undefined) for artists with no followers
df["log_followers"] = np.log(df["followers"] + 1)

# Calculating correlation between number of genres and log of followers 
correlation_genre_log_followers = df["genre_count"].corr(df["log_followers"])
print("Correlation between genres per artist and log(followers):", correlation_genre_log_followers)

# Boxplot showing genres per artist vs popularity
plt.figure()
df.boxplot(column="artist_popularity", by="genre_count")
plt.title("Artist Popularity vs Number of Genres Associated")
plt.xlabel("Number of genres associated with artist")
plt.ylabel("Artist popularity")
plt.suptitle("") 
plt.grid(False)
plt.tight_layout()
plt.savefig("Genres_vs_Popularity_boxplot.png")
plt.close()

# Boxplot showing genres per artist vs number of followers
plt.figure()
df.boxplot(column="log_followers", by="genre_count")
plt.title("Number of followers vs Number of Genres Associated")
plt.xlabel("Number of genres associated with artist")
plt.ylabel("Number of followers (log scale)")
plt.suptitle("") 
plt.grid(False)
plt.tight_layout()
plt.savefig("Genres_vs_followers_boxplot.png")
plt.close()
