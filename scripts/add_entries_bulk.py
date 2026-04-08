"""
Script to bulk add entries from a CSV file.
Allows you to add multiple user_id, food_item, and calorie data at once.

CSV Format:
user_id,date,food_item,calories
1,2026-04-08,Breakfast - Eggs and Toast,350
1,2026-04-08,Lunch - Chicken Salad,450
1,2026-04-08,Snack - Apple,80
2,2026-04-07,Breakfast - Oatmeal,300

Usage: python scripts/add_entries_bulk.py sample_entries.csv
"""

import sqlite3
import sys
import csv
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

DB_NAME = "calories.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def validate_user_exists(user_id):
    """Check if user exists in database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result is not None


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


def get_username(user_id):
    """Get username by user_id."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    return result['username'] if result else None


def process_csv_file(csv_path):
    """Process CSV file and add entries to database."""
    if not Path(csv_path).exists():
        print("✗ File not found: {}".format(csv_path))
        return False
    
    print("\n" + "=" * 70)
    print("CalTrack - Bulk Entry Addition")
    print("=" * 70)
    print("Reading: {}\n".format(csv_path))
    
    added = 0
    failed = 0
    errors = []
    
    try:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            
            if not reader.fieldnames or reader.fieldnames != ['user_id', 'date', 'food_item', 'calories']:
                print("✗ CSV must have columns: user_id, date, food_item, calories")
                return False
            
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                user_id_str = row['user_id'].strip()
                date_str = row['date'].strip()
                food_item = row['food_item'].strip()
                calories_str = row['calories'].strip()
                
                # Validate user_id
                try:
                    user_id = int(user_id_str)
                except ValueError:
                    errors.append("Row {}: Invalid user_id '{}'".format(row_num, user_id_str))
                    failed += 1
                    continue
                
                if not validate_user_exists(user_id):
                    errors.append("Row {}: User ID {} does not exist".format(row_num, user_id))
                    failed += 1
                    continue
                
                # Validate date
                validated_date = validate_date(date_str)
                if not validated_date:
                    errors.append("Row {}: Invalid date format '{}' (use YYYY-MM-DD)".format(row_num, date_str))
                    failed += 1
                    continue
                
                # Validate food item
                if not food_item:
                    errors.append("Row {}: Food item cannot be empty".format(row_num))
                    failed += 1
                    continue
                
                if len(food_item) > 100:
                    errors.append("Row {}: Food item too long (max 100 chars)".format(row_num))
                    failed += 1
                    continue
                
                # Validate calories
                validated_calories = validate_calories(calories_str)
                if not validated_calories:
                    errors.append("Row {}: Invalid calories '{}' (must be positive integer)".format(
                        row_num, calories_str
                    ))
                    failed += 1
                    continue
                
                # Add entry
                entry_id = add_entry(user_id, validated_date, food_item, validated_calories)
                
                if entry_id:
                    username = get_username(user_id)
                    print("✓ Row {}: Added entry {} for user {} ({} cal)".format(
                        row_num, entry_id, username, validated_calories
                    ))
                    added += 1
                else:
                    errors.append("Row {}: Database insertion failed".format(row_num))
                    failed += 1
    
    except csv.Error as e:
        print("✗ CSV parsing error: {}".format(e))
        return False
    except Exception as e:
        print("✗ Unexpected error: {}".format(e))
        return False
    
    # Show summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    print("Total entries processed: {}".format(added + failed))
    print("Successfully added:     {}".format(added))
    print("Failed:                 {}".format(failed))
    
    if errors:
        print("\nErrors:")
        for error in errors[:10]:  # Show first 10 errors
            print("  - {}".format(error))
        if len(errors) > 10:
            print("  ... and {} more errors".format(len(errors) - 10))
    
    print("=" * 70 + "\n")
    
    return True


def create_sample_csv():
    """Create a sample CSV file."""
    sample_path = "sample_entries.csv"
    
    if Path(sample_path).exists():
        print("Sample file already exists: {}".format(sample_path))
        return
    
    with open(sample_path, 'w') as f:
        f.write("user_id,date,food_item,calories\n")
        f.write("1,2026-04-08,Breakfast - Eggs and Toast,350\n")
        f.write("1,2026-04-08,Lunch - Chicken Salad,450\n")
        f.write("1,2026-04-08,Snack - Apple,80\n")
        f.write("1,2026-04-09,Breakfast - Oatmeal,300\n")
        f.write("2,2026-04-08,Morning - Coffee,5\n")
        f.write("2,2026-04-08,Lunch - Pasta,600\n")
    
    print("✓ Created sample file: {}".format(sample_path))


def main():
    """Main application."""
    if len(sys.argv) < 2:
        print("\n" + "=" * 70)
        print("CalTrack - Bulk Entry Addition")
        print("=" * 70)
        print("\nUsage: python scripts/add_entries_bulk.py <csv_file>")
        print("\nCSV Format (user_id, date, food_item, calories):")
        print("  user_id,date,food_item,calories")
        print("  1,2026-04-08,Breakfast Eggs,350")
        print("  1,2026-04-08,Lunch Salad,450")
        print("  1,2026-04-08,Snack Apple,80\n")
        
        response = input("Create a sample CSV file? (y/n): ").strip().lower()
        if response == 'y':
            create_sample_csv()
            print("\nEdit sample_entries.csv and run:")
            print("  python scripts/add_entries_bulk.py sample_entries.csv\n")
        
        return False
    
    csv_file = sys.argv[1]
    return process_csv_file(csv_file)


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n✗ Operation cancelled by user.")
        sys.exit(1)
