# init_db.py
import sqlite3
from werkzeug.security import generate_password_hash

DB = "site.db"

def init():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.executescript("""
    DROP TABLE IF EXISTS users;
    DROP TABLE IF EXISTS secrets;

    CREATE TABLE users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      display_name TEXT DEFAULT ''
    );

    CREATE TABLE secrets (
      user_id INTEGER PRIMARY KEY,
      secret TEXT,
      FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """)

    # create some users (admin is first)
    users = [
        ("admin", generate_password_hash("AdminPass!"), "Site Administrator"),
        ("alice", generate_password_hash("Alice123!"), "Alice"),
        ("bob", generate_password_hash("Bob123!"), "Bob"),
        ("carol", generate_password_hash("Carol123!"), "Carol")
    ]
    cur.executemany("INSERT INTO users (username, password_hash, display_name) VALUES (?, ?, ?);", users)

    # admin secret/flag
    FLAG = "FLAG{predictable_token_bypass_2025_4f86e2e696f71cc4e1a8966a32c2812e}"
    cur.execute("INSERT INTO secrets (user_id, secret) VALUES (?, ?);", (1, FLAG))

    conn.commit()
    conn.close()
    print("Initialized DB:", DB)

if __name__ == "__main__":
    init()

