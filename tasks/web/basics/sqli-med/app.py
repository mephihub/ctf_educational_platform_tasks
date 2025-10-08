# app.py
import sqlite3
from flask import Flask, request, g, render_template_string, redirect, url_for

app = Flask(__name__)
DATABASE = "task.db"

TEMPLATE = """
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Search MEDIUM</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <div class="container-fluid">
    <a class="navbar-brand" href="{{ url_for('index') }}">SQLi-CTF</a>
  </div>
</nav>

<div class="container py-5">
  <div class="row">
    <div class="col-lg-8 mx-auto">
      <div class="card shadow-sm">
        <div class="card-body">
          <h3 class="card-title mb-3">Поиск по товарам</h3>
          <p class="text-muted small">Введи поисковый запрос</p>

          <form method="get" action="{{ url_for('search') }}" class="mb-3">
            <div class="input-group">
              <input name="q" class="form-control" placeholder="search title (e.g. Alpha)" value="{{ q|e }}">
              <button class="btn btn-primary">Search</button>
            </div>
          </form>

          <div>
            <h6 class="mb-2">Результаты</h6>
            {% if rows %}
              <div class="table-responsive">
                <table class="table table-sm table-hover">
                  <thead class="table-light">
                    <tr><th>ID</th><th>Title</th><th>Description</th></tr>
                  </thead>
                  <tbody>
                    {% for r in rows %}
                    <tr>
                      <td>{{ r[0] }}</td>
                      <td>{{ r[1] }}</td>
                      <td>{{ r[2] }}</td>
                    </tr>
                    {% endfor %}
                  </tbody>
                </table>
              </div>
            {% else %}
              <div class="alert alert-info py-2">Ничего не найдено.</div>
            {% endif %}
          </div>

          <hr>
        </div>
      </div>

      <div class="text-center mt-3 text-muted small">
        Для обучения. Запускать локально.
      </div>
    </div>
  </div>
</div>
</body>
</html>
"""

def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DATABASE)
    return db

def init_db():
    db = sqlite3.connect(DATABASE)
    cur = db.cursor()
    cur.execute("DROP TABLE IF EXISTS items;")
    cur.execute("""
      CREATE TABLE items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT
      );
    """)
    cur.executemany("INSERT INTO items (title, description) VALUES (?, ?);", [
        ("Alpha", "First item"),
        ("Bravo", "Second item"),
        ("Charlie", "Third item")
    ])

    cur.execute("DROP TABLE IF EXISTS secrets;")
    cur.execute("""
      CREATE TABLE secrets (
        id INTEGER PRIMARY KEY,
        name TEXT,
        secret TEXT
      );
    """)

    FLAG = "FLAG{sql_injection_2025_3534767cb3c73ff87e26fb688b41797f}"
    cur.execute("INSERT INTO secrets (id, name, secret) VALUES (1, 'admin', ?);", (FLAG,))
    db.commit()
    db.close()

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return redirect(url_for("search"))

@app.route("/search")
def search():
    q = request.args.get("q", "")
    db = get_db()
    cur = db.cursor()

    sql = f"SELECT id, title, description FROM items WHERE title = '{q}';"

    try:
        cur.execute(sql)
        rows = cur.fetchall()
    except Exception as e:
        rows = []
        print("SQL Error:", e)
    return render_template_string(TEMPLATE, q=q, rows=rows)

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="127.0.0.1", port=5000)

