import sqlite3
from datetime import date

DB_NAME = "calories.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            entry_date TEXT NOT NULL,
            food_item TEXT NOT NULL,
            calories INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()


# User Management Functions
def create_user(username, email, password_hash):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, password_hash)
        )
        conn.commit()
        user = conn.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        ).fetchone()
        conn.close()
        return user["id"] if user else None
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_user_by_username(username):
    conn = get_connection()
    user = conn.execute(
        "SELECT id, username, email, password_hash FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_connection()
    user = conn.execute(
        "SELECT id, username, email FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    return user


# Entry Management Functions (user-specific)
def get_entries_by_date(user_id, entry_date):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM entries WHERE user_id = ? AND entry_date = ? ORDER BY created_at DESC",
        (user_id, entry_date)
    ).fetchall()
    conn.close()
    return rows


def add_entry(user_id, entry_date, food_item, calories):
    conn = get_connection()
    conn.execute(
        "INSERT INTO entries (user_id, entry_date, food_item, calories) VALUES (?, ?, ?, ?)",
        (user_id, entry_date, food_item, calories)
    )
    conn.commit()
    conn.close()


def delete_entry(entry_id, user_id):
    conn = get_connection()
    conn.execute("DELETE FROM entries WHERE id = ? AND user_id = ?", (entry_id, user_id))
    conn.commit()
    conn.close()


def get_all_dates(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT entry_date FROM entries WHERE user_id = ? ORDER BY entry_date DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [row["entry_date"] for row in rows]


def get_total_calories(user_id, entry_date):
    conn = get_connection()
    result = conn.execute(
        "SELECT SUM(calories) as total FROM entries WHERE user_id = ? AND entry_date = ?",
        (user_id, entry_date)
    ).fetchone()
    conn.close()
    return result["total"] or 0
