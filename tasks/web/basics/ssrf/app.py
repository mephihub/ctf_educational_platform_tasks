from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import requests
from pathlib import Path

BASE = Path(__file__).parent.resolve()
DB_PATH = BASE / "ssrf_demo.db"

app = Flask(__name__)
app.secret_key = "dev-secret-change-me"

# ---- DB helpers ----
def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    conn = get_db()
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
        ("bob", generate_password_hash("Bob123!"), "Bob B."),
        ("carol", generate_password_hash("Carol123!"), "Carol C."),
    ]
    cur.executemany("INSERT INTO users (username,password_hash,display_name) VALUES (?,?,?);", users)
    conn.commit()
    conn.close()

# ---- Auth helpers ----
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    db = get_db()
    user = db.execute("SELECT id, username, display_name FROM users WHERE id=?;", (uid,)).fetchone()
    db.close()
    return user

# ---- Routes ----
@app.route("/")
def index():
    user = current_user()
    return render_template("index.html", user=user)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="GET":
        return render_template("register.html")
    username = request.form.get("username","").strip()
    password = request.form.get("password","")
    display = request.form.get("display_name",username)
    if not username or not password:
        flash("Provide username and password","warning")
        return redirect(url_for("register"))
    db = get_db()
    try:
        db.execute("INSERT INTO users(username,password_hash,display_name) VALUES(?,?,?)",
                   (username,generate_password_hash(password),display))
        db.commit()
    except:
        flash("Username taken","danger")
        db.close()
        return redirect(url_for("register"))
    row = db.execute("SELECT id FROM users WHERE username=?",(username,)).fetchone()
    db.close()
    session["user_id"]=row["id"]
    flash("Registered and logged in","success")
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    username = request.form.get("username","").strip()
    password = request.form.get("password","")
    db = get_db()
    row = db.execute("SELECT id,password_hash FROM users WHERE username=?",(username,)).fetchone()
    db.close()
    if not row or not check_password_hash(row["password_hash"], password):
        flash("Invalid credentials","danger")
        return redirect(url_for("login"))
    session["user_id"]=row["id"]
    flash("Logged in","success")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("user_id",None)
    flash("Logged out","info")
    return redirect(url_for("index"))

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    fetched_content = None
    url_input = ""
    if request.method=="POST":
        url_input = request.form.get("url","")
        try:
            # ---- SSRF vulnerable request ----
            resp = requests.get(url_input, timeout=3)
            fetched_content = resp.text[:2000]  # limit to 2k chars
        except Exception as e:
            fetched_content = f"Error fetching URL: {e}"
    return render_template("dashboard.html", user=user, fetched_content=fetched_content, url_input=url_input)


@app.route("/internal/flag")
def internal_flag():
    if request.remote_addr != "127.0.0.1":
        return "Access denied", 403
    return "FLAG{ssrf_6ff78f39ca699311d0574ebb1af348bf}", 200
def internal_flag():
    return "FLAG{ssrf_11}", 200

# ---- Init DB if missing ----
if not DB_PATH.exists():
    init_db()
    print("Initialized SSRF demo DB.")

if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

