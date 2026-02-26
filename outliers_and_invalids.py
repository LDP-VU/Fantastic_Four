import pandas as pd
import numpy as np
import sqlite3

conn = sqlite3.connect("spotify_database.db")

# Start with detecting outliers in different features with IQR method
feature = "danceability"

Q1 = df[feature].quantile(0.25)
Q3 = df[feature].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
outliers = df[(df[feature] < lower) | (df[feature] > upper)]
print(outliers.head())

# Then outliers in popularity with IQR method
pop_Q1 = df["popularity"].quantile(0.25)
pop_Q3 = df["popularity"].quantile(0.75)
pop_IQR = pop_Q3 - pop_Q1

pop_lower = pop_Q1 - 1.5 * pop_IQR
pop_upper = pop_Q3 + 1.5 * pop_IQR
pop_outliers = df[(df["popularity"] < pop_lower) | (df["popularity"] > pop_upper)]
print(pop_outliers.head())

