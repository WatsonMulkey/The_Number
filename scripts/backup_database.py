"""
Database backup script for The Number.

Creates timestamped backups of the SQLite database using SQLite's
backup API for safe hot backups (backups while the database is in use).
"""

import shutil
import sqlite3
import os
from datetime import datetime
from pathlib import Path
import sys


def backup_database(
    db_path: str = "api/budget.db",
    backup_dir: str = "backups/automatic"
) -> str:
    """
    Create a timestamped database backup.

    Uses SQLite's backup API which is safe for hot backups
    (backing up while the database is in use).

    Args:
        db_path: Path to the source database file
        backup_dir: Directory to store the backup

    Returns:
        Path to the created backup file

    Raises:
        FileNotFoundError: If source database doesn't exist
        PermissionError: If backup directory isn't writable
    """
    # Validate source database exists
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found: {db_path}")

    # Create backup directory if it doesn't exist
    backup_path_obj = Path(backup_dir)
    backup_path_obj.mkdir(parents=True, exist_ok=True)

    # Generate timestamped backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"budget_backup_{timestamp}.db"
    backup_path = backup_path_obj / backup_name

    print(f"Creating backup: {backup_path}")
    print(f"Source: {db_path}")

    # Use SQLite's backup API for safe hot backup
    try:
        src = sqlite3.connect(db_path)
        dst = sqlite3.connect(str(backup_path))

        with dst:
            src.backup(dst)

        src.close()
        dst.close()

        # Verify backup was created
        backup_size = os.path.getsize(backup_path)
        print(f"Backup created successfully: {backup_path}")
        print(f"Backup size: {backup_size:,} bytes")

        return str(backup_path)

    except sqlite3.Error as e:
        print(f"SQLite error during backup: {e}", file=sys.stderr)
        # Clean up failed backup
        if backup_path.exists():
            backup_path.unlink()
        raise


def cleanup_old_backups(backup_dir: str = "backups/automatic", keep_count: int = 10):
    """
    Remove old backups, keeping only the most recent ones.

    Args:
        backup_dir: Directory containing backups
        keep_count: Number of recent backups to keep (default: 10)
    """
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        print(f"Backup directory doesn't exist: {backup_dir}")
        return

    # Get all backup files sorted by modification time (newest first)
    backups = sorted(
        backup_path.glob("budget_backup_*.db"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    if len(backups) <= keep_count:
        print(f"Found {len(backups)} backups (keeping all, limit is {keep_count})")
        return

    # Delete old backups beyond the keep_count
    old_backups = backups[keep_count:]
    print(f"Cleaning up {len(old_backups)} old backups (keeping {keep_count} most recent)")

    for backup in old_backups:
        try:
            backup.unlink()
            print(f"  Deleted: {backup.name}")
        except OSError as e:
            print(f"  Failed to delete {backup.name}: {e}", file=sys.stderr)


def list_backups(backup_dir: str = "backups"):
    """
    List all available backups.

    Args:
        backup_dir: Root backup directory
    """
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        print(f"No backups found - directory doesn't exist: {backup_dir}")
        return

    # Find all backup files in manual and automatic directories
    all_backups = []
    for subdir in ["manual", "automatic"]:
        subdir_path = backup_path / subdir
        if subdir_path.exists():
            backups = list(subdir_path.glob("budget_backup_*.db"))
            all_backups.extend([(b, subdir) for b in backups])

    if not all_backups:
        print("No backups found")
        return

    # Sort by modification time (newest first)
    all_backups.sort(key=lambda x: x[0].stat().st_mtime, reverse=True)

    print(f"\nFound {len(all_backups)} backup(s):\n")
    print(f"{'Filename':<30} {'Type':<10} {'Size':>12} {'Created':<20}")
    print("=" * 75)

    for backup, backup_type in all_backups:
        stat = backup.stat()
        size = stat.st_size
        created = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

        # Format size in human-readable format
        if size < 1024:
            size_str = f"{size} B"
        elif size < 1024 * 1024:
            size_str = f"{size / 1024:.1f} KB"
        else:
            size_str = f"{size / (1024 * 1024):.1f} MB"

        print(f"{backup.name:<30} {backup_type:<10} {size_str:>12} {created:<20}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Backup The Number database")
    parser.add_argument(
        "--db-path",
        default="api/budget.db",
        help="Path to database file (default: api/budget.db)"
    )
    parser.add_argument(
        "--backup-dir",
        default="backups/automatic",
        help="Backup directory (default: backups/automatic)"
    )
    parser.add_argument(
        "--manual",
        action="store_true",
        help="Save to backups/manual instead of backups/automatic"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up old automatic backups (keeps 10 most recent)"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available backups"
    )

    args = parser.parse_args()

    try:
        if args.list:
            list_backups()
        else:
            # Determine backup directory
            if args.manual:
                backup_dir = "backups/manual"
            else:
                backup_dir = args.backup_dir

            # Create backup
            backup_path = backup_database(args.db_path, backup_dir)
            print(f"\nBackup complete: {backup_path}")

            # Cleanup old backups if requested (only for automatic)
            if args.cleanup and not args.manual:
                print()
                cleanup_old_backups(backup_dir)

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except PermissionError as e:
        print(f"Permission error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
