import sqlite3

conn = sqlite3.connect("my_files.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    data BLOB
)
""")

conn.commit()
conn.close()