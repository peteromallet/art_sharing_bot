import json
import sqlite3

# IMPORTANT: create database by sqlalchemy by running main.py first
# Edit: no need to do this manual migration, use ALTER TABLE command

con = sqlite3.connect("database.db")
cursor = con.cursor()

with open("data/users.json", "r") as f:
    users = json.load(f)
    # columns = ', '.join(f'{k} {type(v).__name__}' for k, v in users[0].items())
    # cursor.execute(f"CREATE TABLE IF NOT EXISTS users ({columns});")

    for user in users:
        placeholders = ', '.join('?' for _ in user.values())
        cursor.execute(
            f"INSERT INTO users VALUES ({placeholders})", tuple(user.values()))

with open("data/posts.json", "r") as f:
    posts = json.load(f)
    # columns = ', '.join(f'{k} {type(v).__name__}' for k, v in posts[0].items())
    # cursor.execute(f"CREATE TABLE IF NOT EXISTS posts ({columns});")

    for post in posts:
        placeholders = ', '.join('?' for _ in post.values())
        cursor.execute(
            f"INSERT INTO posts VALUES ({placeholders})", tuple(post.values()))

con.commit()
