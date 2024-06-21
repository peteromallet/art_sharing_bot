import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()

query = "SELECT u.name, COUNT(*) FROM users u JOIN posts p ON u.id = p.user_id GROUP BY u.id ORDER BY COUNT(*) DESC;"
res = cur.execute(query)

data = res.fetchall()

for d in data:
    print(d)
