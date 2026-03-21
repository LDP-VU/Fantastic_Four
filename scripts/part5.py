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
    /* --- MAIN APP BACKGROUND --- */
    .stApp {
        background-color: #121212;
        color: #FFFFFF;
    }

    /* --- REMOVE WHITE TOP BAR --- */
    header {
        background-color: #121212 !important;
    }

    /* --- MAIN CONTENT AREA --- */
    .main {
        background-color: #121212;
    }

    /* --- MAIN CONTAINER --- */
    .block-container {
        background-color: #121212;
        padding: 2rem;
    }

    /* --- SIDEBAR --- */
    section[data-testid="stSidebar"] {
        background-color: #0e0e0e;
        border-right: 2px solid #1DB954;
    }

    /* --- REMOVE ANY REMAINING WHITE --- */
    div[data-testid="stAppViewContainer"] {
        background-color: #121212;
    }

    /* --- TEXT --- */
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF;
    }

    p, span, div {
        color: #FFFFFF;
    }

    /* --- BUTTON STYLE --- */
div.stButton > button {
    background-color: #FFFFFF;
    color: #000000 !important;   
    border-radius: 10px;
    border: none;
    padding: 0.6em 1em;
    transition: all 0.2s ease-in-out;
}

/* --- BUTTON TEXT (fix inner span) --- */
div.stButton > button * {
    color: #000000 !important;   
}

/* --- BUTTON HOVER --- */
div.stButton > button:hover {
    background-color: #1DB954;
    color: #000000 !important;
}

/* --- BUTTON HOVER TEXT --- */
div.stButton > button:hover * {
    color: #FFFFFF !important;
}

