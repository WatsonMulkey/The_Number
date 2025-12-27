"""
Database restore script for The Number.

Restores a database from a backup file, with safety measures:
- Creates a backup of current database before restoring
- Verifies backup file integrity
- Provides confirmation prompts
"""

import shutil
import sqlite3
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def list_available_backups(backup_root: str = "backups") -> list[tuple[Path, str]]:
    """
    List all available backup files.

    Args:
        backup_root: Root directory containing backups

    Returns:
        List of tuples: (backup_path, backup_type)
    """
    backup_path = Path(backup_root)
    if not backup_path.exists():
        return []

    all_backups = []

    # Scan both manual and automatic directories
    for subdir in ["manual", "automatic"]:
        subdir_path = backup_path / subdir
        if subdir_path.exists():
            for backup in subdir_path.glob("budget_backup_*.db"):
                all_backups.append((backup, subdir))

    # Sort by modification time (newest first)
    all_backups.sort(key=lambda x: x[0].stat().st_mtime, reverse=True)

    return all_backups


def verify_backup_integrity(backup_path: Path) -> bool:
    """
    Verify that a backup file is a valid SQLite database.

    Args:
        backup_path: Path to the backup file

    Returns:
        True if the backup is valid, False otherwise
    """
    try:
        conn = sqlite3.connect(str(backup_path))
        cursor = conn.cursor()

        # Try to query the database to verify it's valid
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        conn.close()

        # Ensure we have at least some tables
        return len(tables) > 0
    except sqlite3.Error as e:
        print(f"Backup verification failed: {e}", file=sys.stderr)
        return False


def backup_current_database(
    db_path: str = "api/budget.db",
    backup_dir: str = "backups/pre-restore"
) -> Optional[str]:
    """
    Create a backup of the current database before restoring.

    Args:
        db_path: Path to current database
        backup_dir: Directory for pre-restore backup

    Returns:
        Path to the backup file, or None if failed
    """
    # Import backup function from backup_database script
    # We need to add parent directory to path if not already there
    parent_dir = str(Path(__file__).parent.parent)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)

    from scripts.backup_database import backup_database

    try:
        print(f"Creating backup of current database before restore...")
        backup_path = backup_database(db_path, backup_dir)
        print(f"Pre-restore backup saved: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Failed to create pre-restore backup: {e}", file=sys.stderr)
        return None


