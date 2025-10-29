# app.py
from flask import Flask, request, render_template, redirect, url_for, session, jsonify
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-change-me")

DB_CFG = dict(host="db", port=3306, user="root", password="root", db="sqli_accounts", charset="utf8mb4", cursorclass=pymysql.cursors.Cursor, autocommit=True)

def get_conn():
    return pymysql.connect(**DB_CFG)

# ---- Routes ----

@app.route("/")
def index():
    if session.get("user"):
        return redirect(url_for("dashboard"))
    return render_template("index.html")

# Registration — НАМЕРЕННО УЯЗВИМЫЙ (string interpolation) для error-based SQLi.
# В случае успеха возвращает JSON {"success": true}
# В случае ошибки возвращает JSON {"success": false, "error": "<sql error text>"}
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return jsonify(success=False, error="Username and password required"), 400

    # Хешируем пароль (даже если SQL инъекцию мы допускаем — пароль хранится как hash)
    password_hash = generate_password_hash(password)

    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        # ВНИМАННО: уязвимый код — прямая строковая подстановка.
        # Кто-то может вставить payload, который вызовет ошибку и в тексте ошибки будет например значение из таблицы secrets.
        sql = f"INSERT INTO users (username, password_hash) VALUES ('{username}', '{password_hash}');"
        cur.execute(sql)
        # Если дошли сюда — запрос выполнен успешно
        return jsonify(success=True)
    except Exception as e:
        # Возвращаем текст SQL-ошибки — для учебной error-based инъекции это критично
        # Необходимо аккуратно формировать JSON ответ
        return jsonify(success=False, error=str(e)), 400
    finally:
        if conn:
            conn.close()

# Login — безопасно: параметризованный запрос + проверка хеша
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        return render_template("login.html", error="Введите логин и пароль")

    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        if not row:
            return render_template("login.html", error="Неверные учётные данные")
        user_id, user_name, pwd_hash = row
        if not check_password_hash(pwd_hash, password):
            return render_template("login.html", error="Неверные учётные данные")
        # Успешный вход
        session["user"] = {"id": user_id, "username": user_name}
        return redirect(url_for("dashboard"))
    except Exception as e:
        return render_template("login.html", error="Internal error")
    finally:
        if conn:
            conn.close()

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=user)

# Простая страница профиля (можно расширить)
@app.route("/profile")
def profile():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    return render_template("profile.html", user=user)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

