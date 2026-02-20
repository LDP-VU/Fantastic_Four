import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import statsmodels.api as sm

# Connect to database
con = sqlite3.connect("spotify_database.db")

# Load track popularity and explicit flag
query = """
SELECT 
track_popularity,
explicit
FROM tracks_data
WHERE track_popularity IS NOT NULL
AND explicit IS NOT NULL
"""
df = pd.read_sql(query, con)
con.close()

# Convert explicit column to 0/1 safely
df["explicit"] = df["explicit"].astype(str).str.strip().str.lower()
df["explicit"] = df["explicit"].map({"true": 1, "false": 0})

# Drop any rows that didn't map properly (just in case)
df = df.dropna(subset=["explicit"])
df["explicit"] = df["explicit"].astype(int)

# Compare average popularity
explicit_mean = df[df["explicit"] == 1]["track_popularity"].mean()
non_explicit_mean = df[df["explicit"] == 0]["track_popularity"].mean()

print("Average popularity (Explicit tracks):", round(explicit_mean, 2))
print("Average popularity (Non-explicit tracks):", round(non_explicit_mean, 2))

# Correlation
corr = df["explicit"].corr(df["track_popularity"])
print("Correlation between explicit and popularity:", round(corr, 3))

# Linear regression
x = sm.add_constant(df["explicit"])
y = df["track_popularity"]

model = sm.OLS(y, x).fit()

print("\nRegression Parameters:")
print(model.params)

# Plot comparison and save
plt.figure()

means = [non_explicit_mean, explicit_mean]
labels = ["Non-explicit", "Explicit"]

colors = ["#4C72B0", "#E64A19"]  # Blue for non-explicit, orange-red for explicit

plt.bar(labels, means, color=colors)

plt.title("Average Popularity: Explicit vs Non-explicit Tracks")
plt.ylabel("Average Track Popularity")

plt.tight_layout()
plt.savefig("Explicit_vs_Popularity_barplot.png", dpi=300, bbox_inches="tight")
plt.close()

print("Saved plot: Explicit_vs_Popularity_barplot.png")

