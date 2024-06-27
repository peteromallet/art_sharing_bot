import sqlite3
con = sqlite3.connect("database.db")
cur = con.cursor()

query = "ALTER TABLE users ADD COLUMN tiktok VARCHAR DEFAULT NULL;"
res = cur.execute(query)

con.commit()
