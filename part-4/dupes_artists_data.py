import pandas as pd
import sqlite3
from pathlib import Path
import os

# Adds the parent directory to the search path
db_path = os.path.join(os.path.dirname(__file__), "..", "spotify_database.db")

# Connects to the database at that specific location
connection = sqlite3.connect(db_path)
cursor = connection.cursor()

query = f"SELECT * FROM artist_data"
cursor.execute(query)

#stores the query in a dataframe
rows = cursor.fetchall()
df = pd.DataFrame(rows,
                  columns = [x[0] for x in cursor.description])


# puts all names in lowercase and removes unnecessary white spaces
df['name_lower'] = df['name'].str.lower().str.strip()

# sorts the df names alphabetically and followers from high to low
df_sorted = df.sort_values(by=['name_lower','followers'], ascending = [True,False])

# drops duplicates names and keeps the most followed one
df_cleaned = df_sorted.drop_duplicates(subset = ['name_lower'], keep='first').copy()

#reverts the names back to being capitalized
df_cleaned['name'] = df_cleaned['name'].str.title()

#drops the name_lower column
df_cleaned = df_cleaned.drop(columns=['name_lower'])





