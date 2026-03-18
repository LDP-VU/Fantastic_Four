import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt
import os
import sys
import ast

db_path = os.path.join(os.path.dirname(__file__), '..', 'spotify_database.db')


# Database path
df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'artist_data.csv'))

# Setting dashboard layout
st.set_page_config(
    page_title="Spotify Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for page navigation if not exists
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Sidebar navigation
with st.sidebar:
    st.markdown("## Navigation")
    
    if st.button("Home", use_container_width=True):
        st.session_state.page = "Home"
    
    if st.button("Feature & Genre Analysis", use_container_width=True):
        st.session_state.page = "Feature & Genre Analysis"
    
    if st.button("Artist Search", use_container_width=True):
        st.session_state.page = "Artist Search"
    
    if st.button("Trends Over Time", use_container_width=True):
        st.session_state.page = "Trends Over Time"
    
    st.markdown("---")
    

# ============================================================================
# DATA LOADING FUNCTIONS (Shared across pages)
# ============================================================================

@st.cache_data
def load_artist_data():
    """Load artist data for genre analysis"""
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'artist_data.csv'))
    return df

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
    # drops duplicates names and keeps the most followed one
    df_cleaned = df_sorted.drop_duplicates(subset=['name_lower'], keep='first').copy()

    # reverts the names back to being capitalized
    df_cleaned['name'] = df_cleaned['name'].str.title()

    # drops the name_lower column
    df_cleaned = df_cleaned.drop(columns=['name_lower'])

    return df_cleaned

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

@st.cache_data
def load_feature_data(db_path, feature):
    """Load feature data from database"""
    connection = sqlite3.connect(db_path)
    df = pd.read_sql(f"""
        SELECT 
            albums_data.track_name,
            albums_data.artist_0,
            albums_data.artist_1,
            albums_data.artist_2,
            features_data.{feature}
        FROM albums_data
        JOIN features_data ON albums_data.track_id = features_data.id
        WHERE features_data.{feature} IS NOT NULL
    """, connection)
    connection.close()
    return df

def get_top_tracks_for_artist(selected_artist_name, db_path):
    connection = sqlite3.connect(db_path)

    # 1. Fetch popularity data from tracks_data
    query_pop = "SELECT id, track_popularity FROM tracks_data"
    df_pop = pd.read_sql(query_pop, connection)

    # 2. Fetch track names and artist info from albums_data
    # We include artist_0 to match the main artist name
    query_albums = "SELECT track_id, track_name, artist_0 FROM albums_data"
    df_albums = pd.read_sql(query_albums, connection)

    connection.close()

    # 3. Merge dataframes on the track ID
    # tracks_data uses 'id', albums_data uses 'track_id'
    df_merged = pd.merge(df_albums, df_pop, left_on='track_id', right_on='id', how='inner')

    # 4. Filter for the selected artist and sort
    # We strip and lowercase to ensure a match regardless of formatting
    df_merged['artist_0_clean'] = df_merged['artist_0'].str.lower().str.strip()
    target_name = selected_artist_name.lower().strip()

    artist_tracks = df_merged[df_merged['artist_0_clean'] == target_name].copy()

    # Sort by popularity and take the top 5
    top_5 = artist_tracks.sort_values(by='track_popularity', ascending=False).head(5)

    return top_5[['track_name', 'track_popularity']]

# ============================================================================
# PAGE FUNCTIONS
# ============================================================================

