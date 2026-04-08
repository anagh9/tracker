"""
Database module for Tracker App
Handles: Users, Calorie Entries, Vices Entries
"""

import sqlite3
from datetime import date
from config import Config

DB_NAME = Config.DATABASE

def get_connection():
    """Get database connection with Row factory"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables"""
    conn = get_connection()
    
    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Calorie entries table
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
    
    # Vice types table (define types of vices)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vice_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            unit TEXT NOT NULL,
            description TEXT,
            icon TEXT
        )
    """)
    
    # Vices entries table (user's vice tracking)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vice_type_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            entry_date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (vice_type_id) REFERENCES vice_types (id) ON DELETE CASCADE
        )
    """)
    
    # Insert default vice types if not exists
    vice_type_defaults = [
        ("cigarettes", "count", "Cigarettes smoked", "🚬"),
        ("alcohol", "ml", "Alcoholic beverages", "🍷"),
        ("coffee", "count", "Cups of coffee", "☕"),
    ]
    
    for name, unit, desc, icon in vice_type_defaults:
        conn.execute(
            "INSERT OR IGNORE INTO vice_types (name, unit, description, icon) VALUES (?, ?, ?, ?)",
            (name, unit, desc, icon)
        )
    
    conn.commit()
    conn.close()

# ============= USER MANAGEMENT FUNCTIONS =============

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
        "SELECT id, username, email, password_hash FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    return user


def get_user_by_email(email):
    """Get user by email address for OAuth login"""
    conn = get_connection()
    user = conn.execute(
        "SELECT id, username, email FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()
    return user


def update_user_password(user_id, password_hash):
    """Update user password"""
    try:
        conn = get_connection()
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        return False


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

# ============= VICE TYPES FUNCTIONS =============

def get_all_vice_types():
    """Get all available vice types"""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM vice_types ORDER BY name").fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_vice_type_by_id(vice_type_id):
    """Get vice type by ID"""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM vice_types WHERE id = ?",
        (vice_type_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def get_vice_type_by_name(name):
    """Get vice type by name"""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM vice_types WHERE name = ?",
        (name,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

# ============= VICE ENTRIES FUNCTIONS =============

def add_vice_entry(user_id, vice_type_id, quantity, entry_date, notes=""):
    """Add a vice entry"""
    conn = get_connection()
    conn.execute(
        """INSERT INTO vices (user_id, vice_type_id, quantity, entry_date, notes)
           VALUES (?, ?, ?, ?, ?)""",
        (user_id, vice_type_id, quantity, entry_date, notes)
    )
    conn.commit()
    conn.close()

def get_vices_by_date(user_id, entry_date):
    """Get vice entries for a specific date"""
    conn = get_connection()
    rows = conn.execute(
        """SELECT v.*, vt.name, vt.unit, vt.icon 
           FROM vices v
           JOIN vice_types vt ON v.vice_type_id = vt.id
           WHERE v.user_id = ? AND v.entry_date = ?
           ORDER BY v.created_at DESC""",
        (user_id, entry_date)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def delete_vice_entry(entry_id, user_id):
    """Delete a vice entry"""
    conn = get_connection()
    conn.execute(
        "DELETE FROM vices WHERE id = ? AND user_id = ?",
        (entry_id, user_id)
    )
    conn.commit()
    conn.close()

def get_vice_dates(user_id):
    """Get all dates with vice entries"""
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT entry_date FROM vices WHERE user_id = ? ORDER BY entry_date DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [row["entry_date"] for row in rows]

def get_vice_summary(user_id, entry_date):
    """Get summary of vices for a date"""
    conn = get_connection()
    rows = conn.execute(
        """SELECT vt.name, vt.unit, vt.icon, SUM(v.quantity) as total_quantity, COUNT(*) as count
           FROM vices v
           JOIN vice_types vt ON v.vice_type_id = vt.id
           WHERE v.user_id = ? AND v.entry_date = ?
           GROUP BY v.vice_type_id
           ORDER BY vt.name""",
        (user_id, entry_date)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
