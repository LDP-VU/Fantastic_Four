import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os


# Adds the parent directory to the search path
db_path = os.path.join(os.path.dirname(__file__), "..", "spotify_database.db")


@st.cache_data
def get_all_artist(db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    query = f"SELECT * FROM artist_data WHERE followers >= 1000"
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows,
                      columns=[x[0] for x in cursor.description])
    connection.close()

    # puts all names in lowercase and removes unnecessary white spaces
    df['name_lower'] = df['name'].str.lower().str.strip()

    # sorts the df names alphabetically and followers from high to low
    df_sorted = df.sort_values(by=['name_lower', 'followers'], ascending=[True, False])

    # removes very similar names, like drake and Drakee or The Weeknd and The Weekendd
    unique_names = []
    name_mapping = []

    # drops duplicates names and keeps the most followed one
    df_cleaned = df_sorted.drop_duplicates(subset=['name_lower'], keep='first').copy()

    # reverts the names back to being capitalized
    df_cleaned['name'] = df_cleaned['name'].str.title()

    # drops the name_lower column
    df_cleaned = df_cleaned.drop(columns=['name_lower'])

    return df_cleaned


def get_top_tracks_for_artist(selected_artist_name, db_path):
    connection = sqlite3.connect(db_path)

    # 1. Fetch popularity data from tracks_data [cite: 51, 54]
    query_pop = "SELECT id, track_popularity FROM tracks_data"
    df_pop = pd.read_sql(query_pop, connection)

    # 2. Fetch track names and artist info from albums_data [cite: 50, 54]
    # We include artist_0 to match the main artist name
    query_albums = "SELECT track_id, track_name, artist_0 FROM albums_data"
    df_albums = pd.read_sql(query_albums, connection)

    connection.close()

    # 3. Merge dataframes on the track ID [cite: 56]
    # tracks_data uses 'id', albums_data uses 'track_id'
    df_merged = pd.merge(df_albums, df_pop, left_on='track_id', right_on='id', how='inner')

    # 4. Filter for the selected artist and sort
    # We strip and lowercase to ensure a match regardless of formatting
    df_merged['artist_0_clean'] = df_merged['artist_0'].str.lower().str.strip()
    target_name = selected_artist_name.lower().strip()

    artist_tracks = df_merged[df_merged['artist_0_clean'] == target_name].copy()

    # Sort by popularity and take the top 5 [cite: 12]
    top_5 = artist_tracks.sort_values(by='track_popularity', ascending=False).head(5)

    return top_5[['track_name', 'track_popularity']]




df_cleaned = get_all_artist(db_path)

st.sidebar.header("Artist search")
selected_artist = st.sidebar.selectbox(
    "Type to search for an artist:",
    options = df_cleaned['name'],
    index = None,
    placeholder = "Start typing an artist name"
)

if selected_artist:
    artist_info =df_cleaned[df_cleaned['name'] == selected_artist].iloc[0]

    st.title(f"{artist_info['name']}")


    col1, col2, col3 = st.columns(3)
    col1.metric("Popularity", f"{artist_info['artist_popularity']}")
    col2.metric("Followers",f"{artist_info['followers']}")

    genre_data = artist_info['artist_genres']
    if isinstance(genre_data,str):
        genre_list = eval(genre_data)
    else:
        genre_list=[]

    col3.metric("Number of Genres", len(genre_list))

    if genre_list:
        st.write(f"**Genres** {', '.join(genre_list)}")
    else:
        st.write("No genres were listed for this artist.")
    st.subheader(f"Top 5 Tracks by {selected_artist}")

    df_top_tracks = get_top_tracks_for_artist(selected_artist, db_path)

    if not df_top_tracks.empty:
        # Loop through the top 5 tracks to create the numbered list
        for i, (index, row) in enumerate(df_top_tracks.iterrows(), start=1):
            track_name = row['track_name']
            popularity = row['track_popularity']

            # Displaying in the format: 1. Song Name - Popularity: 85
            st.write(f"{i}. **{track_name}** — Popularity: `{popularity}`")
    else:
        st.write("No track data found for this artist.")



