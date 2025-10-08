# app.py
import os
import sqlite3
from flask import Flask, g, render_template, request, redirect, url_for, session, flash, send_file, abort, Response
from werkzeug.security import generate_password_hash, check_password_hash
from pathlib import Path

BASE = Path(__file__).parent.resolve()
DB_PATH = BASE / "fileshare.db"
UPLOADS = BASE / "uploads"   # directory with per-user folders
SECRET = BASE / "secret"     # directory outside uploads (contains flag)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-change-me")

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

# ---- helpers ----
def current_user():
    uid = session.get("user_id")
    if not uid:
        return None
    db = get_db()
    r = db.execute("SELECT id, username, display_name FROM users WHERE id = ?;", (uid,)).fetchone()
    return r

# ---- routes ----
@app.route("/")
def index():
    user = current_user()
    return render_template("index.html", user=user)

@app.route("/upload", methods=["GET","POST"])
def upload():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part", "warning")
            return redirect(request.url)
        f = request.files["file"]
        if f.filename == "":
            flash("No selected file", "warning")
            return redirect(request.url)
        # сохраняем в директорию пользователя
        user_dir = UPLOADS / user["username"]
        user_dir.mkdir(exist_ok=True)
        safe_name = secure_filename(f.filename)
        f.save(user_dir / safe_name)
        flash(f"File '{safe_name}' uploaded!", "success")
        return redirect(url_for("dashboard"))
    
    return render_template("upload.html", user=user)

# download: отдаёт файл пользователю
@app.route("/download")
def download():
    file_param = request.args.get("file", "")
    if not file_param:
        return "Missing 'file' parameter", 400
    target = UPLOADS / file_param  # уязвимый путь
    if not target.exists() or not target.is_file():
        return "File not found", 404
    return send_file(str(target), as_attachment=True)


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    display = request.form.get("display_name", username)
    if not username or not password:
        flash("Please provide username and password", "warning")
        return redirect(url_for("register"))
    db = get_db()
    try:
        db.execute("INSERT INTO users (username, password_hash, display_name) VALUES (?, ?, ?);",
                   (username, generate_password_hash(password), display))
        db.commit()
    except Exception as e:
        flash("Username already taken", "danger")
        return redirect(url_for("register"))
    # auto-login
    row = db.execute("SELECT id FROM users WHERE username = ?;", (username,)).fetchone()
    session["user_id"] = row["id"]
    flash("Registered and logged in", "success")
    return redirect(url_for("dashboard"))

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    db = get_db()
    row = db.execute("SELECT id, username, password_hash FROM users WHERE username = ?;", (username,)).fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        flash("Invalid credentials", "danger")
        return redirect(url_for("login"))
    session["user_id"] = row["id"]
    flash("Logged in", "success")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    user = current_user()
    if not user:
        return redirect(url_for("login"))
    # list user's files from uploads/<username> directory
    user_dir = UPLOADS / user["username"]
    files = []
    if user_dir.exists():
        for p in sorted(user_dir.iterdir()):
            if p.is_file():
                files.append(p.name)
    return render_template("dashboard.html", user=user, files=files)


@app.route("/view")
def view():
    file_param = request.args.get("file", "")
    if not file_param:
        return "Missing 'file' parameter", 400
    target = UPLOADS / file_param
    if not target.exists() or not target.is_file():
        return "File not found", 404
    # Return text/plain
    try:
        with open(target, "rb") as f:
            data = f.read()
        return Response(data, mimetype="text/plain")
    except Exception as e:
        return f"Error reading file: {e}", 500

# small admin/debug route to list uploads (not linked in UI)
@app.route("/_ls")
def _ls():
    out = "<h3>Uploads tree</h3><ul>"
    for root, dirs, files in os.walk(UPLOADS):
        rel = os.path.relpath(root, UPLOADS)
        out += f"<li><strong>{rel}</strong><ul>"
        for fn in files:
            out += f"<li>{fn}</li>"
        out += "</ul></li>"
    out += "</ul>"
    return out

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

