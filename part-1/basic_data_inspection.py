import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

df = pd.read_csv("artist_data.csv")

# Columns in the dataset
print("Columns:")
print(df.columns)
print()

# Type of data in each column
print("Data types:")
print(df.dtypes)
print()

# Number of unique artists
unique_artists = df["name"].nunique()
print("Number of unique artists:", unique_artists)
print()

# Top 10 artists by popularity
top_popularity = df.sort_values("artist_popularity", ascending=False).head(10)

plt.figure()
plt.bar(top_popularity["name"], top_popularity["artist_popularity"])
plt.xticks(rotation=90)
plt.title("Top 10 Artists by Popularity")
plt.xlabel("Artist")
plt.ylabel("Popularity")
plt.tight_layout()
plt.savefig("Top_Popularity_bar_chart.png")
plt.close()

print("Top 10 artists by popularity:")
print(top_popularity[["name", "artist_popularity"]])
print()

# Top 10 artists by followers
top_followers = df.sort_values("followers", ascending=False).head(10)

plt.figure()
plt.bar(top_followers["name"], top_followers["followers"])
plt.xticks(rotation=90)
plt.title("Top 10 Artists by Followers")
plt.xlabel("Artist")
plt.ylabel("Followers")
plt.tight_layout()
plt.savefig("Top_Followers_bar_chart.png")
plt.close()

print("Top 10 by followers:")
print(top_followers[["name", "followers"]])