def home_page():
    """Home page / Opening page content"""
    # Load data
    df = load_artist_data()

    st.title("Spotify Data Analysis Dashboard")
    st.write(""" 
             This dashboard explores a database released by Spotify (1900-2023) containing information on artists, albums, tracks and audio features.
             
             The goal is to investigate relationships between artist popularity, follower counts, genres and song features. Also, patterns about how these have evolved over time are explored.
             """)

    # Basic cleaning
    df = df.dropna(subset=["artist_popularity", "followers"])

    # Numerical summaries (KPI cards)
    # Calculating important statistics to display
    unique_artists = df["id"].nunique() if "id" in df.columns else len(df)
    avg_popularity = df["artist_popularity"].mean()
    median_popularity = df["artist_popularity"].median()
    avg_followers = df["followers"].mean()
    median_followers = df["followers"].median()
    all_genres = (df[["genre_1", "genre_2", "genre_3", "genre_4"]].stack().dropna().str.strip())
    num_genres = all_genres.nunique()
    avg_genres_per_artist = (df[["genre_1","genre_2","genre_3","genre_4"]].notna().sum(axis=1).mean())

    # Row 1 display
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Unique artists", f"{unique_artists:,}")
    col2.metric("Avg popularity ( /100)", f"{avg_popularity:.2f}")
    col3.metric("Avg followers", f"{avg_followers:,.0f}")
    col4.metric("Avg genres per artist", f"{avg_genres_per_artist:.2f}")

    # Row 2 display
    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Number of genres", f"{num_genres}")
    col6.metric("Median popularity ( /100)", f"{median_popularity:.2f}")
    col7.metric("Median followers", f"{median_followers:,.0f}")
    col8.metric("Total rows", f"{len(df):,}")

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
        st.pyplot(fig1, use_container_width=True)

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
        st.pyplot(fig2, use_container_width=True)

    # Plot 3: Followers vs Popularity scatter plot
    fig = px.scatter(
        df,
        x="followers",
        y="artist_popularity",
        hover_name="name",
        opacity=0.4)
    fig.update_xaxes(type="log")
    fig.update_layout(
        title="Relationship: Followers vs Artist Popularity",
        xaxis_title="Followers (log scale)",
        yaxis_title="Artist Popularity")
    st.plotly_chart(fig, use_container_width=True)

    # Descriptive summary table for popularity and followers
    summary_df = pd.DataFrame({
        "Statistic": ["Mean", "Median", "Std", "Min", "Max"],
        "Popularity": [
            df["artist_popularity"].mean(),
            df["artist_popularity"].median(),
            df["artist_popularity"].std(),
            df["artist_popularity"].min(),
            df["artist_popularity"].max()],
        "Followers": [
            df["followers"].mean(),
            df["followers"].median(),
            df["followers"].std(),
            df["followers"].min(),
            df["followers"].max()]})
    with st.expander("Descriptive Statistics for Popularity and Followers"):
        st.dataframe(summary_df.round(2), use_container_width=True)

    # Plot 4: Top 10 genres
    st.markdown("### Genres")
    left, right = st.columns(2)
    with left:     
        fig4, ax4 = plt.subplots(figsize=(6,5))
        top_genres = all_genres.value_counts().head(10)
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
        df.boxplot(column="artist_popularity", by="genre_count", ax=ax5,
            boxprops=dict(linewidth=2, color="#2E86C1"),
            whiskerprops=dict(linewidth=2, color="#2E86C1"),
            capprops=dict(linewidth=2, color="#2E86C1"),
            medianprops=dict(linewidth=2, color="#2E86C1"))
        ax5.set_title("Artist Popularity vs Number of Genres Associated", fontweight="bold", fontsize=14)
        ax5.set_xlabel("Number of Genres Associated with Artist", fontsize=12)
        ax5.set_ylabel("Artist Popularity", fontsize=12)
        ax5.grid(False)
        plt.suptitle("")
        fig5.tight_layout()
        st.pyplot(fig5, use_container_width=True)

