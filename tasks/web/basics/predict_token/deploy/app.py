# app.py
import os
import sqlite3
import base64
from flask import Flask, g, render_template, request, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.environ.get("SITE_DB", "site.db")
APP_SECRET = os.environ.get("FLASK_SECRET", "dev-secret-change-me")

app = Flask(__name__)
app.secret_key = APP_SECRET

def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = sqlite3.connect(DB_PATH)
        db.row_factory = sqlite3.Row
        g._db = db
    return db

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_db", None)
    if db:
        db.close()

# Utility: generate token (intentionally simple / predictable)
# Two supported formats:
#  - base64 of "username:userid"
#  - numeric: userid * 1000 (string)
def make_token(username: str, userid: int) -> str:
    raw = f"{username}:{userid}"
    b64 = base64.b64encode(raw.encode()).decode()
    return b64  # primary scheme issued

def make_numeric_token(userid: int) -> str:
    return str(userid * 1000)

def lookup_user_by_id(uid):
    db = get_db()
    cur = db.execute("SELECT id, username, display_name FROM users WHERE id = ?;", (uid,))
    return cur.fetchone()

def lookup_user_by_name_and_id(name, uid):
    db = get_db()
    cur = db.execute("SELECT id, username, display_name FROM users WHERE id = ? AND username = ?;", (uid, name))
    return cur.fetchone()

def get_secret(uid):
    db = get_db()
    cur = db.execute("SELECT secret FROM secrets WHERE user_id = ?;", (uid,))
    r = cur.fetchone()
    return r["secret"] if r else None

# --- Frontend pages ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    display = request.form.get("display_name", username)
    if not username or not password:
        return jsonify(success=False, error="username and password required"), 400
    db = get_db()
    try:
        cur = db.execute("INSERT INTO users (username, password_hash, display_name) VALUES (?, ?, ?);",
                         (username, generate_password_hash(password), display))
        db.commit()
        uid = cur.lastrowid
        token = make_token(username, uid)
        # Return token to client (auto-issue)
        return jsonify(success=True, token=token)
    except Exception as e:
        return jsonify(success=False, error="username taken or error"), 400

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not username or not password:
        return jsonify(success=False, error="username and password required"), 400
    db = get_db()
    cur = db.execute("SELECT id, username, password_hash FROM users WHERE username = ?;", (username,))
    row = cur.fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify(success=False, error="invalid credentials"), 401
    # Issue token on login
    token = make_token(row["username"], row["id"])
    return jsonify(success=True, token=token)

@app.route("/dashboard")
def dashboard():
    # Single page. Client obtains token from localStorage and calls /api/me to fill content.
    return render_template("dashboard.html")

# --- API endpoint (vulnerable) ---
@app.route("/api/me")
def api_me():
    # Accept Authorization: Bearer <token>
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "missing token"}), 401
    token = auth.split(" ", 1)[1].strip()

    user = None

    # Attempt scheme 1: base64(username:userid)
    try:
        decoded = base64.b64decode(token.encode(), validate=True).decode()
        if ":" in decoded:
            name, uid_s = decoded.split(":", 1)
            if uid_s.isdigit():
                uid = int(uid_s)
                user = lookup_user_by_name_and_id(name, uid)
    except Exception:
        # ignore base64 errors
        pass

    if user is None and token.isdigit():
        try:
            n = int(token)
            if n % 1000 == 0:
                uid = n // 1000
                user = lookup_user_by_id(uid)
        except Exception:
            pass

    if not user:
        return jsonify({"error": "invalid token"}), 401

    resp = {"id": user["id"], "username": user["username"], "display_name": user["display_name"]}

    # admin disclosure: includes secret if exists (intentionally)
    if user["username"] == "admin":
        secret = get_secret(user["id"])
        if secret:
            resp["secret"] = secret

    return jsonify(resp), 200

# Small helper to view users (for debugging, not linked in UI)
@app.route("/_users")
def _users():
    db = get_db()
    rows = db.execute("SELECT id, username, display_name FROM users ORDER BY id;").fetchall()
    out = "<h3>Users</h3><ul>"
    for r in rows:
        out += f"<li>{r['id']}: {r['username']} — {r['display_name']}</li>"
    out += "</ul>"
    return out

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("DB not found. Run init_db.py first.")
    app.run(debug=True, host="0.0.0.0", port=5000)

