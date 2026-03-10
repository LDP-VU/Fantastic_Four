import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sys
import os
import plotly.express as px

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
st.title("Spotify Data Analysis Dashboard")
st.write(""" 
         This dashboard explores a database released by Spotify (1900-2023) containing information on artists, albums, tracks and audio features.
         
         The goal is to investigate relationships between artist popularity, follower counts, genres and song features. Also, patterns about how these have evolved over time are explored.
         """)

# Basic cleaning
df = df.dropna(subset=["artist_popularity", "followers"])

# Sidebar (simple filter area)
st.sidebar.header("Filters")

# If you later have a year column, you can filter here.
# For now, we just show a placeholder filter message.
st.sidebar.write("No year filter available in artist_data.csv (yet).")

# Numerical summaries (KPI cards)
# Calculating important statistics to display
unique_artists = df["id"].nunique() if "id" in df.columns else len(df)
avg_popularity = df["artist_popularity"].mean()
median_popularity = df["artist_popularity"].median()
avg_followers = df["followers"].mean()
median_followeres= df["followers"].median()
all_genres = (df[["genre_1", "genre_2", "genre_3", "genre_4"]].stack().dropna().str.strip())
num_genres = all_genres.nunique()
avg_genres_per_artist = (df[["genre_1","genre_2","genre_3","genre_4"]].notna().sum(axis=1).mean())

# Row 1 display
col1, col2, col3, col4 = st.columns(4)
col1.metric("**Unique artists**", f"{unique_artists:,}")
col2.metric("**Avg popularity ( /100)**", f"{avg_popularity:.2f}")
col3.metric("**Avg followers**", f"{avg_followers:,.0f}")
col4.metric("**Avg genres per artist**", f"{avg_genres_per_artist:.2f}")

# Row 2 display
col5, col6, col7, col8 = st.columns(4)
col5.metric("**Number of genres**", f"{num_genres}")
col6.metric("**Median popularity ( /100)**", f"{median_popularity:.2f}")
col7.metric("**Median followers**", f"{median_followeres:,.0f}")
col8.metric("**Total rows**", f"{len(df):,}")

# Graphical summaries
st.subheader("Followers vs Artist Popularity")
left, right = st.columns(2)

# Plot 1: Histogram of popularity
with left:
    fig1, ax1 = plt.subplots(figsize=(6,5))

    ax1.hist(
        df["artist_popularity"],
        bins=20,
        color="#2E86C1",
        alpha=0.5,
        edgecolor="black")
    ax1.set_title("Distribution of Artist Popularity", fontweight="bold")
    ax1.set_xlabel("Artist popularity")
    ax1.set_ylabel("Count of artists")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    st.pyplot(fig1,use_container_width=True)

# Plot 2: Top 10 artists by followers
with right:
    top10 = df.sort_values(by="followers", ascending=False).head(10)
    fig2, ax2 = plt.subplots(figsize=(6, 5.7))
    ax2.barh(top10["name"], top10["followers"], color="#2E86C1")
    ax2.set_title("Top 10 Artists by Followers", fontweight="bold")
    ax2.set_xlabel("Followers", fontsize=12)
    ax2.set_ylabel("Artist", fontsize=12)
    ax2.invert_yaxis()
    ax2.grid(axis="x", linestyle="--", alpha=0.4)
    st.pyplot(fig2,use_container_width=True)

# Plot 3: Followers vs Popularity scatter plot
fig = px.scatter(
    df,
    x="followers",
    y="artist_popularity",
    hover_name="name",
    opacity=0.4,)
fig.update_xaxes(type="log")
fig.update_layout(
    title="Relationship: Followers vs Artist Popularity",
    xaxis_title="Followers (log scale)",
    yaxis_title="Artist Popularity",)
st.plotly_chart(fig)

# Descriptive summary table for popularity and followers
summary_df = pd.DataFrame({
    "Statistic": ["Mean", "Median", "Std", "Min", "Max"],
    "Popularity": [
        df["artist_popularity"].mean(),
        df["artist_popularity"].median(),
        df["artist_popularity"].std(),
        df["artist_popularity"].min(),
        df["artist_popularity"].max(),],
    "Followers": [
        df["followers"].mean(),
        df["followers"].median(),
        df["followers"].std(),
        df["followers"].min(),
        df["followers"].max(),],})
with st.expander("Descriptive Statistics for Popularity and Followers"):
    st.dataframe(summary_df.round(2), use_container_width=True)

# Plot 4: Top 10 genres
st.markdown("### Genres")
left, right = st.columns(2)
with left:     
    fig4, ax4 = plt.subplots(figsize=(6,5))
    top_genres=all_genres.value_counts().head(10)
    ax4.barh(top_genres.index, top_genres.values, color="#2E86C1")
    ax4.set_title("Top 10 Genres", fontweight="bold")
    ax4.set_xlabel("Number of Artists")
    ax4.invert_yaxis() 
    ax4.grid(axis="x", linestyle="--", alpha=0.4)
    fig4.tight_layout()
    st.pyplot(fig4, use_container_width=True)

# Plot 5: Artist popularity vs number of genres associated with artist    
with right: 
    df["genre_count"] = df[["genre_1", "genre_2", "genre_3", "genre_4"]].notna().sum(axis=1)
    fig5, ax5 = plt.subplots(figsize=(7,5.9))
    df.boxplot(column="artist_popularity", by="genre_count",ax=ax5,
        boxprops=dict(linewidth=2,color="#2E86C1"),
        whiskerprops=dict(linewidth=2,color="#2E86C1"),
        capprops=dict(linewidth=2,color="#2E86C1"),
        medianprops=dict(linewidth=2,color="#2E86C1"))
    ax5.set_title("Artist Popularity vs Number of Genres Associated",fontweight="bold", fontsize=14)
    ax5.set_xlabel("Number of Genres Associated with Artist", fontsize=12)
    ax5.set_ylabel("Artist Popularity", fontsize=12)
    ax5.grid(False)
    plt.suptitle("")
    fig5.tight_layout()
    st.pyplot(fig5, use_container_width=True)


