import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()

query = "SELECT * FROM posts;"
res = cur.execute(query)

posts = res.fetchall()

for post in posts:
    print(post)
