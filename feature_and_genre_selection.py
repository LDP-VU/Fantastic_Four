import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import os
import sys

# Add path to import from part-1 and part-3
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'part-1')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'part-3')))

# Import modules
import Genres_inspection
import album_features

# Database path
db_path = os.path.join(os.path.dirname(__file__), "..", "spotify_database.db")

# Setting dashboard layout
st.set_page_config(
    page_title="Feature & Genre Analysis", 
    layout="wide",
    initial_sidebar_state="expanded"
)

#DATA LOADING FUNCTIONS
@st.cache_data
def load_artist_data():
    """Load artist data for genre analysis"""
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), '..', 'artist_data.csv'))
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

#BUILDING THE DASHBOARD
st.title("Feature & Genre Analysis")
st.markdown("---")

# Sidebar for selection
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

# DISPLAYING RESULTS
if analysis_type == "Genre Analysis":
    st.header(f"Genre Analysis: {selected_genre.capitalize()}")
    
    # Load artist data
    df_artists = load_artist_data()
    
    # Get top artists for selected genre using the function from Genres_inspection
    result = Genres_inspection.top_10_by_genre(selected_genre, df_artists)
    
    if not result.empty:
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            # Count artists in this genre
            mask = df_artists[Genres_inspection.genre_cols].apply(
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
            st.metric(f"Threshold", f"{threshold:.3f}")
        
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

# Footer
st.markdown("---")
st.caption("Data source: Spotify Dataset 2023")