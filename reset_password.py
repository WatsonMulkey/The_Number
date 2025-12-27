#!/usr/bin/env python3
"""
Password Reset CLI Script for The Number Budget App

This script allows administrators to reset user passwords from the command line.
It's useful for emergency password resets or initial user setup.

Usage:
    python reset_password.py <username> [--password <new_password>]

Examples:
    # Reset password with a specific password
    python reset_password.py john_doe --password NewSecurePass123

    # Generate a random password
    python reset_password.py john_doe
"""

import argparse
import hashlib
import secrets
import string
import sqlite3
import sys
from pathlib import Path


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256.
    This matches the password hashing used in the API.

    Args:
        password: The plain text password to hash

    Returns:
        The hexadecimal hash of the password
    """
    return hashlib.sha256(password.encode()).hexdigest()


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


def reset_user_password(username: str, new_password: str, db_path: str = "budget.db") -> bool:
    """
    Reset a user's password in the database.

    Args:
        username: The username of the account to reset
        new_password: The new password (will be hashed before storage)
        db_path: Path to the SQLite database file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if database exists
        if not Path(db_path).exists():
            print(f"❌ Error: Database not found at {db_path}")
            return False

        # Hash the new password
        hashed_password = hash_password(new_password)

        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check if user exists
        cursor.execute("SELECT id, username FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            print(f"❌ Error: User '{username}' not found in database")
            conn.close()
            return False

        user_id, db_username = user

        # Update password
        cursor.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (hashed_password, user_id)
        )
        conn.commit()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return False


def main():
    """Main entry point for the password reset script."""
    parser = argparse.ArgumentParser(
        description="Reset user password for The Number Budget App",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Reset password with a specific password
  python reset_password.py john_doe --password NewSecurePass123

  # Generate a random password
  python reset_password.py john_doe

  # Use custom database path
  python reset_password.py john_doe --db /path/to/budget.db
        """
    )

    parser.add_argument(
        "username",
        help="Username of the account to reset"
    )

    parser.add_argument(
        "-p", "--password",
        help="New password (if not provided, a random password will be generated)",
        default=None
    )

    parser.add_argument(
        "-d", "--db",
        help="Path to the database file (default: budget.db)",
        default="budget.db"
    )

    args = parser.parse_args()

    # Generate or use provided password
    if args.password:
        new_password = args.password
        password_generated = False
    else:
        new_password = generate_random_password()
        password_generated = True

    # Validate password requirements
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

    # Confirm reset
    print(f"\n🔐 Password Reset for user: {args.username}")
    print(f"   Database: {args.db}")

    if password_generated:
        print(f"   Generated password: {new_password}")

    confirm = input("\nProceed with password reset? (yes/no): ")

    if confirm.lower() not in ['yes', 'y']:
        print("❌ Password reset cancelled")
        sys.exit(0)

    # Reset password
    if reset_user_password(args.username, new_password, args.db):
        print(f"\n✅ Password reset successful for user: {args.username}")
        if password_generated:
            print(f"\n⚠️  IMPORTANT: Save this generated password securely:")
            print(f"   {new_password}")
            print("\n   This password will NOT be displayed again!")
    else:
        print(f"\n❌ Password reset failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
