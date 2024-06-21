import sqlite3
con = sqlite3.connect("database.db")
cur = con.cursor()

query = "ALTER TABLE users ADD COLUMN dm_notifications INTEGER DEFAULT 1;"
res = cur.execute(query)

con.commit()
