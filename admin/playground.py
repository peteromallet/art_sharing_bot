import sqlite3
con = sqlite3.connect("database.db")
cur = con.cursor()

# query = "ALTER TABLE users ADD COLUMN tiktok VARCHAR DEFAULT NULL;"
query = "DELETE FROM users WHERE id = 688343645644259328;"
res = cur.execute(query)

con.commit()