/* --- BUTTON CLICK --- */
div.stButton > button:active {
    transform: scale(0.98);
}
    </style>
    """,
    unsafe_allow_html=True
)
# artist search black text

st.markdown(
    """
    <style>
    /* Selected text / typed text inside the selectbox */
    div[data-baseweb="select"] input {
        color: black !important;
        -webkit-text-fill-color: black !important;
    }

    /* Placeholder text */
    div[data-baseweb="select"] input::placeholder {
        color: #666666 !important;
        -webkit-text-fill-color: #666666 !important;
        opacity: 1 !important;
    }

    /* The visible selected value in the box */
    div[data-baseweb="select"] span {
        color: black !important;
        -webkit-text-fill-color: black !important;
    }

    /* The selectbox background itself */
    div[data-baseweb="select"] > div {
        background-color: #f2f2f2 !important;
        color: black !important;
        border-radius: 12px !important;
    }

    /* Dropdown popup container */
    div[data-baseweb="popover"] {
        background-color: white !important;
    }

    /* Dropdown list */
    ul[role="listbox"] {
        background-color: white !important;
    }

    /* Each dropdown option */
    li[role="option"] {
        background-color: white !important;
        color: black !important;
    }

    /* Text inside each option */
    li[role="option"] * {
        color: black !important;
        -webkit-text-fill-color: black !important;
    }

    /* Hovered option */
    li[role="option"]:hover {
        background-color: #eaeaea !important;
        color: black !important;
    }

    li[role="option"]:hover * {
        color: black !important;
        -webkit-text-fill-color: black !important;

    }
     div[data-baseweb="select"] div {
        color: black !important;
        -webkit-text-fill-color: black !important;
    }

    div[data-baseweb="select"] [class*="singleValue"] {
        color: black !important;
        -webkit-text-fill-color: black !important;
    }

    div[data-baseweb="select"] * {
        color: black !important;
        -webkit-text-fill-color: black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
# tool tip ?
st.markdown("""
    <style>
    /* 1. Change the Question Mark (SVG) to White */
    /* This targets the help icon inside the metric */
    [data-testid="stMetric"] svg {
        fill: white !important;
        color: white !important;
        opacity: 1 !important;
    }

    /* 2. Change the Tooltip Box background to White and Text to Black */
    /* Note: Streamlit uses a portal for tooltips, so we target the tooltip content */
    div[data-active-tab="true"] + div .stTooltipHoverTarget, 
    .stTooltipContent {
        background-color: white !important;
        color: black !important;
        border: 1px solid #ccc;
    }
    
    /* This specifically targets the text inside the pop-up */
    .stTooltipContent div {
        color: black !important;
    }
    </style>
    """, unsafe_allow_html=True)


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

    # Spotify logo (top of sidebar)
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 10px;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/8/84/Spotify_icon.svg" width="50">
        </div>
        """,
        unsafe_allow_html=True
    )

    # Navigation title
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

@st.cache_data
def load_explicit_data(db_path):
    connection = sqlite3.connect(db_path)
    df = pd.read_sql("""
        SELECT track_popularity, explicit
        FROM tracks_data
        WHERE track_popularity IS NOT NULL
        AND explicit IS NOT NULL
    """, connection)
    connection.close()

    df["explicit_num"] = df["explicit"].astype(str).str.lower().map({"true": 1, "false": 0})
    df = df.dropna(subset=["explicit_num"])

    return df

@st.cache_data
def load_genre_feature_data(db_path, feature):
    connection = sqlite3.connect(db_path)

    df = pd.read_sql(f"""
        SELECT 
            features_data.{feature} AS feature_value,
            artist_data.genre_1,
            artist_data.genre_2,
            artist_data.genre_3,
            artist_data.genre_4
        FROM features_data
        JOIN albums_data ON features_data.id = albums_data.track_id
        JOIN artist_data ON albums_data.artist_id = artist_data.id
        WHERE features_data.{feature} IS NOT NULL
    """, connection)

    connection.close()
    return df


@st.cache_data
def get_artist_explicit_data(artist_name, db_path):
    connection = sqlite3.connect(db_path)
    # Using SQL JOIN is much faster than loading full tables into memory
    query = """
        SELECT t.explicit
        FROM tracks_data t
        JOIN albums_data a ON t.id = a.track_id
        WHERE LOWER(TRIM(a.artist_0)) = ?
    """
    df_artist = pd.read_sql(query, connection, params=(artist_name.lower().strip(),))
    connection.close()

    if df_artist.empty:
        return None

    # Convert to numeric (handling 'true'/'false' strings or booleans)
    df_artist["is_explicit"] = df_artist["explicit"].astype(str).str.lower().map({"true": 1, "false": 0})

    explicit_count = int(df_artist["is_explicit"].sum())
    total_count = len(df_artist)
    clean_count = total_count - explicit_count
    ratio = explicit_count / total_count if total_count > 0 else 0

    return {
        "explicit_count": explicit_count,
        "clean_count": clean_count,
        "total": total_count,
        "ratio": ratio
    }


def get_top_tracks_for_artist(selected_artist_name, db_path):
    connection = sqlite3.connect(db_path)

    # 1. Fetch popularity data
    query_pop = "SELECT id, track_popularity, explicit FROM tracks_data"
    df_pop = pd.read_sql(query_pop, connection)

    # 2. Fetch track info and audio features from albums_data & features_data
    # We add duration and features to perform the "Outlier/Invalid" check
    query_details = """
        SELECT 
            albums_data.track_id, 
            albums_data.track_name, 
            albums_data.artist_0, 
            albums_data.duration_ms,
            features_data.danceability,
            features_data.energy,
            features_data.valence
        FROM albums_data
        JOIN features_data ON albums_data.track_id = features_data.id
    """
    df_details = pd.read_sql(query_details, connection)
    connection.close()

    # 3. Merge dataframes
    df_merged = pd.merge(df_details, df_pop, left_on='track_id', right_on='id', how='inner')

    # --- WRANGLING STEP: Outliers and Invalid Records ---

    # Remove missing IDs and non-positive durations
    df_merged = df_merged.dropna(subset=["track_id"])
    df_merged = df_merged[df_merged["duration_ms"] > 0]

    df_merged = df_merged.sort_values(by='track_popularity', ascending=False)
    df_merged = df_merged.drop_duplicates(subset=["track_name"], keep='first')

    # Ensure audio features are in the valid range [0, 1]
    features = ["danceability", "energy", "valence"]
    for col in features:
        df_merged = df_merged[(df_merged[col] >= 0) & (df_merged[col] <= 1)]

    # Remove duplicate tracks to ensure the Top 5 are unique
    df_merged = df_merged.drop_duplicates(subset=["track_id"])

    # --- FILTERING FOR ARTIST ---

    df_merged['artist_0_clean'] = df_merged['artist_0'].str.lower().str.strip()
    target_name = selected_artist_name.lower().strip()
    artist_tracks = df_merged[df_merged['artist_0_clean'] == target_name].copy()

    return artist_tracks.sort_values(by='track_popularity', ascending=False)[['track_name', 'track_popularity', 'explicit']]

def load_collaboration_data(db_path):
    connection = sqlite3.connect(db_path)

    df_tracks = pd.read_sql("""
        SELECT id, track_popularity
        FROM tracks_data
        WHERE track_popularity IS NOT NULL
    """, connection)

    df_collab = pd.read_sql("""
        SELECT track_id, artist_0, artist_1
        FROM albums_data
    """, connection)

    connection.close()

    df = pd.merge(df_collab, df_tracks, left_on="track_id", right_on="id", how="inner")

    # collaboration logic (reuse your own function)
    def is_collaboration(row):
        return str(row["artist_1"]).strip().lower() not in ["", "none"]

    df["is_collab"] = df.apply(is_collaboration, axis=1)

    return df



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


    #Pots 6&7: Explicit and Collaborations
    st.markdown("---")
    st.subheader("Explicitness and Collaborations")

    col1, col2 = st.columns(2)

    #Explicit content analysis
    with col1:
        df_explicit = load_explicit_data(db_path)

        if not df_explicit.empty:
            explicit_mean = df_explicit[df_explicit["explicit_num"] == 1]["track_popularity"].mean()
            non_explicit_mean = df_explicit[df_explicit["explicit_num"] == 0]["track_popularity"].mean()

            m1, m2 = st.columns(2)
            with m1:
                st.metric("Explicit Avg", f"{explicit_mean:.2f}")
            with m2:
                st.metric("Non-Explicit Avg", f"{non_explicit_mean:.2f}")

            fig_explicit = go.Figure()
            fig_explicit.add_trace(go.Bar(
                x=["Non-Explicit", "Explicit"],
                y=[non_explicit_mean, explicit_mean],
                marker_color=["#4C72B0", "#E64A19"]
            ))

            fig_explicit.update_layout(
                title="Explicit vs Popularity",
                yaxis_title="Popularity"
            )

            st.plotly_chart(fig_explicit, use_container_width=True)

    #Collaboration analysis
    with col2:
        df_collab = load_collaboration_data(db_path)

        if not df_collab.empty:
            mean_values = df_collab.groupby("is_collab")["track_popularity"].mean()

            solo = mean_values.get(False, 0)
            collab = mean_values.get(True, 0)

            m1, m2 = st.columns(2)
            with m1:
                st.metric("Solo Avg", f"{solo:.2f}")
            with m2:
                st.metric("Collab Avg", f"{collab:.2f}")

            fig_collab = go.Figure()
            fig_collab.add_trace(go.Bar(
                x=["Solo", "Collaboration"],
                y=[solo, collab],
                marker_color=["#4C72B0", "#E64A19"]
            ))

            fig_collab.update_layout(
                title="Collaboration vs Popularity",
                yaxis_title="Popularity"
            )

            st.plotly_chart(fig_collab, use_container_width=True)

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
        result = result.sort_values(by="artist_popularity", ascending=True)
        
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
            expanded = expanded.dropna(subset=["artist"])
            expanded = expanded[expanded["artist"].str.strip() != ""]
            expanded = expanded[expanded["artist"].str.lower() != "nan"]
            artist_counts = expanded.groupby("artist").size().sort_values(ascending=False)
            
            # Display metrics
            #Define units for the features
            units = {
                "tempo": "BPM",
                "loudness": "dB",
                "danceability": "score",
                "energy": "score",
                "valence": "score",
                "acousticness": "score",
                "speechiness": "score",
                "instrumentalness": "score"
            }

            # Get the unit for  current selection
            unit = units.get(selected_feature, "")

            # 2. Updated Metrics with Units and Tooltips
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total tracks", f"{len(df_features):,}")
            with col2:
                st.metric(f"Top {selected_percent}% tracks", len(top_tracks))
            with col3:
                # We add the unit to the value and a descriptive tooltip
                st.metric(
                    label="Threshold",
                    value=f"{threshold:.2f} {unit}",
                    help=f"To be in the top {selected_percent}% for {selected_feature}, "
                         f"a track must have a value of at least {threshold:.2f} {unit}."
                )
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

            #Genres hig hand low on specific feature
            st.markdown("---")
            st.subheader(f"Genres low and high in {selected_feature}")

            df_genre_feat = load_genre_feature_data(db_path, selected_feature)
            if not df_genre_feat.empty:
                df_genre_feat = df_genre_feat.dropna(subset=["feature_value"])

                # Create quantiles
                labels_full = ["very low", "low", "medium", "high", "very high"]
                df_genre_feat["level"] = pd.cut(
                    df_genre_feat["feature_value"],
                    bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                    labels=labels_full,
                    include_lowest=True
                )
                n_bins = df_genre_feat["level"].nunique()
                df_genre_feat["level"] = pd.cut(
                    df_genre_feat["feature_value"],
                    bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
                    labels=labels_full,
                    include_lowest=True
                )

                def count_genres(df_subset):
                    genres = []
                    for col in ["genre_1", "genre_2", "genre_3", "genre_4"]:
                        cleaned = (
                            df_subset[col]
                            .dropna()
                            .astype(str)
                            .str.strip()
                        )
                        # REMOVE bad values
                        cleaned = cleaned[
                            (cleaned != "") &
                            (cleaned.str.lower() != "nan") &
                            (cleaned.str.lower() != "none")
                        ]
                        genres.extend(cleaned)
                    return pd.Series(genres).value_counts().head(10)

                low_counts = count_genres(df_genre_feat[df_genre_feat["level"] == "very low"])
                high_counts = count_genres(df_genre_feat[df_genre_feat["level"] == "very high"])
                col1, col2 = st.columns(2)
                with col1:
                    fig_low = px.bar(
                        x=low_counts.values,
                        y=low_counts.index,
                        orientation='h',
                        title=f"Very low {selected_feature}"
                    )
                    fig_low.update_layout(
                        yaxis=dict(categoryorder='total ascending'),
                        showlegend=False,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    st.plotly_chart(fig_low, use_container_width=True)
                with col2:
                    fig_high = px.bar(
                        x=high_counts.values,
                        y=high_counts.index,
                        orientation='h',
                        title=f"Very high {selected_feature}"
                    )
                    fig_high.update_layout(
                        yaxis=dict(categoryorder='total ascending'),
                        showlegend=False,
                        margin=dict(l=0, r=0, t=40, b=0)
                    )
                    st.plotly_chart(fig_high, use_container_width=True)
            else:
                st.warning(f"No data found for feature: {selected_feature}")


def artist_search_page():
    """Artist Search page content"""
    df_cleaned = get_all_artist(db_path)

    st.header("Artist Search")
    selected_artist = st.selectbox(
        "Type to search for an artist:",
        options=df_cleaned['name'],
        index=None,
        placeholder="Start typing an artist name"
    )

    if selected_artist:
        artist_info = df_cleaned[df_cleaned['name'] == selected_artist].iloc[0]
        st.title(f"{artist_info['name']}")

        # 1. Get the CLEANED tracks first (this uses all your filters: duration, features, etc.)
        # Note: We need to make sure this function also returns the 'explicit' column now!
        df_top_tracks = get_top_tracks_for_artist(selected_artist, db_path)

        # 2. Calculate explicit stats ONLY from these cleaned tracks
        if not df_top_tracks.empty:
            # Ensure 'explicit' column exists in your merged dataframe
            # (You may need to add 't.explicit' to the SQL query in get_top_tracks_for_artist)
            df_top_tracks["is_explicit"] = df_top_tracks["explicit"].astype(str).str.lower().map(
                {"true": 1, "false": 0})

            explicit_count = int(df_top_tracks["is_explicit"].sum())
            total_count = len(df_top_tracks)
            clean_count = total_count - explicit_count

        # --- Metrics Row ---
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Popularity", f"{artist_info['artist_popularity']}")
        col2.metric("Followers", f"{int(artist_info['followers']):,}")

        # --- Genre Display Logic ---
        genre_data = artist_info['artist_genres']

        # Robust parsing of the genre string
        if isinstance(genre_data, str) and genre_data.strip() and genre_data != "[]":
            try:
                genre_list = ast.literal_eval(genre_data)
            except:
                genre_list = [g.strip() for g in genre_data.split(',')]
        else:
            genre_list = []

        # Update the Metric
        col3.metric("Genres", len(genre_list))

        # The "Missing Genre" Message
        if genre_list:
            # Capitalize each genre for a cleaner look
            formatted_genres = ", ".join([g.capitalize() for g in genre_list])
            st.write(f"**Genres:** {formatted_genres}")
        else:
            # This is the message you were looking for
            st.info("No genres were listed for this artist in the database.")


        st.markdown("---")

        # --- Display List and Chart side-by-side ---
        track_col, chart_col = st.columns([1, 1])

        with track_col:
            st.subheader("Top 5 Tracks")  # Kept the title the same
            if not df_top_tracks.empty:
                # Use .head(5) here instead of in the function
                for i, (index, row) in enumerate(df_top_tracks.head(5).iterrows(), start=1):
                    st.write(f"{i}. **{row['track_name']}** (Pop: `{row['track_popularity']}`)")
            else:
                st.write("No valid tracks found.")

        with chart_col:
            if not df_top_tracks.empty:
                st.subheader("Explicit Proportion")
                fig = go.Figure(data=[go.Pie(
                    labels=['Explicit', 'Clean'],
                    values=[explicit_count, clean_count],
                    hole=0,
                    marker_colors=['#E74C3C', '#2ECC71'],
                    textinfo='value+percent',
                    insidetextfont=dict(size=20, color="white")
                )])

                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    height=450,
                    margin=dict(t=0, b=0, l=0, r=0),
                    legend=dict(font=dict(color="white"), orientation="h", y=-0.1, x=0.5, xanchor="center")
                )
                st.plotly_chart(fig, use_container_width=True)

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