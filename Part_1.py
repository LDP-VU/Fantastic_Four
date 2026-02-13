import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("artist_data.csv")

print("Columns:")
print(df.columns.tolist())
print()

print("Data types:")
print(df.dtypes)
print()

unique_artists = df["name"].nunique()
print("Number of unique artists:", unique_artists)
print()

top_popularity = df.sort_values("artist_popularity", ascending=False).head(10)

plt.figure()
plt.bar(top_popularity["name"], top_popularity["artist_popularity"])
plt.xticks(rotation=90)
plt.title("Top 10 Artists by Popularity")
plt.xlabel("Artist")
plt.ylabel("Popularity")
plt.tight_layout()
plt.show()

print("Top 10 by popularity:")
print(top_popularity[["name", "artist_popularity"]])
print()

top_followers = df.sort_values("followers", ascending=False).head(10)

plt.figure()
plt.bar(top_followers["name"], top_followers["followers"])
plt.xticks(rotation=90)
plt.title("Top 10 Artists by Followers")
plt.xlabel("Artist")
plt.ylabel("Followers")
plt.tight_layout()
plt.show()

print("Top 10 by followers:")
print(top_followers[["name", "followers"]])
