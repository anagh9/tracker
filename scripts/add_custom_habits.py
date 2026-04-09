#!/usr/bin/env python3
"""
Add sample custom habits for testing
Adds 20+ predefined habits to demonstrate the habit creation feature
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database

# Sample habits with emoji, unit, description
SAMPLE_HABITS = [
    # Exercise & Health
    ("Running", "miles", "🏃", "Track daily running distance"),
    ("Gym Workout", "minutes", "💪", "Time spent at the gym"),
    ("Yoga", "minutes", "🧘", "Yoga practice sessions"),
    ("Walking", "steps", "🚶", "Daily walking steps"),
    ("Swimming", "laps", "🏊", "Swimming pool sessions"),
    
    # Mindfulness & Health
    ("Meditation", "minutes", "🧠", "Meditation practice time"),
    ("Sleep", "hours", "😴", "Hours of sleep"),
    ("Water Intake", "glasses", "💧", "Glasses of water per day"),
    ("Stretching", "minutes", "🤸", "Stretching exercises"),
    
    # Learning & Development
    ("Reading", "pages", "📚", "Pages read from books"),
    ("Learning", "minutes", "🎓", "Time spent learning new skills"),
    ("Coding", "minutes", "💻", "Time spent coding"),
    ("Language Practice", "minutes", "🗣️", "Language learning practice"),
    ("Journaling", "entries", "📝", "Daily journal entries"),
    
    # Creative & Personal
    ("Drawing", "minutes", "🎨", "Drawing or sketching time"),
    ("Music Practice", "minutes", "🎵", "Musical instrument practice"),
    ("Writing", "words", "✍️", "Words written"),
    ("Photography", "photos", "📷", "Photos taken"),
    
    # Productivity & Organization
    ("Task Completion", "tasks", "✅", "Tasks completed"),
    ("Meetings", "count", "👥", "Meetings attended"),
    ("Calls", "minutes", "☎️", "Productive calls made"),
    ("Project Work", "hours", "🚀", "Hours on projects"),
    
    # Personal Care & Habits
    ("Cold Shower", "count", "🚿", "Cold showers taken"),
    ("Skincare", "minutes", "💆", "Skincare routine time"),
    ("Cooking", "meals", "🍳", "Meals cooked"),
    ("Cleaning", "minutes", "🧹", "Cleaning and tidying"),
]

def add_custom_habits(user_id):
    """Add sample habits for a user"""
    print(f"\n{'='*60}")
    print(f"Adding {len(SAMPLE_HABITS)} Custom Habits for User ID: {user_id}")
    print(f"{'='*60}\n")
    
    added = 0
    failed = 0
    
    for name, unit, icon, description in SAMPLE_HABITS:
        try:
            habit_id = database.create_user_habit(
                user_id=user_id,
                name=name,
                unit=unit,
                icon=icon,
                description=description,
                color="purple"
            )
            print(f"✓ Added: {icon} {name} ({unit})")
            added += 1
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                print(f"⚠ Skipped: {name} (already exists)")
            else:
                print(f"✗ Failed: {name} - {str(e)}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  ✓ Added: {added} habits")
    print(f"  ⚠ Skipped/Failed: {failed}")
    print(f"{'='*60}\n")
    
    return added, failed


def main():
    """Main entry point"""
    # Get all users
    try:
        conn = database.get_connection()
        users = conn.execute("SELECT id, username FROM users ORDER BY id").fetchall()
        conn.close()
        
        if not users:
            print("✗ No users found in database. Please create a user first.")
            sys.exit(1)
        
        print("\nAvailable Users:")
        for i, user in enumerate(users, 1):
            print(f"  {i}. {user['username']} (ID: {user['id']})")
        
        # Get user choice
        choice = input("\nSelect user number (or enter ID): ").strip()
        
        try:
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(users):
                    user_id = users[idx]['id']
                    username = users[idx]['username']
                else:
                    user_id = int(choice)
                    username = f"User {user_id}"
            else:
                print("✗ Invalid input")
                sys.exit(1)
        except ValueError:
            print("✗ Invalid user ID")
            sys.exit(1)
        
        print(f"\n✓ Selected: {username} (ID: {user_id})")
        
        # Add habits
        added, failed = add_custom_habits(user_id)
        
        if added > 0:
            print("✓ Custom habits added successfully!")
            print("\nYou can now:")
            print("  1. Log into the app")
            print("  2. Go to Habits Tracker")
            print("  3. See your new habits in the 'Your Habits' section")
            sys.exit(0)
        else:
            print("✗ No habits were added")
            sys.exit(1)
            
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