def restore_database(
    backup_path: Path,
    db_path: str = "api/budget.db",
    create_pre_restore_backup: bool = True
) -> bool:
    """
    Restore database from a backup file.

    Args:
        backup_path: Path to the backup file to restore
        db_path: Path to the target database file
        create_pre_restore_backup: Whether to backup current DB first

    Returns:
        True if restore succeeded, False otherwise
    """
    try:
        # Verify backup integrity first
        print(f"\nVerifying backup integrity...")
        if not verify_backup_integrity(backup_path):
            print("ERROR: Backup file is corrupted or invalid", file=sys.stderr)
            return False

        print("Backup file verified successfully")

        # Create pre-restore backup if requested
        if create_pre_restore_backup and os.path.exists(db_path):
            pre_restore_backup = backup_current_database(db_path)
            if pre_restore_backup is None:
                print("ERROR: Failed to create pre-restore backup", file=sys.stderr)
                print("Aborting restore for safety", file=sys.stderr)
                return False

        # Perform the restore
        print(f"\nRestoring database from: {backup_path}")
        print(f"Target: {db_path}")

        # Use SQLite's backup API for safe restoration
        src = sqlite3.connect(str(backup_path))
        dst = sqlite3.connect(db_path)

        with dst:
            src.backup(dst)

        src.close()
        dst.close()

        # Verify the restored database
        db_path_obj = Path(db_path)
        restored_size = db_path_obj.stat().st_size

        print(f"\nRestore complete!")
        print(f"Restored database size: {restored_size:,} bytes")

        return True

    except Exception as e:
        print(f"ERROR during restore: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def interactive_restore():
    """
    Interactive restore process with user prompts.
    """
    print("=" * 60)
    print("DATABASE RESTORE UTILITY")
    print("=" * 60)
    print()

    # List available backups
    backups = list_available_backups()

    if not backups:
        print("No backups found.")
        print("Backup directories checked:")
        print("  - backups/manual/")
        print("  - backups/automatic/")
        return

    # Display backups
    print(f"Found {len(backups)} backup(s):\n")
    print(f"{'#':<4} {'Filename':<35} {'Type':<10} {'Size':<12} {'Created':<20}")
    print("-" * 85)

    for idx, (backup, backup_type) in enumerate(backups, 1):
        stat = backup.stat()
        size = stat.st_size
        created = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        # Format size
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"

        print(f"{idx:<4} {backup.name:<35} {backup_type:<10} {size_str:<12} {created:<20}")

    # Get user selection
    print()
    try:
        selection = input("Enter backup number to restore (or 'q' to quit): ").strip()

        if selection.lower() == 'q':
            print("Restore cancelled")
            return

        backup_idx = int(selection) - 1
        if backup_idx < 0 or backup_idx >= len(backups):
            print("Invalid selection")
            return

        selected_backup, backup_type = backups[backup_idx]

        # Confirmation
        print()
        print("=" * 60)
        print("WARNING: This will replace your current database!")
        print("=" * 60)
        print(f"Selected backup: {selected_backup.name}")
        print(f"Type: {backup_type}")
        print(f"Created: {datetime.fromtimestamp(selected_backup.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("A backup of your current database will be created first")
        print("at: backups/pre-restore/")
        print()

        confirm = input("Type 'YES' to confirm restore: ").strip()

        if confirm != "YES":
            print("Restore cancelled")
            return

        # Perform restore
        print()
        success = restore_database(selected_backup)

        if success:
            print()
            print("=" * 60)
            print("RESTORE SUCCESSFUL!")
            print("=" * 60)
            print()
            print("Your database has been restored from the backup.")
            print("Please restart the API server if it's running.")
        else:
            print()
            print("=" * 60)
            print("RESTORE FAILED")
            print("=" * 60)
            print()
            print("Please check the error messages above.")
            print("Your original database should be intact.")

    except ValueError:
        print("Invalid input")
    except KeyboardInterrupt:
        print("\nRestore cancelled")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Restore The Number database from backup")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available backups and exit"
    )
    parser.add_argument(
        "--backup-file",
        type=str,
        help="Path to backup file to restore"
    )
    parser.add_argument(
        "--db-path",
        default="api/budget.db",
        help="Path to database file (default: api/budget.db)"
    )
    parser.add_argument(
        "--no-pre-backup",
        action="store_true",
        help="Skip creating pre-restore backup (dangerous!)"
    )

    args = parser.parse_args()

    try:
        if args.list:
            # Just list backups
            backups = list_available_backups()
            if not backups:
                print("No backups found")
                sys.exit(0)

            print(f"Found {len(backups)} backup(s):\n")
            print(f"{'Filename':<35} {'Type':<10} {'Size':<12} {'Created':<20}")
            print("-" * 80)

            for backup, backup_type in backups:
                stat = backup.stat()
                size = stat.st_size
                created = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size / 1024:.1f} KB"
                else:
                    size_str = f"{size / (1024 * 1024):.1f} MB"

                print(f"{backup.name:<35} {backup_type:<10} {size_str:<12} {created:<20}")

        elif args.backup_file:
            # Restore from specified backup file
            backup_path = Path(args.backup_file)
            if not backup_path.exists():
                print(f"ERROR: Backup file not found: {args.backup_file}", file=sys.stderr)
                sys.exit(1)

            success = restore_database(
                backup_path,
                args.db_path,
                create_pre_restore_backup=not args.no_pre_backup
            )
            sys.exit(0 if success else 1)

        else:
            # Interactive mode
            interactive_restore()

    except KeyboardInterrupt:
        print("\nOperation cancelled")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
