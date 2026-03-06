import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os

# Add the directory to the search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))


# Setting dashboard layout
st.set_page_config(
    page_title="Feature & Genre analysis", 
    layout="wide",
    initial_sidebar_state="expanded"
)