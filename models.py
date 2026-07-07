import sqlite3

from config import DB_PATH


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            client TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
    )
    conn.commit()
    conn.close()


def add_user(username, password_hash):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
        (username, password_hash),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id


def get_user_by_username(username):
    conn = get_connection()
    user = conn.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def get_user_by_id(user_id):
    conn = get_connection()
    user = conn.execute(
        "SELECT id, username FROM users WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def create_order(title, client, description, status, user_id):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO orders (title, client, description, status, user_id) VALUES (?, ?, ?, ?, ?)",
        (title, client, description, status, user_id),
    )
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id


def get_orders(user_id):
    conn = get_connection()
    orders = conn.execute(
        "SELECT id, title, client, description, status FROM orders WHERE user_id = ? ORDER BY id DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(order) for order in orders]


def get_order(order_id, user_id):
    conn = get_connection()
    order = conn.execute(
        "SELECT id, title, client, description, status FROM orders WHERE id = ? AND user_id = ?",
        (order_id, user_id),
    ).fetchone()
    conn.close()
    return dict(order) if order else None


def update_order(order_id, title, client, description, status, user_id):
    conn = get_connection()
    conn.execute(
        "UPDATE orders SET title = ?, client = ?, description = ?, status = ? WHERE id = ? AND user_id = ?",
        (title, client, description, status, order_id, user_id),
    )
    conn.commit()
    conn.close()


def delete_order(order_id, user_id):
    conn = get_connection()
    conn.execute("DELETE FROM orders WHERE id = ? AND user_id = ?", (order_id, user_id))
    conn.commit()
    conn.close()
