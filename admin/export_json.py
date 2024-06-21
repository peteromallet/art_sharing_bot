import sqlite3
import json


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


con = sqlite3.connect("database.db")

con.row_factory = dict_factory
cur = con.cursor()

query = "SELECT * FROM users;"
cur.execute(query)
users = cur.fetchall()

with open("data/users.json", "w") as f:
    json.dump(users, f)

query = "SELECT * FROM posts;"
cur.execute(query)
posts = cur.fetchall()


with open("data/posts.json", "w") as f:
    json.dump(posts, f)
