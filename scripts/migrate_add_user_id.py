"""
Migration script to add user_id to previous entries.
This script handles entries that were created before the user_id concept was introduced.

Usage: python scripts/migrate_add_user_id.py
"""

import sqlite3
import sys
from pathlib import Path
from werkzeug.security import generate_password_hash

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

DB_NAME = "calories.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def check_database_status():
    """Check the current state of the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if entries table has user_id column
    cursor.execute("PRAGMA table_info(entries)")
    columns = cursor.fetchall()
    has_user_id = any(col[1] == 'user_id' for col in columns)
    
    # Count entries
    cursor.execute("SELECT COUNT(*) FROM entries")
    entry_count = cursor.fetchone()[0]
    
    # Count users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    # Count entries with NULL user_id (if column exists)
    null_user_count = 0
    if has_user_id:
        cursor.execute("SELECT COUNT(*) FROM entries WHERE user_id IS NULL")
        result = cursor.fetchone()
        null_user_count = result[0] if result else 0
    
    conn.close()
    
    return {
        'has_user_id': has_user_id,
        'total_entries': entry_count,
        'total_users': user_count,
        'null_user_entries': null_user_count
    }


def create_legacy_user():
    """Create a 'legacy' user to own previous entries."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if legacy user already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", ('legacy_admin',))
    existing = cursor.fetchone()
    
    if existing:
        print("✓ Legacy user already exists (ID: {})".format(existing[0]))
        conn.close()
        return existing[0]
    
    # Create legacy user
    password_hash = generate_password_hash('default_legacy_password')
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            ('legacy_admin', 'legacy@caltrack.local', password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        print("✓ Created legacy user with ID: {}".format(user_id))
        conn.close()
        return user_id
    except sqlite3.IntegrityError as e:
        print("✗ Error creating legacy user: {}".format(str(e)))
        conn.close()
        return None


def migrate_entries(user_id):
    """Assign all orphaned entries to the specified user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get count of entries to be updated
        cursor.execute("SELECT COUNT(*) FROM entries WHERE user_id IS NULL OR user_id = 0")
        result = cursor.fetchone()
        count = result[0] if result else 0
        
        if count == 0:
            print("✓ No entries to migrate (all entries already have user_id)")
            conn.close()
            return True
        
        print("\nMigrating {} entries...".format(count))
        
        # Update entries with NULL or 0 user_id
        cursor.execute(
            "UPDATE entries SET user_id = ? WHERE user_id IS NULL OR user_id = 0",
            (user_id,)
        )
        conn.commit()
        
        print("✓ Successfully migrated {} entries".format(count))
        return True
        
    except Exception as e:
        print("✗ Error during migration: {}".format(str(e)))
        conn.rollback()
        return False
    finally:
        conn.close()


def verify_migration():
    """Verify that the migration was successful."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check for any remaining entries with NULL user_id
    cursor.execute("SELECT COUNT(*) FROM entries WHERE user_id IS NULL")
    null_count = cursor.fetchone()[0]
    
    # Get entry count by user
    cursor.execute("""
        SELECT u.username, COUNT(e.id) as entry_count
        FROM users u
        LEFT JOIN entries e ON u.id = e.user_id
        GROUP BY u.id, u.username
    """)
    user_stats = cursor.fetchall()
    
    conn.close()
    
    if null_count > 0:
        print("\n✗ Migration verification FAILED!")
        print("  {} entries still have NULL user_id".format(null_count))
        return False
    
    print("\n✓ Migration verification PASSED!")
    print("\nEntry Distribution:")
    for stat in user_stats:
        count = stat[1] if stat[1] else 0
        print("  - {}: {} entries".format(stat[0], count))
    
    return True


def main():
    """Main migration routine."""
    print("=" * 60)
    print("CalTrack Migration: Add user_id to Previous Entries")
    print("=" * 60)
    
    # Check current database status
    print("\n1. Checking database status...")
    status = check_database_status()
    
    print("  - Total users: {}".format(status['total_users']))
    print("  - Total entries: {}".format(status['total_entries']))
    print("  - Entries needing migration: {}".format(status['null_user_entries']))
    
    if status['total_entries'] == 0:
        print("\n✓ No entries to migrate. Database is clean!")
        return True
    
    if status['null_user_entries'] == 0:
        print("\n✓ All entries already have user_id. Migration not needed!")
        return True
    
    # Create legacy user
    print("\n2. Creating/verifying legacy user...")
    legacy_user_id = create_legacy_user()
    
    if not legacy_user_id:
        print("\n✗ Failed to create legacy user. Aborting migration.")
        return False
    
    # Migrate entries
    print("\n3. Migrating entries...")
    if not migrate_entries(legacy_user_id):
        print("\n✗ Migration failed. Aborting.")
        return False
    
    # Verify migration
    print("\n4. Verifying migration...")
    if not verify_migration():
        return False
    
    print("\n" + "=" * 60)
    print("✓ Migration completed successfully!")
    print("=" * 60)
    print("\nNotes:")
    print("  - Legacy entries are now owned by 'legacy_admin' user")
    print("  - You can change the owner by updating the user_id")
    print("  - All future entries will be properly associated with their user")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
