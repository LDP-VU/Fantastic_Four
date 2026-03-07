import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os

# Adds the parent directory to the search path
db_path = os.path.join(os.path.dirname(__file__), "..", "spotify_database.db")

# Setting dashboard layout
st.set_page_config(
    page_title="Trends Over Time", 
    layout="wide",
    initial_sidebar_state = "expanded"
    )

# Loading data using the format from "music_over_time.py"
@st.cache_data
def load_joined_data(db_path):
    connection = sqlite3.connect(db_path)
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
        WHERE albums_data.release_date IS NOT NULL """, connection )
    connection.close()

    # Getting dates
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df = df.dropna(subset=["release_date"]).copy()

    # Extracting year for slider 
    df["year"] = df["release_date"].dt.year.astype(int)

    return df

# Features to choose from on page
FEATURES = [
    "danceability",
    "energy",
    "valence",
    "acousticness",
    "tempo",
    "speechiness",
    "instrumentalness",
]

# Page output
st.title("Trends over time (Yearly averages)")

# Load data onto page
df = load_joined_data(db_path)

# Year range for slider based on data
min_year = int(df["year"].min())
max_year = int(df["year"].max())

# generating filter layout
st.subheader("Filters")
col1, col2 = st.columns([2, 1])
# slider
with col1:
    year_range = st.slider(
        "Select year range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
        step=1)
# feature drop down menu
with col2:
    feature = st.selectbox(
    "Feature",
    FEATURES,
    index=1,
    format_func=lambda x: x.capitalize())

# Filtering data by selected year range
start_year = year_range[0]
end_year = year_range[1]
df_time = df[df["year"].between(start_year, end_year)].copy()

# Calculating yearly means for selected year range
yearly_means = (df_time.groupby("year")[FEATURES].mean().reset_index().sort_values("year"))

# Output of selected filters
st.subheader(f"{feature.capitalize()} (Yearly Mean)")
st.info(
    "This chart shows the yearly average of the selected audio feature across all tracks in the Spotify dataset.\n"
    "Each point represents the mean value for that year.\n "
    "The lighter line shows a 10-year rolling average to highlight longer-term trends.\n"
    "Use the slider above to focus on a specific period, and the dropdown to select features."
)

# Plot
if yearly_means.empty or len(yearly_means) < 2:
    st.warning("Not enough data in the selected year range to display a trend.")
else:
    x = yearly_means["year"].to_numpy(dtype=float)
    y = yearly_means[feature].to_numpy(dtype=float)

    # Rolling smoothing over 10 years to show clearer trends over time 
    y_smooth = (pd.Series(y).rolling(window=10, center=True, min_periods=1).mean().to_numpy())

    fig = go.Figure()

    # adding trace lines
    fig.add_trace(go.Scatter(
        x=x,
        y=y,
        mode="lines+markers",
        name="Yearly mean",
    ))
    fig.add_trace(go.Scatter(
        x=x,
        y=y_smooth,
        mode="lines",
        name="Smoothed mean",
    ))

    # Adjusting x axis labels to make cleaner
    start_tick = int(np.ceil(x.min() / 10) * 10)
    end_tick = int(np.floor(x.max() / 10) * 10)
    ticks = np.arange(start_tick, end_tick + 1, 10)

    # overall figure layout
    fig.update_layout(
        title=f"Yearly average of {feature.capitalize()} over time",
        xaxis_title="Year",
        yaxis_title=f"Average {feature}",
        xaxis=dict(
            tickmode="array",
            tickvals=ticks,
            ticktext=[str(int(t)) for t in ticks]),
        hovermode="x unified",
        height=600)

    st.plotly_chart(fig, use_container_width=True)


# Table of actual yearly means for selected year range
with st.expander("Show yearly averages table"):
    st.dataframe(yearly_means, use_container_width=True)
st.caption(f"Years shown: {start_year}–{end_year}")
