"""
Script to manually add entries to the database.
Allows you to add user_id, food_item, and calorie data interactively.

Usage: python scripts/add_entry_manual.py
"""

import sqlite3
import sys
from pathlib import Path
from datetime import date, datetime

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


def get_user_entries_count(user_id):
    """Get count of entries for a user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM entries WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    count = result[0] if result else 0
    
    conn.close()
    return count


def add_entry(user_id, entry_date, food_item, calories):
    """Add a single entry to the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO entries (user_id, entry_date, food_item, calories) VALUES (?, ?, ?, ?)",
            (user_id, entry_date, food_item, calories)
        )
        conn.commit()
        entry_id = cursor.lastrowid
        conn.close()
        return entry_id
    except Exception as e:
        conn.close()
        return None


def validate_date(date_str):
    """Validate date string format YYYY-MM-DD."""
    try:
        parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
        return parsed_date.date().isoformat()
    except ValueError:
        return None


def validate_calories(calories_str):
    """Validate calories is a positive integer."""
    try:
        calories = int(calories_str)
        if calories <= 0:
            return None
        return calories
    except ValueError:
        return None


def select_user():
    """Let user select from available users."""
    users = list_users()
    
    if not users:
        print("\n✗ No users found in database!")
        print("  Please create a user first via the web app.")
        return None
    
    print("\nAvailable Users:")
    for user in users:
        count = get_user_entries_count(user['id'])
        print("  [{}] {} ({}) - {} entries".format(
            user['id'],
            user['username'],
            user['email'],
            count
        ))
    
    print("\n" + "-" * 60)
    while True:
        try:
            choice = input("Enter user ID: ").strip()
            user_id = int(choice)
            
            if not any(u['id'] == user_id for u in users):
                print("✗ User not found. Try again.")
                continue
            
            return user_id
        except ValueError:
            print("✗ Invalid input. Enter a number.")


def select_date():
    """Get entry date from user."""
    print("\n" + "-" * 60)
    print("Entry Date")
    today = date.today().isoformat()
    default_str = "(default: today - {})".format(today)
    
    while True:
        date_input = input("Enter date (YYYY-MM-DD) {}: ".format(default_str)).strip()
        
        if not date_input:
            return today
        
        validated = validate_date(date_input)
        if validated:
            return validated
        
        print("✗ Invalid date format. Use YYYY-MM-DD")


def get_food_item():
    """Get food item name from user."""
    print("\n" + "-" * 60)
    
    while True:
        food = input("Enter food item (e.g., Apple, Chicken Rice, Coffee): ").strip()
        
        if not food:
            print("✗ Food item cannot be empty.")
            continue
        
        if len(food) > 100:
            print("✗ Food item too long (max 100 characters).")
            continue
        
        return food


def get_calories():
    """Get calorie amount from user."""
    print("\n" + "-" * 60)
    
    while True:
        cal_input = input("Enter calories (positive integer): ").strip()
        
        validated = validate_calories(cal_input)
        if validated:
            return validated
        
        print("✗ Invalid calorie value. Enter a positive integer.")


def confirm_entry(user_id, entry_date, food_item, calories):
    """Show summary and ask for confirmation."""
    users = list_users()
    user_name = next(
        (u['username'] for u in users if u['id'] == user_id),
        "Unknown"
    )
    
    print("\n" + "=" * 60)
    print("Entry Summary")
    print("=" * 60)
    print("User:       {}".format(user_name))
    print("Date:       {}".format(entry_date))
    print("Food:       {}".format(food_item))
    print("Calories:   {}".format(calories))
    print("=" * 60)
    
    while True:
        confirm = input("\nSave this entry? (y/n): ").lower().strip()
        if confirm in ['y', 'n']:
            return confirm == 'y'


def add_another():
    """Ask if user wants to add another entry."""
    while True:
        choice = input("\nAdd another entry? (y/n): ").lower().strip()
        if choice in ['y', 'n']:
            return choice == 'y'


def show_user_summary(user_id):
    """Show user's current entry count."""
    users = list_users()
    user = next((u for u in users if u['id'] == user_id), None)
    
    if not user:
        return
    
    count = get_user_entries_count(user_id)
    print("\n✓ {} now has {} total entries".format(user['username'], count))


def main():
    """Main application flow."""
    print("\n" + "=" * 60)
    print("CalTrack - Manual Entry Addition")
    print("=" * 60)
    
    total_added = 0
    
    # Select user
    user_id = select_user()
    if not user_id:
        return False
    
    # Main loop
    while True:
        # Get entry details
        entry_date = select_date()
        food_item = get_food_item()
        calories = get_calories()
        
        # Confirm
        if not confirm_entry(user_id, entry_date, food_item, calories):
            print("✗ Entry cancelled.")
            if not add_another():
                break
            continue
        
        # Add to database
        entry_id = add_entry(user_id, entry_date, food_item, calories)
        
        if entry_id:
            print("\n✓ Entry added successfully (ID: {})".format(entry_id))
            total_added += 1
            show_user_summary(user_id)
        else:
            print("\n✗ Failed to add entry. Please try again.")
        
        # Ask if adding more
        if not add_another():
            break
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print("Total entries added: {}".format(total_added))
    print("=" * 60 + "\n")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user.")
        sys.exit(1)


