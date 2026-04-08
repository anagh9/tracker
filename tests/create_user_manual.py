"""
Script to manually create a user in the database.
Allows you to add username, email, and password interactively.

Usage: python scripts/create_user_manual.py
"""

import database
import sys
from pathlib import Path
from getpass import getpass
from werkzeug.security import generate_password_hash
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


DB_NAME = database.DB_NAME


def validate_username(username):
    """Validate username - not empty, no special chars"""
    if not username or len(username) < 3:
        return None, "Username must be at least 3 characters long."
    if not username.replace("_", "").replace("-", "").isalnum():
        return None, "Username can only contain letters, numbers, hyphens, and underscores."

    # Check if username already exists
    try:
        existing_user = database.get_user_by_username(username)
        if existing_user:
            return None, f"Username '{username}' already exists."
    except Exception:
        pass

    return username, None


def validate_email(email):
    """Validate email format"""
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        return None, "Please enter a valid email address."

    # Check if email already exists
    try:
        existing_user = database.get_user_by_email(email)
        if existing_user:
            return None, f"Email '{email}' is already registered."
    except Exception:
        pass

    return email, None


def validate_password(password):
    """Validate password - minimum length and complexity"""
    if not password or len(password) < 6:
        return None, "Password must be at least 6 characters long."

    return password, None


def get_username():
    """Prompt for and validate username"""
    while True:
        username = input("\nEnter username: ").strip()
        valid_username, error = validate_username(username)

        if valid_username:
            return valid_username
        else:
            print(f"✗ {error}")


def get_email():
    """Prompt for and validate email"""
    while True:
        email = input("Enter email: ").strip()
        valid_email, error = validate_email(email)

        if valid_email:
            return valid_email
        else:
            print(f"✗ {error}")


def get_password():
    """Prompt for and validate password"""
    while True:
        password = getpass("Enter password (will not be displayed): ")
        valid_password, error = validate_password(password)

        if valid_password:
            # Ask for confirmation
            confirm_password = getpass("Confirm password: ")
            if password == confirm_password:
                return password
            else:
                print("✗ Passwords do not match. Please try again.")
        else:
            print(f"✗ {error}")


def list_existing_users():
    """Display all existing users"""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, username, email, created_at FROM users ORDER BY id")
        users = cursor.fetchall()
        conn.close()

        if users:
            print("\n" + "=" * 70)
            print("EXISTING USERS")
            print("=" * 70)
            for user in users:
                print(
                    f"ID: {user['id']:3d} | Username: {user['username']:20s} | Email: {user['email']}")
            print("=" * 70 + "\n")
        else:
            print("\nNo users found in database yet.\n")
    except Exception as e:
        print(f"Error listing users: {e}\n")


def create_user():
    """Main function to create a user"""
    print("\n" + "=" * 70)
    print("CREATE NEW USER")
    print("=" * 70)

    # Show existing users
    list_existing_users()

    # Get user input
    username = get_username()
    email = get_email()
    password = get_password()

    # Hash password
    password_hash = generate_password_hash(password)

    # Create user in database
    try:
        user_id = database.create_user(username, email, password_hash)

        if user_id:
            print("\n" + "=" * 70)
            print("✓ USER CREATED SUCCESSFULLY!")
            print("=" * 70)
            print(f"User ID:   {user_id}")
            print(f"Username:  {username}")
            print(f"Email:     {email}")
            print("=" * 70 + "\n")
        else:
            print("\n✗ Failed to create user. Username or email may already exist.")
    except sqlite3.IntegrityError as e:
        print(f"\n✗ Database error: {e}")
        print("  Make sure the username and email are unique.")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


def main():
    """Entry point"""
    try:
        # Initialize database if needed
        database.init_db()

        # Create user
        create_user()

        # Ask if user wants to create another
        while True:
            response = input("Create another user? (y/n): ").strip().lower()
            if response == "y":
                create_user()
            elif response == "n":
                print("\nGoodbye!")
                break
            else:
                print("Please enter 'y' or 'n'.")

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
