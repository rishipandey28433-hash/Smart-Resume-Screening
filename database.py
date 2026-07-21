import sqlite3

conn = sqlite3.connect("resume.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS resumes(

id INTEGER PRIMARY KEY AUTOINCREMENT,

filename TEXT,

score REAL,

recommendation TEXT

)
""")

conn.commit()

conn.close()

print("Database Created Successfully")