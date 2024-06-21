import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()

query = "SELECT * FROM users;"
res = cur.execute(query)

users = res.fetchall()

for user in users:
    print(user)