def feature_genre_analysis_page():
    """Feature & Genre Analysis page content"""
    st.title("Feature & Genre Analysis")
    st.markdown("---")

    # Sidebar for selection (within page content)
    with st.sidebar:
        st.header("Analysis Options")
        
        # Main selection
        analysis_type = st.radio(
            "Select analysis type:",
            ["Genre Analysis", "Feature Analysis"]
        )
        
        st.markdown("---")
        
        if analysis_type == "Genre Analysis":
            st.subheader("Genre Selection")
            selected_genre = st.selectbox(
                "Choose a genre:",
                ["pop", "rock", "hip hop", "jazz", "electronic", "r&b", "country", "classical"]
            )
            
        else:  # Feature Analysis
            st.subheader("Feature Selection")
            selected_feature = st.selectbox(
                "Choose a feature:",
                ["danceability", "energy", "valence", "acousticness", "speechiness", "instrumentalness", "tempo", "loudness"]
            )
            
            selected_percent = st.slider(
                "Top percentage of tracks:",
                min_value=5, max_value=50, value=10, step=5
            )

    # Define genre columns
    genre_cols = ['genre_1', 'genre_2', 'genre_3', 'genre_4']
    
    # Function to get top artists by genre
    def top_10_by_genre(genre, df):
        """Get top 10 artists for a specific genre"""
        # Filter artists that have the genre in any genre column
        mask = df[genre_cols].apply(
            lambda row: row.astype(str).str.contains(genre, case=False).any(), 
            axis=1
        )
        genre_artists = df[mask].copy()
        
        # Sort by popularity and get top 10
        top_10 = genre_artists.nlargest(10, 'artist_popularity')[['name', 'artist_popularity']]
        
        return top_10

    # DISPLAYING RESULTS
    if analysis_type == "Genre Analysis":
        st.header(f"Genre Analysis: {selected_genre.capitalize()}")
        
        # Load artist data
        df_artists = load_artist_data()
        
        # Get top artists for selected genre
        result = top_10_by_genre(selected_genre, df_artists)
        
        if not result.empty:
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                # Count artists in this genre
                mask = df_artists[genre_cols].apply(
                    lambda row: row.astype(str).str.contains(selected_genre, case=False).any(), 
                    axis=1
                )
                st.metric("Total artists in genre", mask.sum())
            with col2:
                st.metric("Avg popularity", round(result['artist_popularity'].mean(), 1))
            with col3:
                st.metric("Top artist", result.iloc[0]['name'])
            
            st.markdown("---")
            
            # Display top artists
            st.subheader(f"Top 10 Artists in {selected_genre.capitalize()}")
            
            # Create a bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=result['artist_popularity'],
                y=result['name'],
                orientation='h',
                marker=dict(color='lightcoral')
            ))
            
            fig.update_layout(
                title=f"Top 10 {selected_genre.capitalize()} Artists by Popularity",
                xaxis_title="Popularity",
                yaxis_title="Artist",
                height=400 + (10 * 20),
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show table
            with st.expander("View as table"):
                st.dataframe(result.head(10), use_container_width=True)
        else:
            st.warning(f"No artists found for genre: {selected_genre}")

    else:  # Feature Analysis
        st.header(f"Feature Analysis: {selected_feature.capitalize()}")
        
        # Load feature data
        df_features = load_feature_data(db_path, selected_feature)
        
        if not df_features.empty:
            # Calculate threshold for top percentage
            threshold = df_features[selected_feature].quantile(1 - selected_percent/100)
            top_tracks = df_features[df_features[selected_feature] >= threshold].copy()
            
            # Process collaborations
            artists_df = top_tracks[["artist_0", "artist_1", "artist_2"]]
            artists_no_nan = artists_df.apply(lambda row: row.dropna(), axis=1)
            artists_joined = artists_no_nan.apply(lambda row: ", ".join(row), axis=1)
            
            top_tracks["artists"] = artists_joined
            expanded = top_tracks.assign(
                artist=top_tracks["artists"].str.split(", ")
            ).explode("artist")
            
            # Get artist counts
            artist_counts = expanded.groupby("artist").size().sort_values(ascending=False)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total tracks", len(df_features))
            with col2:
                st.metric(f"Top {selected_percent}% tracks", len(top_tracks))
            with col3:
                st.metric("Threshold", f"{threshold:.3f}")
            
            st.markdown("---")
            
            # Two columns for display
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.subheader(f"Top Tracks by {selected_feature.capitalize()}")
                
                # Display top tracks
                display_tracks = top_tracks[["track_name", "artist_0", selected_feature]]\
                    .sort_values(by=selected_feature, ascending=False)\
                    .head(10)
                
                fig_tracks = go.Figure(data=[go.Table(
                    header=dict(values=["Track", "Artist", selected_feature.capitalize()],
                               fill_color='lightgray',
                               align='left'),
                    cells=dict(values=[display_tracks['track_name'], 
                                      display_tracks['artist_0'],
                                      display_tracks[selected_feature].round(3)],
                              fill_color='white',
                              align='left')
                )])
                
                fig_tracks.update_layout(height=400)
                st.plotly_chart(fig_tracks, use_container_width=True)
            
            with col_right:
                st.subheader("Top Artists by Track Count")
                
                if not artist_counts.empty:
                    # Show top 10 artists
                    top_artists = artist_counts.head(10)
                    
                    fig_artists = go.Figure()
                    fig_artists.add_trace(go.Bar(
                        x=list(top_artists.values),
                        y=list(top_artists.index),
                        orientation='h',
                        marker=dict(color='lightblue')
                    ))
                    
                    fig_artists.update_layout(
                        title=f"Artists with most tracks in top {selected_percent}%",
                        xaxis_title="Number of tracks",
                        yaxis_title="Artist",
                        height=400,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    
                    st.plotly_chart(fig_artists, use_container_width=True)
            
            # Show full statistics in expander
            with st.expander("View detailed statistics"):
                # Artist statistics
                st.subheader("Artist Statistics")
                artist_stats = expanded.groupby("artist").agg(
                    avg_feature=(selected_feature, "mean"),
                    num_tracks=(selected_feature, "count")
                ).sort_values(by="num_tracks", ascending=False)
                
                st.dataframe(artist_stats.head(20), use_container_width=True)
                
                # Feature distribution
                st.subheader("Feature Distribution")
                fig_dist = go.Figure()
                fig_dist.add_trace(go.Histogram(
                    x=df_features[selected_feature],
                    nbinsx=50,
                    name="All tracks"
                ))
                fig_dist.add_trace(go.Histogram(
                    x=top_tracks[selected_feature],
                    nbinsx=30,
                    name=f"Top {selected_percent}%"
                ))
                fig_dist.update_layout(
                    title=f"Distribution of {selected_feature.capitalize()}",
                    xaxis_title=selected_feature.capitalize(),
                    yaxis_title="Count",
                    barmode='overlay'
                )
                st.plotly_chart(fig_dist, use_container_width=True)
        else:
            st.warning(f"No data found for feature: {selected_feature}")

def artist_search_page():
    """Artist Search page content"""
    df_cleaned = get_all_artist(db_path)

    st.header("Artist search")
    selected_artist = st.selectbox(
        "Type to search for an artist:",
        options = df_cleaned['name'],
        index = None,
        placeholder = "Start typing an artist name"
    )

    if selected_artist:
        artist_info = df_cleaned[df_cleaned['name'] == selected_artist].iloc[0]

        st.title(f"{artist_info['name']}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Popularity", f"{artist_info['artist_popularity']}")
        col2.metric("Followers", f"{artist_info['followers']}")

        genre_data = artist_info['artist_genres']
        if isinstance(genre_data, str):
            genre_list = ast.literal_eval(genre_data)
        else:
            genre_list = []

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

def trends_over_time_page():
    """Trends Over Time page content"""
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

# ============================================================================
# SPOTIFY THEME STYLING
# ============================================================================

SPOTIFY_GREEN = "#1DB954"
DARK_BG = "#000000"
CARD_BG = "#121212"
TEXT_COLOR = "#FFFFFF"

# Set full app background to black
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
        color: white;
    }

    /* Optional: nicer container look */
    .block-container {
        background-color: #121212;
        padding: 2rem;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ============================================================================
# MAIN APP - Page routing
# ============================================================================

# Display the selected page
if st.session_state.page == "Home":
    home_page()
elif st.session_state.page == "Feature & Genre Analysis":
    feature_genre_analysis_page()
elif st.session_state.page == "Artist Search":
    artist_search_page()
elif st.session_state.page == "Trends Over Time":
    trends_over_time_page()

# Footer
st.markdown("---")
st.caption("Data source: Spotify Dataset 2023")