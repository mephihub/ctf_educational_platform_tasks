# app.py
from flask import Flask, g, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
import os

APP_SECRET = os.environ.get("FLASK_SECRET", "dev-secret-change-me")
DB_PATH = os.environ.get("IDOR_DB", "idor_task.db")

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
    if db is not None:
        db.close()

# ---- Public ----
@app.route("/")
def index():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not username or not password:
        flash("Введите имя пользователя и пароль", "warning")
        return redirect(url_for("register"))
    db = get_db()
    try:
        cur = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?);",
            (username, generate_password_hash(password))
        )
        db.commit()
        user_id = cur.lastrowid  # id нового пользователя

        # --- ДОБАВЛЕНИЕ ТЕСТОВЫХ ДОКУМЕНТОВ ---
        test_docs = [
            (user_id, "Welcome Note", f"Привет! Это ваша первая заметка."),
            (user_id, "Todo List", "1. Учить SQL\n2. Найти флаг"),
            (user_id, "Random Note", "Эта заметка создана для тестирования.")
        ]
        db.executemany(
            "INSERT INTO documents (owner_id, title, body) VALUES (?, ?, ?);",
            test_docs
        )
        db.commit()

        flash("Регистрация успешна. Войдите.", "success")
        return redirect(url_for("login"))
    except Exception as e:
        flash("Ошибка: имя пользователя может быть занято", "danger")
        return redirect(url_for("register"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    if not username or not password:
        flash("Введите имя пользователя и пароль", "warning")
        return redirect(url_for("login"))
    db = get_db()
    cur = db.execute("SELECT id, username, password_hash FROM users WHERE username = ?;", (username,))
    row = cur.fetchone()
    if not row or not check_password_hash(row["password_hash"], password):
        flash("Неверные учётные данные", "danger")
        return redirect(url_for("login"))
    # login ok
    session["user"] = {"id": row["id"], "username": row["username"]}
    flash("Вход выполнен", "success")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Вы вышли", "info")
    return redirect(url_for("index"))

# ---- Dashboard (shows only own documents) ----
@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    db = get_db()
    cur = db.execute("SELECT id, title FROM documents WHERE owner_id = ? ORDER BY id DESC;", (user["id"],))
    docs = cur.fetchall()
    return render_template("dashboard.html", user=user, docs=docs)

# ---- Vulnerable endpoint: IDOR ----
# ВНИМАННО: уязвимая логика — сервер доверяет параметру owner_id из query вместо того, чтобы проверять session['user'].
# Пример эксплоита: любой залогиненный user может открыть /doc?id=XXX&owner_id=5 чтобы прочитать документ юзера с id=5 (в т.ч. флаг).
@app.route("/doc")
def view_doc():
    doc_id = request.args.get("id", type=int)
    owner_id = request.args.get("owner_id", type=int)  # <-- проблема: доверяем запросу
    if not doc_id or not owner_id:
        return "Missing parameters. Use ?id=<doc_id>&owner_id=<owner_id>", 400

    db = get_db()
    # intentionally uses owner_id from request, not session
    cur = db.execute("SELECT d.id,d.title,d.body,u.username AS owner FROM documents d JOIN users u ON d.owner_id=u.id WHERE d.id=? AND d.owner_id=?;",
                     (doc_id, owner_id))
    row = cur.fetchone()
    if not row:
        return render_template("doc.html", notfound=True, doc_id=doc_id, owner_id=owner_id)
    return render_template("doc.html", doc=row)

# ---- Simple helper: list all docs (for debugging) - not linked in UI ----
@app.route("/_all_docs")
def all_docs():
    db = get_db()
    cur = db.execute("SELECT d.id,d.title,d.owner_id,u.username FROM documents d JOIN users u ON d.owner_id=u.id ORDER BY d.id;")
    rows = cur.fetchall()
    out = "<h3>All documents</h3><ul>"
    for r in rows:
        out += f"<li>id={r['id']} owner_id={r['owner_id']} owner={r['username']} title={r['title']}</li>"
    out += "</ul>"
    return out

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

