"""
Alternative migration script to add user_id to previous entries.
This version allows you to choose which existing user should own legacy entries.

Usage: python scripts/migrate_add_user_id_manual.py
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

DB_NAME = "calories.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def list_users():
    """Display all available users."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username, email FROM users ORDER BY id")
    users = cursor.fetchall()
    conn.close()
    
    return users


def get_orphaned_entry_count():
    """Count entries without user_id."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM entries WHERE user_id IS NULL OR user_id = 0")
    result = cursor.fetchone()
    count = result[0] if result else 0
    
    conn.close()
    return count


def assign_entries_to_user(user_id):
    """Assign all orphaned entries to specified user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE entries SET user_id = ? WHERE user_id IS NULL OR user_id = 0",
            (user_id,)
        )
        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected
    except Exception as e:
        print("✗ Error: {}".format(str(e)))
        conn.close()
        return 0


def main():
    """Main routine."""
    print("\n" + "=" * 60)
    print("CalTrack Migration: Assign Legacy Entries to User")
    print("=" * 60)
    
    # Check orphaned entries
    orphaned_count = get_orphaned_entry_count()
    
    if orphaned_count == 0:
        print("\n✓ No orphaned entries found!")
        print("  All entries already have a user_id assigned.")
        return True
    
    print("\nFound {} entries without user_id".format(orphaned_count))
    
    # List available users
    print("\nAvailable users:")
    users = list_users()
    
    if not users:
        print("✗ No users found in database!")
        print("  Please create a user first.")
        return False
    
    for user in users:
        print("  [{}] {} ({})".format(user['id'], user['username'], user['email']))
    
    # Get user choice
    print("\n" + "-" * 60)
    while True:
        try:
            choice = input("Enter user ID to assign {} entries to: ".format(orphaned_count))
            user_id = int(choice)
            
            # Check if user exists
            user_exists = any(u['id'] == user_id for u in users)
            if not user_exists:
                print("✗ User ID {} not found. Try again.".format(user_id))
                continue
            
            break
        except ValueError:
            print("✗ Invalid input. Please enter a number.")
    
    # Confirm action
    selected_user = next(u for u in users if u['id'] == user_id)
    print("\nAssigning {} entries to user: {} ({})".format(
        orphaned_count, 
        selected_user['username'],
        selected_user['email']
    ))
    
    confirm = input("Continue? (y/n): ").lower().strip()
    if confirm != 'y':
        print("\n✗ Migration cancelled.")
        return False
    
    # Perform migration
    print("\nMigrating entries...")
    affected = assign_entries_to_user(user_id)
    
    if affected > 0:
        print("✓ Successfully assigned {} entries!".format(affected))
        
        # Verify
        remaining = get_orphaned_entry_count()
        if remaining == 0:
            print("✓ Migration verified: all entries now have user_id")
        else:
            print("⚠ Warning: {} entries still orphaned".format(remaining))
    else:
        print("✗ No entries were updated.")
        return False
    
    print("\n" + "=" * 60)
    print("Migration completed successfully!")
    print("=" * 60 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✗ Migration cancelled by user.")
        sys.exit(1)
