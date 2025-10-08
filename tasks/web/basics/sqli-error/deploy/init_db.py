# init_db.py
# Инициализация MySQL БД и тестовых данных (users + secrets)
import pymysql

CFG = dict(host="db", port=3306, user="root", password="root", charset="utf8mb4", autocommit=True)

DB = "sqli_accounts"

conn = pymysql.connect(**CFG)
cur = conn.cursor()
cur.execute(f"DROP DATABASE IF EXISTS {DB};")
cur.execute(f"CREATE DATABASE {DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;")
cur.execute(f"USE {DB};")

# Таблица пользователей (для логина, хранится хеш пароля)
cur.execute("DROP TABLE IF EXISTS users;")
cur.execute("""
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(150) UNIQUE,
  password_hash VARCHAR(255)
) ENGINE=InnoDB;
""")

# Таблица secrets — сюда положим флаг/секрет для CTF (чтобы error-based инъекция могла вытянуть его через ошибку)
cur.execute("DROP TABLE IF EXISTS secrets;")
cur.execute("""
CREATE TABLE secrets (
  id INT PRIMARY KEY,
  name VARCHAR(50),
  secret TEXT
) ENGINE=InnoDB;
""")

FLAG = "FLAG{error_based_account_2025}"
cur.execute("INSERT INTO secrets (id, name, secret) VALUES (1, 'admin', %s);", (FLAG,))

# Для удобства создадим тестового пользователя: user / password: P@ssw0rd
from werkzeug.security import generate_password_hash
pwd_hash = generate_password_hash("P@ssw0rd")
cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s);", ("testuser", pwd_hash))

print("DB initialized:", DB)
cur.close()
conn.close()

