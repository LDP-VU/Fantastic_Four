import sqlite3
from datetime import datetime
import pandas as pd

connection = sqlite3.connect("spotify_database.db")
cursor = connection.cursor()

# Checking the structure of the albums_data table by printing column names and a sample row
query = "SELECT * FROM albums_data LIMIT 1"
cursor.execute(query)
columns = [c[0] for c in cursor.description]
row = cursor.fetchone()
row_dict = dict(zip(columns, row))
print("List of column names and a corresponding sample row: ")
for col, value in row_dict.items():
    print(f"{col}: {value}")
print()

print("Empty columns:")
# Checking which artist columns have no entries at all in any rows
for i in range(12):
    col_name = f'artist_{i}'
    query = f"""
    SELECT COUNT(*) AS non_missing
    FROM albums_data
    WHERE {col_name} IS NOT NULL AND TRIM({col_name}) != '' AND LOWER(TRIM({col_name})) != 'none';
    """
    result = pd.read_sql(query, connection)
    if result['non_missing'][0] == 0:
        print(f"{col_name} is completely empty")

print()

# Rebuilding table with only the relevant artist columns
cols_to_drop = ["artist_7", "artist_8", "artist_9", "artist_10", "artist_11"]
cols_keep = [c for c in columns if c not in cols_to_drop]
cols_keep_sql = ", ".join(cols_keep)
query_clean = f"SELECT {cols_keep_sql} FROM albums_data;"

# Checking the rebuild worked
cursor.execute(query_clean)
new_columns = [col[0] for col in cursor.description]
print("Columns after exclusion:")
for col in new_columns:
    print(col)


# Adding new column "decade" to the albums_data table (if not already existing)
try:
    query_add = "ALTER TABLE albums_data ADD COLUMN decade TEXT"
    cursor.execute(query_add)
    connection.commit()
    print("Added column: decade")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column 'decade' already exists")
    else:
        raise

# Fetching all rows to calculate the decade for each album
cursor.execute("SELECT rowid, release_date FROM albums_data")
rows = cursor.fetchall()

def to_decade(release_date):
    try:
        dt = datetime.strptime(str(release_date)[:10], "%Y-%m-%d")  
        decade = (dt.year // 10) * 10
        return f"{decade}s" 
    except:
        return "Unknown"

# Update table
decades = [(to_decade(release_date), rowid) for (rowid, release_date) in rows]
for row in decades:
    cursor.execute(
        "UPDATE albums_data SET decade = ? WHERE rowid = ?",
        row
    )
connection.commit()

# Checking the update worked by printing a sample of release_date and decade
query = "SELECT release_date, decade FROM albums_data LIMIT 10"
cursor.execute(query)
print("Example of decade column next to release date:")
for row in cursor.fetchall():
    print(row)



