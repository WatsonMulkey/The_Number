"""
Utility functions for The Number app.

Includes platform-aware console helpers and validation utilities.
"""

import os
import sys
import platform


def configure_console_encoding():
    """
    Configure console for UTF-8 output on Windows if possible.

    On Windows, attempts to set console code page to UTF-8 (65001).
    Falls back gracefully if this fails.
    """
    if platform.system() == 'Windows':
        try:
            # Try to set console to UTF-8 mode
            import ctypes
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        except Exception:
            # If it fails, we'll just use ASCII-safe output
            pass


def safe_print(text: str, fallback_char: str = '?') -> None:
    """
    Print text with encoding fallback for Windows compatibility.

    Args:
        text: Text to print (may contain Unicode)
        fallback_char: Character to use for unencodable characters
    """
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback for consoles that don't support Unicode
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)


def validate_database_access(db_path: str, encryption_key: str) -> tuple[bool, str]:
    """
    Validate that database can be accessed with given encryption key.

    Args:
        db_path: Path to database file
        encryption_key: Encryption key to test

    Returns:
        Tuple of (success: bool, error_message: str)
    """
    if not os.path.exists(db_path):
        return True, ""  # No database yet, will be created

    if not encryption_key:
        return False, "Database exists but no encryption key provided"

    try:
        from .database import EncryptedDatabase
        db = EncryptedDatabase(db_path=db_path, encryption_key=encryption_key)
        # Try to read a setting (will fail if key is wrong)
        db.get_setting("onboarded")
        return True, ""
    except Exception as e:
        error_msg = (
            f"Cannot access database: {str(e)}\n\n"
            "This usually means:\n"
            "  1. The database was created with a different encryption key\n"
            "  2. The database file is corrupted\n\n"
            "Solutions:\n"
            "  1. Delete the database file to start fresh (loses all data)\n"
            "  2. Restore the correct DB_ENCRYPTION_KEY in your .env file\n"
            f"\nDatabase location: {os.path.abspath(db_path)}"
        )
        return False, error_msg


def check_database_health() -> None:
    """
    Perform health check on database before app starts.

    Exits with error message if database is inaccessible.
    """
    db_path = "budget.db"
    encryption_key = os.getenv("DB_ENCRYPTION_KEY")

    success, error_msg = validate_database_access(db_path, encryption_key)

    if not success:
        print("\n" + "="*70)
        print("  DATABASE ERROR")
        print("="*70 + "\n")
        print(error_msg)
        print("\n" + "="*70 + "\n")
        sys.exit(1)


def ensure_env_file() -> None:
    """
    Ensure .env file exists with encryption key.

    Creates .env file with new encryption key if it doesn't exist.
    """
    from pathlib import Path

    env_path = Path(".env")

    if not env_path.exists():
        from cryptography.fernet import Fernet
        key = Fernet.generate_key().decode()

        with open(env_path, 'w') as f:
            f.write(f"# The Number - Environment Configuration\n")
            f.write(f"# Generated: {platform.node()} on {platform.system()}\n\n")
            f.write(f"# Database encryption key - KEEP THIS SECURE!\n")
            f.write(f"# If you lose this key, you cannot access your data.\n")
            f.write(f"DB_ENCRYPTION_KEY={key}\n")

        print("\n" + "="*70)
        print("  NEW ENCRYPTION KEY GENERATED")
        print("="*70)
        print(f"\n  Created new .env file with encryption key.")
        print(f"  Location: {env_path.absolute()}\n")
        print("  IMPORTANT: Keep this file secure and backed up!")
        print("  Without it, you cannot access your budget data.\n")
        print("="*70 + "\n")
