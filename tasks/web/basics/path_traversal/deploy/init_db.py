# init_data.py
import os
import sqlite3
from werkzeug.security import generate_password_hash

BASE = os.path.dirname(__file__)
DB = os.path.join(BASE, "fileshare.db")
UPLOADS = os.path.join(BASE, "uploads")

def ensure_dirs():
    os.makedirs(UPLOADS, exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.executescript("""
    DROP TABLE IF EXISTS users;
    CREATE TABLE users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      display_name TEXT
    );
    """)
    users = [
        ("alice", generate_password_hash("Alice123!"), "Alice A."),
        ("bob", generate_password_hash("Bob123!"), "Robert B."),
        ("carol", generate_password_hash("Carol123!"), "Carol C."),
    ]
    cur.executemany("INSERT INTO users (username, password_hash, display_name) VALUES (?, ?, ?);", users)
    conn.commit()
    conn.close()

def seed_files():
    # create per-user upload folders and files
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, username FROM users;")
    rows = cur.fetchall()
    for uid, username in rows:
        userdir = os.path.join(UPLOADS, username)
        os.makedirs(userdir, exist_ok=True)
        # create 3 files per user
        for i in range(1,4):
            fname = f"note{i}.txt"
            path = os.path.join(userdir, fname)
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"Hello {username}!\nThis is your file {fname}.\nOwner: {username}\nUserID: {uid}\n")
    conn.close()

def write_flag():
    FLAG = "FLAG{path_traversal_5d6198f04b150a812762f3c47b513ce3}"
    with open("/flag.txt", "w+") as f:
        f.write(FLAG + "\n")

def main():
    ensure_dirs()
    init_db()
    seed_files()
    write_flag()
    print("Initialized DB, uploads and secret. DB:", DB)
    print("Uploads dir:", UPLOADS)

if __name__ == "__main__":
    main()

