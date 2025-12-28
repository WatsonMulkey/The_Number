#!/usr/bin/env python3
"""
Password Reset CLI Script for The Number Budget App

This script allows administrators to reset user passwords from the command line.
It's useful for emergency password resets or initial user setup.

Usage:
    python reset_password.py

Interactive mode will prompt you for username and password.

Requirements:
    pip install passlib[bcrypt] python-dotenv cryptography
"""

import getpass
import os
import secrets
import string
import sqlite3
import sys
from pathlib import Path

try:
    from passlib.context import CryptContext
except ImportError:
    print("❌ Error: passlib not installed")
    print("   Install it with: pip install passlib[bcrypt]")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ Error: python-dotenv not installed")
    print("   Install it with: pip install python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Initialize bcrypt password context (MUST match api/auth.py)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    This matches the password hashing used in the API.

    Args:
        password: The plain text password to hash

    Returns:
        The bcrypt hash of the password
    """
    return pwd_context.hash(password)


def generate_random_password(length: int = 16) -> str:
    """
    Generate a secure random password.

    Args:
        length: Length of the password (default: 16)

    Returns:
        A random password containing uppercase, lowercase, digits, and special characters
    """
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*"

    # Ensure at least one character from each set
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]

    # Fill the rest with random characters from all sets
    all_chars = lowercase + uppercase + digits + special
    password.extend(secrets.choice(all_chars) for _ in range(length - 4))

    # Shuffle to avoid predictable patterns
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)

    return ''.join(password_list)


def reset_user_password(username: str, new_password: str) -> bool:
    """
    Reset a user's password in the database.

    Args:
        username: The username of the account to reset
        new_password: The new password (will be hashed before storage)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get database path from environment or use default
        db_path = os.getenv("DB_PATH", "api/budget.db")

        # Check if database exists
        if not Path(db_path).exists():
            print(f"❌ Error: Database not found at {db_path}")
            print(f"   Set DB_PATH in .env file if using a different location")
            return False

        # Hash the new password using bcrypt
        hashed_password = hash_password(new_password)
        print(f"   Password hash starts with: {hashed_password[:15]}...")

        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT id, username FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            print(f"❌ Error: User '{username}' not found in database")
            print(f"\nAvailable users:")
            cursor.execute("SELECT username FROM users")
            for row in cursor.fetchall():
                print(f"   - {row[0]}")
            conn.close()
            return False

        user_id, db_username = user

        # Update password (column name is 'hashed_password' not 'password_hash')
        cursor.execute(
            "UPDATE users SET hashed_password = ? WHERE id = ?",
            (hashed_password, user_id)
        )
        conn.commit()

        # Verify update
        cursor.execute("SELECT hashed_password FROM users WHERE id = ?", (user_id,))
        updated_hash = cursor.fetchone()[0]

        conn.close()

        if updated_hash == hashed_password:
            print(f"   ✓ Database updated successfully")
            return True
        else:
            print(f"   ❌ Database update verification failed")
            return False

    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main entry point for the password reset script."""
    print("=" * 50)
    print("Password Reset Tool - The Number")
    print("=" * 50)
    print()

    # Get username
    username = input("Enter username: ").strip()
    if not username:
        print("❌ Error: Username cannot be empty")
        sys.exit(1)

    # Get password (use getpass for security)
    print("\nEnter new password (hidden for security)")
    print("Requirements: 8+ chars, uppercase, lowercase, number")
    new_password = getpass.getpass("New password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if new_password != confirm_password:
        print("❌ Error: Passwords do not match")
        sys.exit(1)

    # Validate password requirements
    print("\nValidating password...")
    if len(new_password) < 8:
        print("❌ Error: Password must be at least 8 characters long")
        sys.exit(1)

    if not any(c.isupper() for c in new_password):
        print("❌ Error: Password must contain at least one uppercase letter")
        sys.exit(1)

    if not any(c.islower() for c in new_password):
        print("❌ Error: Password must contain at least one lowercase letter")
        sys.exit(1)

    if not any(c.isdigit() for c in new_password):
        print("❌ Error: Password must contain at least one digit")
        sys.exit(1)

    print("✓ Password meets requirements")

    # Reset password
    print(f"\nUpdating password for user: {username}...")
    if reset_user_password(username, new_password):
        print(f"\n{'='*50}")
        print("✅ Password updated successfully!")
        print(f"{'='*50}")
        print(f"\nThe user can now log in with:")
        print(f"  Username: {username}")
        print(f"  Password: (the password you just entered)")
        print(f"\nRemember to:")
        print(f"  1. Notify the user securely")
        print(f"  2. Recommend they change their password immediately")
        print(f"{'='*50}")
    else:
        print(f"\n❌ Password reset failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
