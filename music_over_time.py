import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

connection = sqlite3.connect("spotify_database.db")

# Features to analyse over time
features = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "tempo",
    "speechiness",
    "instrumentalness"]

# Joining albums_data and features_data 
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
""", connection)

connection.close()

# Converting release_date to datetime to handle different input formats
df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
df = df.dropna(subset=["release_date"])

# Daily average for selected features
daily_means = (df.groupby(df["release_date"].dt.date)[features].mean().reset_index().sort_values("release_date"))
print("Daily averages example (first rows):")
print(daily_means.head())

#Plotting a daily average example to demonstrate how noisy it is to analyse by day
plt.figure()
plt.plot(daily_means["release_date"],daily_means["energy"], linewidth=0.5)
plt.title(f"Example feature (Energy) over time (Daily Average)")
plt.xlabel("Release Date")
plt.ylabel(f"Average Energy")
plt.tight_layout()
plt.savefig(f"Example_daily_noise.png")
plt.close()

# Yearly average for selected features
yearly_means = (df.groupby(df["release_date"].dt.year)[features].mean().reset_index().sort_values("release_date"))
# Plotting yearly averages for each feature
for feature in features:
    plt.figure()
    plt.plot(yearly_means["release_date"], yearly_means[feature])
    plt.title(f"{feature.capitalize()} over time (Yearly Average)")
    plt.xlabel("Year")
    plt.ylabel(f"Average {feature}")
    plt.tight_layout()
    plt.savefig(f"{feature}_over_time.png")
    plt.close()

# Era averages for selected features 
era_means = (df.groupby("era")[features].mean().sort_index())
print("\nAverage feature values by era:")
print(era_means)
# Plotting
for feature in features:
    plt.bar(era_means.index, era_means[feature])
    plt.title(f"Average {feature} by Era")
    plt.xlabel("Era")
    plt.ylabel(f"Average {feature}")
    plt.tight_layout()
    plt.savefig(f"Era_{feature}.png")
    plt.close()