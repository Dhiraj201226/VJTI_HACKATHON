import sqlite3

conn = sqlite3.connect('./data/gr_database.db')
c = conn.cursor()
c.execute('SELECT id, subject FROM generated_grs ORDER BY id DESC LIMIT 1')
row = c.fetchone()
print(f"ID: {row[0]}")
print(f"Subject bytes: {row[1].encode('utf-8')}")
