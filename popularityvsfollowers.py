import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm

df = pd.read_csv("artist_data.csv")


# Looking at just correlation between followers and popularity
corr = df['followers'].corr(df['artist_popularity'])
print("Correlation between followers and popularity:", corr)

# Scatter plot to vizualize
plt.figure()
plt.scatter(df['followers'], df['artist_popularity'], alpha=0.5)
plt.title('Followers vs Popularity')
plt.xlabel('Followers')
plt.ylabel('Popularity')
plt.savefig("Followers_Popularity_scatter_plot.png")
plt.close()


#Linear regression model
df = df.dropna(subset=["followers", "artist_popularity"])
df['followers_log'] = np.log(df['followers'] + 1)
x = sm.add_constant(df['followers_log'])
y = df['artist_popularity']

model = sm.OLS(y, x).fit()
print("Parameters of the model: ")
print(model.params)
print()


# Plotting the regression line
plt.figure()
plt.scatter(df['followers_log'], df['artist_popularity'], alpha=0.5)
x_values = np.linspace(df['followers_log'].min(), df['followers_log'].max(), 100)
y_values = model.params['const'] + model.params['followers_log'] * x_values
plt.plot(x_values, y_values)
plt.title("Regression: Popularity vs log(Followers)")
plt.xlabel("log(Followers)")
plt.ylabel("Popularity")
plt.savefig("log(followers)_popularity_scatter_plot.png")
plt.close()

#Over performers and lgeacy artists
df['predicted_popularity'] = model.predict(x)
df['residual'] = df['artist_popularity'] - df['predicted_popularity']

overperformers = df.sort_values("residual", ascending=False).head(10)
legacy_artists = df.sort_values("residual").head(10)

print("Top 10 overperformers (high popularity, low followers):")
print(overperformers[["name", "followers", "artist_popularity", "residual"]])
print("\nTop 10 legacy artists (low popularity, high followers):")
print(legacy_artists[["name", "followers", "artist_popularity", "residual"]])
