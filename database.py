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
    
    # User custom habits table (user-specific habit types)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            unit TEXT NOT NULL,
            icon TEXT DEFAULT '📌',
            description TEXT,
            color TEXT DEFAULT 'purple',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, name),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    """)
    
    # Vices entries table (user's vice tracking)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vice_type_id INTEGER,
            habit_id INTEGER,
            quantity REAL NOT NULL,
            entry_date TEXT NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (vice_type_id) REFERENCES vice_types (id) ON DELETE CASCADE,
            FOREIGN KEY (habit_id) REFERENCES user_habits (id) ON DELETE CASCADE
        )
    """)

    # Nutrient Calorie breakdown table (cache results from OpenAI analysis)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS food_calorie_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_key TEXT NOT NULL UNIQUE,        -- normalized lookup key (lowercase, trimmed)
            food_name TEXT NOT NULL,              -- display name from AI
            calories INTEGER NOT NULL,
            hit_count INTEGER DEFAULT 1,          -- track popularity
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute(""" CREATE INDEX IF NOT EXISTS idx_food_key ON food_calorie_cache(food_key) 
     """)
                 
    
    # Nutrient breakdown cache table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nutrient_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            entry_date TEXT NOT NULL,
            protein_grams REAL NOT NULL,
            carbs_grams REAL NOT NULL,
            fats_grams REAL NOT NULL,
            fiber_grams REAL NOT NULL,
            analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, entry_date),
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
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

# Run migration on startup
def migrate_vices_table():
    """Add habit_id column to vices table for existing databases"""
    conn = get_connection()
    try:
        # Check if vices table exists
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vices'")
        if not cursor.fetchone():
            conn.close()
            return
        
        # Get current table schema
        cursor = conn.execute("PRAGMA table_info(vices)")
        columns = {row[1]: row for row in cursor.fetchall()}
        
        # Check if habit_id column exists
        if 'habit_id' not in columns:
            # Need to recreate table with new schema
            # Step 1: Create temp table with data
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vices_old AS SELECT * FROM vices
            """)
            
            # Step 2: Drop old table
            conn.execute("DROP TABLE vices")
            
            # Step 3: Create new table with correct schema
            conn.execute("""
                CREATE TABLE vices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    vice_type_id INTEGER,
                    habit_id INTEGER,
                    quantity REAL NOT NULL,
                    entry_date TEXT NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (vice_type_id) REFERENCES vice_types (id) ON DELETE CASCADE,
                    FOREIGN KEY (habit_id) REFERENCES user_habits (id) ON DELETE CASCADE
                )
            """)
            
            # Step 4: Copy data back (all old entries were system vices)
            conn.execute("""
                INSERT INTO vices (id, user_id, vice_type_id, quantity, entry_date, notes, created_at)
                SELECT id, user_id, vice_type_id, quantity, entry_date, notes, created_at FROM vices_old
            """)
            
            # Step 5: Drop temp table
            conn.execute("DROP TABLE vices_old")
            
            conn.commit()
            print("✓ Migrated: Vices table updated to support custom habits")
        
        # Check if vice_type_id is still NOT NULL (for older migrations)
        elif columns['vice_type_id'][3]:  # col[3] = not_null
            # Recreate table to make vice_type_id nullable
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vices_old AS SELECT * FROM vices
            """)
            
            conn.execute("DROP TABLE vices")
            
            conn.execute("""
                CREATE TABLE vices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    vice_type_id INTEGER,
                    habit_id INTEGER,
                    quantity REAL NOT NULL,
                    entry_date TEXT NOT NULL,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                    FOREIGN KEY (vice_type_id) REFERENCES vice_types (id) ON DELETE CASCADE,
                    FOREIGN KEY (habit_id) REFERENCES user_habits (id) ON DELETE CASCADE
                )
            """)
            
            conn.execute("""
                INSERT INTO vices (id, user_id, vice_type_id, quantity, entry_date, notes, created_at)
                SELECT id, user_id, vice_type_id, quantity, entry_date, notes, created_at FROM vices_old
            """)
            
            conn.execute("DROP TABLE vices_old")
            
            conn.commit()
            print("✓ Migrated: vice_type_id now nullable for custom habits")
        
        conn.close()
    except Exception as e:
        try:
            conn.rollback()
        except:
            pass
        conn.close()
        print(f"✗ Migration error: {str(e)}")

migrate_vices_table()

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

