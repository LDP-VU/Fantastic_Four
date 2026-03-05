import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
import statsmodels.api as sm
import sys
import os

# Adds the parent directory to the search path
db_path = os.path.join(os.path.dirname(__file__), "..", "spotify_database.db")
con = sqlite3.connect(db_path)

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

# 2) Correlation

corr = df['album_popularity'].corr(df['artist_popularity'])
print("Correlation between album popularity and artist popularity:", round(corr, 3))


# 3) Linear regression

x = sm.add_constant(df['artist_popularity'])
y = df['album_popularity']

model = sm.OLS(y, x).fit()

print("\nRegression Parameters:")
print(model.params)
print()

# 4) SINGLE Plot (scatter + regression line)

plt.figure()
plt.scatter(df['artist_popularity'], df['album_popularity'], alpha=0.3)

x_values = np.linspace(df['artist_popularity'].min(), df['artist_popularity'].max(), 100)

y_values = model.params['const'] + model.params['artist_popularity'] * x_values

plt.plot(x_values, y_values, color="black", linewidth=2)

plt.title("Album Popularity vs Artist Popularity")
plt.xlabel("Artist Popularity")
plt.ylabel("Album Popularity")

plt.tight_layout()
plt.savefig("Album_vs_Artist_regression_plot.png", dpi=300)
plt.close()

print("Saved plot: Album_vs_Artist_regression_plot.png")
