# init_db.py
import sqlite3
from werkzeug.security import generate_password_hash

DB = "idor_task.db"

def init():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS documents;

    CREATE TABLE users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL
    );

    CREATE TABLE documents (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      owner_id INTEGER NOT NULL,
      title TEXT NOT NULL,
      body TEXT NOT NULL,
      FOREIGN KEY (owner_id) REFERENCES users(id)
    );
    """)

    # Create ~10 users
    users = []
    for i in range(1,11):
        uname = f"user{i}"
        pwd_hash = generate_password_hash(f"Pass{i}!")  # simple passwords for tests
        users.append((uname, pwd_hash))
    cur.executemany("INSERT INTO users (username, password_hash) VALUES (?, ?);", users)

    # Create documents: each user 2-3 docs. Put a special flag in user id 5 doc.
    docs = []
    for uid in range(1,11):
        docs.append((uid, f"{uid} — public note", f"This is public note for user{uid}"))
        docs.append((uid, f"{uid} — private note", f"This is private note for user{uid}"))
        if uid % 3 == 0:
            docs.append((uid, f"{uid} — extra", f"Extra doc for user{uid}"))
    # Insert docs
    cur.executemany("INSERT INTO documents (owner_id, title, body) VALUES (?, ?, ?);", docs)

    # Insert flag into user with id=5 as a private document
    FLAG = "FLAG{idor_simple_2025_d99dbdd7f9837d8d254385694f1c136c}"
    cur.execute("INSERT INTO documents (owner_id, title, body) VALUES (?, ?, ?);", (5, "secret_flag", FLAG))
    conn.commit()
    conn.close()
    print("DB initialized:", DB)

if __name__ == "__main__":
    init()

