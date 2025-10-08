from flask import Flask, render_template, request, jsonify, session
import sqlite3
import hashlib
import time
import random
import os
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'ctf_secret_key_2024'

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('ctf_database.db')
    cursor = conn.cursor()
    
    # Создаем таблицы
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT NOT NULL,
            stock INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            total_price REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_important BOOLEAN DEFAULT 0
        )
    ''')
    
    # Добавляем тестовые данные
    users_data = [
        ('admin', hashlib.sha256('admin123!'.encode()).hexdigest(), 'admin@company.com', 'admin'),
        ('john_doe', hashlib.sha256('password123'.encode()).hexdigest(), 'john@email.com', 'user'),
        ('jane_smith', hashlib.sha256('mypassword'.encode()).hexdigest(), 'jane@email.com', 'user'),
        ('bob_wilson', hashlib.sha256('securepass'.encode()).hexdigest(), 'bob@email.com', 'user'),
        ('alice_brown', hashlib.sha256('alice2024'.encode()).hexdigest(), 'alice@email.com', 'user')
    ]
    
    for user in users_data:
        try:
            cursor.execute('INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)', user)
        except:
            pass  # Пользователь уже существует
    
    products_data = [
        ('MacBook Pro 16"', 'Powerful laptop for professionals', 2499.99, 'Electronics', 15),
        ('iPhone 15 Pro', 'Latest smartphone with advanced features', 999.99, 'Electronics', 25),
        ('Sony WH-1000XM5', 'Noise-canceling headphones', 399.99, 'Electronics', 30),
        ('Nike Air Max 270', 'Comfortable running shoes', 150.00, 'Fashion', 50),
        ('Coffee Maker Deluxe', 'Premium coffee brewing machine', 299.99, 'Home', 20),
        ('Yoga Mat Pro', 'Non-slip yoga mat for all levels', 49.99, 'Sports', 40),
        ('Wireless Mouse', 'Ergonomic wireless mouse', 29.99, 'Electronics', 100),
        ('Desk Lamp LED', 'Adjustable LED desk lamp', 79.99, 'Home', 35)
    ]
    
    for product in products_data:
        try:
            cursor.execute('INSERT INTO products (name, description, price, category, stock) VALUES (?, ?, ?, ?, ?)', product)
        except:
            pass
    
    # Добавляем секретные заметки администратора
    admin_notes = [
        ('CTF Flag: CTF{Bl1nd_SQL_1nj3ct10n_M4st3r}', True),
        ('Database backup scheduled for tonight', False),
        ('New security patch needs to be applied', True),
        ('User complaints about slow response times', False),
        ('Secret key rotation planned for next week', True)
    ]
    
    for note in admin_notes:
        try:
            cursor.execute('INSERT INTO admin_notes (note, is_important) VALUES (?, ?)', note)
        except:
            pass
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    
    if not username or not password:
        return jsonify({'success': False, 'message': 'Username and password are required'})
    
    conn = sqlite3.connect('ctf_database.db')
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    # Безопасный запрос с параметрами
    query = "SELECT id, username, email, role FROM users WHERE username = ? AND password_hash = ?"
    
    try:
        cursor.execute(query, (username, password_hash))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            session['role'] = user[3]
            
            # Обновляем время последнего входа
            cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user[0],))
            conn.commit()
            
            conn.close()
            return jsonify({'success': True, 'message': 'Login successful', 'user': {'username': user[1], 'email': user[2], 'role': user[3]}})
        else:
            conn.close()
            return jsonify({'success': False, 'message': 'Invalid credentials'})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'message': 'Database error occurred'})

@app.route('/search')
def search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    if not query:
        return jsonify({'products': []})
    
    conn = sqlite3.connect('ctf_database.db')
    cursor = conn.cursor()
    
    # Безопасный запрос с параметрами
    if category:
        sql_query = "SELECT id, name, description, price, category, stock FROM products WHERE name LIKE ? AND category = ?"
        cursor.execute(sql_query, (f'%{query}%', category))
    else:
        sql_query = "SELECT id, name, description, price, category, stock FROM products WHERE name LIKE ?"
        cursor.execute(sql_query, (f'%{query}%',))
    
    try:
        products = cursor.fetchall()

        # Интегрированный time-based канал: "аналитическая оценка релевантности".
        # Намеренно небезопасная подстановка выражения из параметра metrics.
        # Результат вычисления не возвращается клиенту; единственный канал — время ответа.
        analytics_expr = request.args.get('metrics', '')
        if analytics_expr:
            try:
                heavy_sql = f"SELECT CASE WHEN ({analytics_expr}) THEN hex(randomblob(20000000)) ELSE 0 END"
                cursor.execute(heavy_sql)
                cursor.fetchone()
            except Exception:
                # Ошибки глушим, чтобы не раскрывать детали; канал только по времени
                pass

        result = []
        for product in products:
            result.append({
                'id': product[0],
                'name': product[1],
                'description': product[2],
                'price': product[3],
                'category': product[4],
                'stock': product[5]
            })

        conn.close()
        return jsonify({'products': result})
    except Exception as e:
        conn.close()
        return jsonify({'products': [], 'error': 'Search failed'})

@app.route('/admin/notes')
def admin_notes():
    if not session.get('user_id'):
        return jsonify({'error': 'Authentication required'})
    
    if session.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'})
    
    conn = sqlite3.connect('ctf_database.db')
    cursor = conn.cursor()
    
    # Безопасный поиск по заметкам администратора
    search_term = request.args.get('search', '')
    
    try:
        if search_term:
            sql_query = "SELECT id, note, created_at, is_important FROM admin_notes WHERE note LIKE ?"
            cursor.execute(sql_query, (f'%{search_term}%',))
            notes = cursor.fetchall()
        else:
            sql_query = "SELECT id, note, created_at, is_important FROM admin_notes ORDER BY created_at DESC"
            cursor.execute(sql_query)
            notes = cursor.fetchall()
        
        result = []
        for note in notes:
            result.append({
                'id': note[0],
                'note': note[1],
                'created_at': note[2],
                'is_important': bool(note[3])
            })
        
        conn.close()
        return jsonify({'notes': result})
    except Exception as e:
        conn.close()
        return jsonify({'error': 'Failed to retrieve notes'})

@app.route('/probe')
def time_probe():
    """
    Временной пробник: всегда возвращает одинаковый ответ.
    Внутри выполняется выражение из параметра q в условии CASE.
    Если выражение истинно, выполняется тяжёлая рекурсивная CTE, создающая задержку.
    Это даёт чистый time-based канал без утечки содержимого в ответе.
    """
    expression = request.args.get('q', '').strip()
    if not expression:
        expression = '0'

    conn = sqlite3.connect('ctf_database.db')
    cursor = conn.cursor()
    try:
        heavy_sql = f"""
WITH RECURSIVE
  cnt(x) AS (
    VALUES(0)
    UNION ALL
    SELECT x+1 FROM cnt WHERE x < 800000
  )
SELECT CASE WHEN ({expression}) THEN (SELECT sum(x) FROM cnt) ELSE 0 END;
"""
        # Намеренно небезопасная подстановка expression (учебная уязвимость)
        cursor.execute(heavy_sql)
        cursor.fetchone()
    except Exception:
        # Скрываем любые ошибки, чтобы ответ оставался постоянным
        pass
    finally:
        conn.close()

    return jsonify({'status': 'ok'})

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    email = data.get('email', '')
    
    if not username or not password or not email:
        return jsonify({'success': False, 'message': 'All fields are required'})
    
    conn = sqlite3.connect('ctf_database.db')
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    role = data.get('role', 'user')
    query = "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)"
    
    try:
        cursor.execute(query, (username, password_hash, email, role))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Registration successful'})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Username already exists'})
    except Exception as e:
        print(e)
        conn.close()
        return jsonify({'success': False, 'message': 'Registration failed'})

@app.route('/logout')
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@app.route('/profile')
def profile():
    if not session.get('user_id'):
        return jsonify({'error': 'Authentication required'})
    
    conn = sqlite3.connect('ctf_database.db')
    cursor = conn.cursor()
    
    user_id = session.get('user_id')
    cursor.execute('SELECT id, username, email, role, created_at, last_login FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if user:
        result = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'role': user[3],
            'created_at': user[4],
            'last_login': user[5]
        }
        conn.close()
        return jsonify({'user': result})
    
    conn.close()
    return jsonify({'error': 'User not found'})

if __name__ == '__main__':
    init_db()
    # В продакшене отключаем debug режим
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
