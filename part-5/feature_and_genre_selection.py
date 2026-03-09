import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os

# Add the directory to the search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))

# Import earlier functions
from part-1.Genres_inspection import atop_10_by_genre
from exercise3.feature_analysis import feature_distribution

# Setting dashboard layout
st.set_page_config(
    page_title="Feature & Genre analysis", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Select either genre or feature analysis
option_type = st.sidebar.selectbox(
    "Select type of analysis",
    ["Genre", "Feature"]
)

