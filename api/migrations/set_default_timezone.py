#!/usr/bin/env python3
"""
One-time migration script to set default timezone for existing users.

Run this after deploying the timezone-aware update to ensure existing users
have a timezone set for correct day boundary calculations.

Usage:
    python -m api.migrations.set_default_timezone
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.database import EncryptedDatabase

DEFAULT_TIMEZONE = "America/Denver"  # MST


def get_production_db() -> EncryptedDatabase:
    """Get database instance using production configuration."""
    encryption_key = os.getenv("DB_ENCRYPTION_KEY")
    if not encryption_key:
        raise RuntimeError(
            "DB_ENCRYPTION_KEY environment variable not set. "
            "Run this script in the production environment."
        )

    # Use the same path logic as api/main.py
    fly_data_path = Path("/data/budget.db")
    if fly_data_path.parent.exists():
        db_path = str(fly_data_path)
    else:
        db_path = str(Path(__file__).parent.parent / "budget.db")

    return EncryptedDatabase(db_path=db_path, encryption_key=encryption_key)


def migrate():
    """Set default timezone for all users who don't have one."""
    db = get_production_db()

    # Get all users
    import sqlite3
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()

        # Get all user IDs
        cursor.execute("SELECT id, username FROM users")
        users = cursor.fetchall()

        updated_count = 0
        for user_id, username in users:
            # Check if user already has a timezone set
            existing_tz = db.get_setting("user_timezone", user_id)

            if not existing_tz:
                db.set_setting("user_timezone", DEFAULT_TIMEZONE, user_id)
                print(f"Set timezone to {DEFAULT_TIMEZONE} for user: {username} (id={user_id})")
                updated_count += 1
            else:
                print(f"User {username} already has timezone: {existing_tz}")

        print(f"\nMigration complete. Updated {updated_count} user(s).")


if __name__ == "__main__":
    migrate()
