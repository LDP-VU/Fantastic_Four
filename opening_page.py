import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

# Adds the parent directory to the search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

# Page setup
st.set_page_config(page_title="Spotify Dashboard", layout="wide")

# Load data (cached so it doesn't reload every time)
@st.cache_data
def load_artist_data():
    df = pd.read_csv("artist_data.csv")
    return df

df = load_artist_data()

# Title + short intro
st.title("Spotify Data Dashboard")
st.write("Opening page: general statistics + quick overview plots.")

# Basic cleaning
df = df.dropna(subset=["artist_popularity", "followers"])

# Sidebar (simple filter area)
st.sidebar.header("Filters")

# If you later have a year column, you can filter here.
# For now, we just show a placeholder filter message.
st.sidebar.write("No year filter available in artist_data.csv (yet).")

# Numerical summaries (KPIs)
unique_artists = df["id"].nunique() if "id" in df.columns else len(df)
avg_popularity = df["artist_popularity"].mean()
median_popularity = df["artist_popularity"].median()
avg_followers = df["followers"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Unique artists", f"{unique_artists:,}")
col2.metric("Avg popularity", f"{avg_popularity:.2f}")
col3.metric("Median popularity", f"{median_popularity:.2f}")
col4.metric("Avg followers", f"{avg_followers:,.0f}")

# Numerical summary table
st.subheader("Numerical summary")

summary_df = pd.DataFrame(
    {
        "Statistic": [
            "Mean popularity",
            "Median popularity",
            "Std popularity",
            "Mean followers",
            "Median followers",
        ],
        "Value": [
            df["artist_popularity"].mean(),
            df["artist_popularity"].median(),
            df["artist_popularity"].std(),
            df["followers"].mean(),
            df["followers"].median(),
        ],
    }
)

st.table(summary_df.round(2))

# Graphical summaries
st.subheader("Graphical summaries")

left, right = st.columns(2)

# Plot 1: Histogram of popularity
with left:
    fig1, ax1 = plt.subplots()
    ax1.hist(df["artist_popularity"], bins=20, color="#1DB954")
    ax1.set_title("Distribution of Artist Popularity")
    ax1.set_xlabel("Artist popularity")
    ax1.set_ylabel("Count of artists")
    st.pyplot(fig1)

# Plot 2: Top 10 artists by followers
with right:
    top10 = df.sort_values(by="followers", ascending=False).head(10)

    fig2, ax2 = plt.subplots()
    ax2.barh(top10["name"], top10["followers"], color="#2E86C1")
    ax2.set_title("Top 10 Artists by Followers")
    ax2.set_xlabel("Followers")
    ax2.set_ylabel("Artist")
    ax2.invert_yaxis()
    st.pyplot(fig2)

# Plot 3: Followers vs Popularity (professional insight)
st.subheader("Relationship: Followers vs Popularity")

fig3, ax3 = plt.subplots()
ax3.scatter(df["followers"], df["artist_popularity"], alpha=0.3, color="#E64A19")
ax3.set_title("Followers vs Artist Popularity")
ax3.set_xlabel("Followers")
ax3.set_ylabel("Artist popularity")
st.pyplot(fig3)

# Optional: show columns and types (useful for debugging, not required)
with st.expander("Show column names and data types"):
    info_df = pd.DataFrame(
        {"Column": df.columns, "Dtype": [str(t) for t in df.dtypes]}
    )
    st.dataframe(info_df)