def add_vice_entry(user_id, vice_type_id=None, quantity=None, entry_date=None, notes="", habit_id=None):
    """Add a vice entry (supports both system vice_types and custom user_habits)"""
    conn = get_connection()
    conn.execute(
        """INSERT INTO vices (user_id, vice_type_id, habit_id, quantity, entry_date, notes)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (user_id, vice_type_id, habit_id, quantity, entry_date, notes)
    )
    conn.commit()
    conn.close()

def get_vices_by_date(user_id, entry_date):
    """Get vice entries for a specific date (includes both system and custom habits)"""
    conn = get_connection()
    rows = conn.execute(
        """SELECT v.*, 
                  COALESCE(vt.name, uh.name) as name,
                  COALESCE(vt.unit, uh.unit) as unit,
                  COALESCE(vt.icon, uh.icon) as icon
           FROM vices v
           LEFT JOIN vice_types vt ON v.vice_type_id = vt.id
           LEFT JOIN user_habits uh ON v.habit_id = uh.id
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
    """Get summary of habits (system and custom) for a date"""
    conn = get_connection()
    # Get system vice types summary
    vice_rows = conn.execute(
        """SELECT vt.name, vt.unit, vt.icon, SUM(v.quantity) as total_quantity, COUNT(*) as count
           FROM vices v
           JOIN vice_types vt ON v.vice_type_id = vt.id
           WHERE v.user_id = ? AND v.entry_date = ?
           GROUP BY v.vice_type_id
           ORDER BY vt.name""",
        (user_id, entry_date)
    ).fetchall()
    
    # Get custom habits summary
    habit_rows = conn.execute(
        """SELECT uh.name, uh.unit, uh.icon, SUM(v.quantity) as total_quantity, COUNT(*) as count
           FROM vices v
           JOIN user_habits uh ON v.habit_id = uh.id
           WHERE v.user_id = ? AND v.entry_date = ?
           GROUP BY v.habit_id
           ORDER BY uh.name""",
        (user_id, entry_date)
    ).fetchall()
    
    conn.close()
    all_rows = [dict(row) for row in vice_rows] + [dict(row) for row in habit_rows]
    return sorted(all_rows, key=lambda x: x['name'])

# ============= USER HABITS FUNCTIONS =============

def create_user_habit(user_id, name, unit, icon="📌", description="", color="purple"):
    """Create a new custom habit for user"""
    conn = get_connection()
    try:
        cursor = conn.execute(
            """INSERT INTO user_habits (user_id, name, unit, icon, description, color)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, name.lower().strip(), unit.strip(), icon, description, color)
        )
        conn.commit()
        habit_id = cursor.lastrowid
        conn.close()
        return habit_id
    except Exception as e:
        conn.close()
        raise e

def get_user_habits(user_id):
    """Get all custom habits for a user"""
    conn = get_connection()
    rows = conn.execute(
        """SELECT * FROM user_habits WHERE user_id = ? ORDER BY created_at DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_user_habit_by_id(habit_id, user_id):
    """Get a specific user habit"""
    conn = get_connection()
    row = conn.execute(
        """SELECT * FROM user_habits WHERE id = ? AND user_id = ?""",
        (habit_id, user_id)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def delete_user_habit(habit_id, user_id):
    """Delete a user habit and all associated entries"""
    conn = get_connection()
    try:
        conn.execute(
            """DELETE FROM user_habits WHERE id = ? AND user_id = ?""",
            (habit_id, user_id)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        raise e

def get_all_available_habits(user_id):
    """Get all available habits (system default + user custom)"""
    conn = get_connection()
    
    # Get system default habits (vice_types)
    default_habits = conn.execute(
        """SELECT id, name, unit, icon, 'system' as type FROM vice_types"""
    ).fetchall()
    
    # Get user custom habits
    custom_habits = conn.execute(
        """SELECT id, name, unit, icon, 'custom' as type FROM user_habits WHERE user_id = ?""",
        (user_id,)
    ).fetchall()
    
    conn.close()
    
    result = [dict(row) for row in default_habits] + [dict(row) for row in custom_habits]
    return result

# ============= NUTRIENT DATA FUNCTIONS =============

def save_nutrient_data(user_id, entry_date, protein, carbs, fats, fiber, analysis):
    """Save or update nutrient breakdown for a date"""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT OR REPLACE INTO nutrient_data 
               (user_id, entry_date, protein_grams, carbs_grams, fats_grams, fiber_grams, analysis)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (user_id, entry_date, protein, carbs, fats, fiber, analysis)
        )
        conn.commit()
        conn.close()
        return True
    except Exception:
        conn.close()
        return False

def get_nutrient_data(user_id, entry_date):
    """Get cached nutrient breakdown for a date"""
    conn = get_connection()
    row = conn.execute(
        """SELECT protein_grams, carbs_grams, fats_grams, fiber_grams, analysis
           FROM nutrient_data
           WHERE user_id = ? AND entry_date = ?""",
        (user_id, entry_date)
    ).fetchone()
    conn.close()
    return dict(row) if row else None

def delete_nutrient_data(user_id, entry_date):
    """Delete cached nutrient data for a date"""
    conn = get_connection()
    conn.execute(
        "DELETE FROM nutrient_data WHERE user_id = ? AND entry_date = ?",
        (user_id, entry_date)
    )
    conn.commit()
    conn.close()

