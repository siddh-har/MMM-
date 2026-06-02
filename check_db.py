import sqlite3

conn = sqlite3.connect("instance/makemymoment.db")

cursor = conn.cursor()

# SHOW ALL TABLES
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

tables = cursor.fetchall()

print("Tables:")
print(tables)