import sqlite3
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt

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
    query_add = "ALTER TABLE albums_data ADD COLUMN era TEXT"
    cursor.execute(query_add)
    connection.commit()
    print("Added column: era")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column 'era' already exists")
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
    cursor.execute("UPDATE albums_data SET era = ? WHERE rowid = ?",row)
connection.commit()

# Checking the update worked by printing a sample of release_date and era
query = "SELECT release_date, era FROM albums_data LIMIT 10"
cursor.execute(query)
print("\nExample of era column next to release date:")
for row in cursor.fetchall():
    print(row)

# Checking how many albums were released in each era
print("\nNumber of albums released in each era:")
query = "SELECT era, COUNT(*) as number_albums FROM albums_data GROUP BY era ORDER BY era"
df_era_numbers = pd.read_sql(query, connection)
print(df_era_numbers)

# Checking the average popularity of albums released in each era
query = "SELECT era, AVG(album_popularity) AS avg_album_popularity FROM albums_data WHERE era != 'Unknown' GROUP BY era ORDER BY era"
df_pop_era = pd.read_sql(query, connection)
print(df_pop_era)

# Plotting 
plt.plot(df_pop_era["era"], df_pop_era["avg_album_popularity"])
plt.xticks(rotation=45)
plt.title("Average Album Popularity by Era")
plt.ylabel("Average Popularity")
plt.xlabel("Era")
plt.savefig("Era_vs_avgPop.png")
plt.close()

# Checking the average duration (converted minutes) of albums released per era 
query = "SELECT era, AVG(duration_ms) / 60000.0 AS avg_minutes FROM albums_data WHERE era != 'Unknown' GROUP BY era ORDER BY era "
df_duration_era = pd.read_sql(query, connection)
print(df_duration_era)

# Plotting
plt.plot(df_duration_era["era"], df_duration_era["avg_minutes"])
plt.xticks(rotation=45)
plt.title("Average Album Duration by Era")
plt.ylabel("Average Duration (minutes)")
plt.xlabel("Era")
plt.savefig("Era_vs_avgDuration.png")
plt.close()





