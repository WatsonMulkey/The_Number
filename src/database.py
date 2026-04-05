"""
Encrypted local database layer for The Number app.

Uses SQLite with encryption for storing user data, expenses, and transactions.
All sensitive data is encrypted at rest using Fernet symmetric encryption.
"""

import sqlite3
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Optional, Any
from zoneinfo import ZoneInfo
from cryptography.fernet import Fernet
from pathlib import Path


class EncryptedDatabase:
    """Manages encrypted local SQLite database for budget data."""

    def __init__(self, db_path: str = "budget.db", encryption_key: Optional[str] = None):
        """
        Initialize encrypted database.

        Args:
            db_path: Path to SQLite database file
            encryption_key: Encryption key (base64 encoded). If None, generates new key.
        """
        self.db_path = db_path

        # Initialize encryption
        if encryption_key:
            self.cipher = Fernet(encryption_key.encode())
        else:
            # Generate new key if none provided
            key = Fernet.generate_key()
            self.cipher = Fernet(key)
            self._save_key_warning(key)

        # Initialize database
        self._init_database()

    def _save_key_warning(self, key: bytes) -> None:
        """Warn user to save their encryption key."""
        key_str = key.decode()
        # Mask key for security (show first/last 4 chars only)
        masked_key = f"{key_str[:4]}...{key_str[-4:]}"

        print("\n" + "="*60)
        print("IMPORTANT: Save this encryption key securely!")
        print("You will need it to access your data.")
        print("="*60)
        print(f"\nEncryption Key (masked): {masked_key}")
        print("\nFull key saved to: .env file")
        print("\nWARNING: Without this key, you cannot access your data!")
        print("Keep the .env file secure and backed up!")
        print("="*60 + "\n")

    def _init_database(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Enable WAL mode for better concurrent read/write performance
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=5000")

            # Schema version tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY,
                    applied_at TEXT NOT NULL,
                    description TEXT
                )
            """)

            # Users table - must be created first for foreign keys
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            # User settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, key)
                )
            """)

            # Expenses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    is_fixed INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

            # Password reset tokens (persistent across restarts)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reset_tokens (
                    token TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
            """)

            # Migration: Add user_id to existing tables if they don't have it
            self._migrate_add_user_id(cursor)

            # Run versioned migrations
            self._run_migrations(cursor)

            conn.commit()

    def _run_migrations(self, cursor) -> None:
        """Run versioned migrations in order, tracking which have been applied."""
        migrations = [
            (1, "Add indexes for query performance", self._migration_001_add_indexes),
            (2, "Clean up expired reset tokens", self._migration_002_cleanup_tokens),
            (3, "Add user_activity table for engagement metrics", self._migration_003_add_user_activity),
            (4, "Add frequency column to expenses", self._migration_004_add_expense_frequency),
        ]

        for version, description, migrate_fn in migrations:
            cursor.execute("SELECT 1 FROM schema_version WHERE version = ?", (version,))
            if cursor.fetchone() is None:
                migrate_fn(cursor)
                cursor.execute(
                    "INSERT INTO schema_version (version, applied_at, description) VALUES (?, ?, ?)",
                    (version, datetime.now(ZoneInfo("UTC")).isoformat(), description)
                )

    @staticmethod
    def _migration_001_add_indexes(cursor) -> None:
        """Add indexes for common query patterns."""
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_expenses_user_id ON expenses(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_settings_user_key ON settings(user_id, key)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(user_id, date)")

    @staticmethod
    def _migration_002_cleanup_tokens(cursor) -> None:
        """Clean up any expired reset tokens on startup."""
        cursor.execute("DELETE FROM reset_tokens WHERE datetime(expires_at) < datetime('now')")

    @staticmethod
    def _migration_003_add_user_activity(cursor) -> None:
        """Add user_activity table for engagement metrics (DAU/WAU/MAU)."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_activity (
                user_id INTEGER NOT NULL,
                activity_date TEXT NOT NULL,
                login_count INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (user_id, activity_date),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_activity_date ON user_activity(activity_date)")

    @staticmethod
    def _migration_004_add_expense_frequency(cursor) -> None:
        """Add frequency column to expenses table (weekly/monthly)."""
        cursor.execute("ALTER TABLE expenses ADD COLUMN frequency TEXT NOT NULL DEFAULT 'monthly'")

    def _migrate_add_user_id(self, cursor) -> None:
        """Add user_id column to existing tables that don't have it."""
        # Check and add user_id to settings
        cursor.execute("PRAGMA table_info(settings)")
        settings_cols = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in settings_cols:
            # Add column (SQLite doesn't support adding foreign keys to existing tables easily)
            cursor.execute("ALTER TABLE settings ADD COLUMN user_id INTEGER")
            # Set default user_id to 1 for existing data (if any users exist)
            cursor.execute("UPDATE settings SET user_id = 1 WHERE user_id IS NULL")

        # Check and add user_id to expenses
        cursor.execute("PRAGMA table_info(expenses)")
        expenses_cols = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in expenses_cols:
            cursor.execute("ALTER TABLE expenses ADD COLUMN user_id INTEGER")
            cursor.execute("UPDATE expenses SET user_id = 1 WHERE user_id IS NULL")

        # Check and add user_id to transactions
        cursor.execute("PRAGMA table_info(transactions)")
        transactions_cols = [col[1] for col in cursor.fetchall()]
        if 'user_id' not in transactions_cols:
            cursor.execute("ALTER TABLE transactions ADD COLUMN user_id INTEGER")
            cursor.execute("UPDATE transactions SET user_id = 1 WHERE user_id IS NULL")

    def _encrypt(self, data: str) -> str:
        """Encrypt a string."""
        return self.cipher.encrypt(data.encode()).decode()

    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    @staticmethod
    def _sanitize_text(text: str) -> str:
        """
        Sanitize text input to prevent XSS and injection attacks.

        Args:
            text: Text to sanitize

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Remove any HTML/XML tags
        sanitized = re.sub(r'<[^>]*>', '', text)

        # Remove script-like patterns
        sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
        sanitized = re.sub(r'on\w+\s*=', '', sanitized, flags=re.IGNORECASE)

        # Remove null bytes (SQL injection prevention)
        sanitized = sanitized.replace('\x00', '')

        return sanitized.strip()

    # Settings operations
    def set_setting(self, key: str, value: Any, user_id: int) -> None:
        """
        Store an encrypted setting for a specific user.

        Args:
            key: Setting key (not encrypted)
            value: Setting value (will be encrypted)
            user_id: User ID this setting belongs to
        """
        encrypted_value = self._encrypt(json.dumps(value))
        now = datetime.now(ZoneInfo("UTC")).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (user_id, key, value, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id, key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
            """, (user_id, key, encrypted_value, now, now))
            conn.commit()

    def get_setting(self, key: str, user_id: int, default: Any = None) -> Any:
        """
        Retrieve and decrypt a setting for a specific user.

        Args:
            key: Setting key
            user_id: User ID to fetch setting for
            default: Default value if setting doesn't exist

        Returns:
            Decrypted setting value or default
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ? AND user_id = ?", (key, user_id))
            row = cursor.fetchone()

            if row:
                decrypted = self._decrypt(row[0])
                return json.loads(decrypted)
            return default

    # Expense operations
    def add_expense(self, name: str, amount: float, user_id: int, is_fixed: bool = True,
                    frequency: str = "monthly") -> int:
        """
        Add an expense to the database for a specific user.

        Args:
            name: Expense name
            amount: Expense amount
            user_id: User ID this expense belongs to
            is_fixed: Whether this is a fixed monthly expense
            frequency: 'weekly' or 'monthly'

        Returns:
            ID of created expense
        """
        # Sanitize and validate expense data
        name = self._sanitize_text(name)

        if amount < 0:
            raise ValueError("Expense amount cannot be negative")
        if amount > 10_000_000:
            raise ValueError("Amount exceeds maximum ($10,000,000)")
        if not name:
            raise ValueError("Expense name is required")
        if len(name) > 200:
            raise ValueError("Expense name too long (max 200 characters)")
        if frequency not in ("weekly", "monthly"):
            raise ValueError("Frequency must be 'weekly' or 'monthly'")

        now = datetime.now(ZoneInfo("UTC")).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO expenses (user_id, name, amount, is_fixed, frequency, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, name, amount, 1 if is_fixed else 0, frequency, now, now))
            conn.commit()
            return cursor.lastrowid

    def get_expenses(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get all expenses for a specific user.

        Args:
            user_id: User ID to fetch expenses for

        Returns:
            List of expense dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
            rows = cursor.fetchall()

            return [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "amount": row["amount"],
                    "is_fixed": bool(row["is_fixed"]),
                    "frequency": row["frequency"] if "frequency" in row.keys() else "monthly",
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                }
                for row in rows
            ]

    def get_expense_by_id(self, expense_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a single expense by ID for a specific user.

        Args:
            expense_id: The expense ID to retrieve
            user_id: User ID (for access control)

        Returns:
            Expense dictionary or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "id": row["id"],
                "name": row["name"],
                "amount": row["amount"],
                "is_fixed": bool(row["is_fixed"]),
                "frequency": row["frequency"] if "frequency" in row.keys() else "monthly",
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }

    def update_expense(self, expense_id: int, user_id: int, name: Optional[str] = None,
                      amount: Optional[float] = None, is_fixed: Optional[bool] = None,
                      frequency: Optional[str] = None) -> None:
        """Update an expense for a specific user."""
        # Whitelist of allowed columns (security: prevent SQL injection pattern)
        ALLOWED_COLUMNS = {'name', 'amount', 'is_fixed', 'frequency', 'updated_at'}

        updates = []
        params = []

        if name is not None:
            if len(name) > 200:
                raise ValueError("Expense name too long (max 200 characters)")
            updates.append("name = ?")
            params.append(name.strip())
        if amount is not None:
            if amount < 0:
                raise ValueError("Amount cannot be negative")
            if amount > 10_000_000:
                raise ValueError("Amount exceeds maximum ($10,000,000)")
            updates.append("amount = ?")
            params.append(amount)
        if is_fixed is not None:
            updates.append("is_fixed = ?")
            params.append(1 if is_fixed else 0)
        if frequency is not None:
            if frequency not in ("weekly", "monthly"):
                raise ValueError("Frequency must be 'weekly' or 'monthly'")
            updates.append("frequency = ?")
            params.append(frequency)

        if not updates:
            return

        updates.append("updated_at = ?")
        params.append(datetime.now(ZoneInfo("UTC")).isoformat())
        params.append(expense_id)
        params.append(user_id)

        # Validate all update columns are in whitelist (prevent SQL injection)
        update_cols = {u.split('=')[0].strip() for u in updates}
        if not update_cols.issubset(ALLOWED_COLUMNS):
            raise ValueError("Invalid column names in update")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE expenses SET {', '.join(updates)} WHERE id = ? AND user_id = ?",
                params
            )
            conn.commit()

    def delete_expense(self, expense_id: int, user_id: int) -> None:
        """Delete an expense for a specific user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
            conn.commit()

    # Transaction operations
    def add_transaction(self, amount: float, description: str, user_id: int,
                       date: Optional[datetime] = None, category: Optional[str] = None) -> int:
        """
        Record a spending transaction for a specific user.

        Args:
            amount: Transaction amount
            description: Transaction description
            user_id: User ID this transaction belongs to
            date: Transaction date (defaults to now)
            category: Optional category

        Returns:
            ID of created transaction
        """
        # Sanitize and validate transaction data
        description = self._sanitize_text(description)
        if category:
            category = self._sanitize_text(category)

        if amount <= 0:
            raise ValueError("Transaction amount must be positive")
        if amount > 10_000_000:
            raise ValueError("Amount exceeds maximum ($10,000,000)")
        if not description:
            raise ValueError("Transaction description is required")
        if len(description) > 200:
            raise ValueError("Description too long (max 200 characters)")

        if date is None:
            date = datetime.now(ZoneInfo("UTC"))

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (user_id, date, amount, description, category, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, date.isoformat(), amount, description, category, datetime.now(ZoneInfo("UTC")).isoformat()))
            conn.commit()
            return cursor.lastrowid

    def get_transactions(self, user_id: int, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get transactions for a specific user, optionally filtered by date range.

        Args:
            user_id: User ID to fetch transactions for
            start_date: Filter transactions after this date
            end_date: Filter transactions before this date
            limit: Maximum number of transactions to return

        Returns:
            List of transaction dictionaries
        """
        query = "SELECT * FROM transactions WHERE user_id = ?"
        params = [user_id]

        if start_date:
            query += " AND date >= ?"
            params.append(start_date.isoformat())
        if end_date:
            query += " AND date <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY date DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [
                {
                    "id": row["id"],
                    "date": row["date"],
                    "amount": row["amount"],
                    "description": row["description"],
                    "category": row["category"],
                    "created_at": row["created_at"]
                }
                for row in rows
            ]

    def delete_transaction(self, transaction_id: int, user_id: int) -> None:
        """Delete a transaction for a specific user."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user_id))
            conn.commit()

    def get_total_spending_today(self, user_id: int, user_timezone: str | None = None) -> float:
        """
        Get NET spending for today for a specific user, using their timezone.

        Calculates: total expenses - total income for today.
        This means "Money In" transactions offset spending.

        Args:
            user_id: The user's ID
            user_timezone: User's timezone string (e.g., "America/Denver").
                          If None, uses default (America/Denver for MST).

        Returns:
            Net spending amount (can be negative if income > expenses)

        Note:
            Uses timezone-aware day boundaries to correctly identify "today"
            regardless of server timezone. Transactions are stored in UTC
            and queried using the user's local day boundaries converted to UTC.
        """
        # Import here to avoid circular imports
        from api.utils.dates import get_user_day_boundaries_utc

        start_utc, end_utc = get_user_day_boundaries_utc(user_timezone)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Calculate net spending: expenses add, income subtracts
            # Query using UTC boundaries that correspond to user's local "today"
            cursor.execute("""
                SELECT COALESCE(SUM(
                    CASE WHEN category = 'income' THEN -amount ELSE amount END
                ), 0) as net_spending
                FROM transactions
                WHERE user_id = ?
                  AND datetime(date) >= datetime(?)
                  AND datetime(date) <= datetime(?)
            """, (user_id, start_utc.isoformat(), end_utc.isoformat()))
            result = cursor.fetchone()
            return result[0] if result[0] else 0.0

    def get_transactions_sum_for_period(self, user_id: int, start_date: datetime, end_date: datetime) -> float:
        """
        Get total NET spending for a date range for a specific user.

        Calculates: total expenses - total income for the period.
        This means "Money In" transactions offset spending.

        Args:
            user_id: The user's ID
            start_date: Start of period (inclusive)
            end_date: End of period (exclusive)

        Returns:
            Net spending amount (can be negative if income > expenses)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(
                    CASE WHEN category = 'income' THEN -amount ELSE amount END
                ), 0) as net_spending
                FROM transactions
                WHERE user_id = ?
                  AND datetime(date) >= datetime(?)
                  AND datetime(date) < datetime(?)
            """, (user_id, start_date.isoformat(), end_date.isoformat()))
            result = cursor.fetchone()
            return result[0] if result[0] else 0.0

    # ========================================================================
    # USER MANAGEMENT
    # ========================================================================

    def create_user(self, username: str, password_hash: str, email: Optional[str] = None) -> int:
        """
        Create a new user.

        Args:
            username: Unique username
            password_hash: Hashed password
            email: Optional email address

        Returns:
            User ID of created user

        Raises:
            ValueError: If username already exists or invalid input
        """
        # Sanitize inputs
        username = self._sanitize_text(username)
        if email:
            email = self._sanitize_text(email)

        # Validate username
        if not username or len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(username) > 50:
            raise ValueError("Username too long (max 50 characters)")

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now(ZoneInfo("UTC")).isoformat()

            try:
                cursor.execute("""
                    INSERT INTO users (username, password_hash, email, created_at)
                    VALUES (?, ?, ?, ?)
                """, (username, password_hash, email, now))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                raise ValueError(f"Username '{username}' already exists")

    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Get user by username.

        Args:
            username: Username to look up

        Returns:
            User dict or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, password_hash, email, created_at
                FROM users
                WHERE username = ?
            """, (username,))
            row = cursor.fetchone()

            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "password_hash": row[2],
                    "email": row[3],
                    "created_at": row[4]
                }
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user by ID.

        Args:
            user_id: User ID to look up

        Returns:
            User dict or None if not found
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, password_hash, email, created_at
                FROM users
                WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()

            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "password_hash": row[2],
                    "email": row[3],
                    "created_at": row[4]
                }
            return None

    def update_user_password(self, user_id: int, new_password_hash: str) -> None:
        """
        Update a user's password.

        Args:
            user_id: ID of the user
            new_password_hash: New password hash

        Raises:
            ValueError: If user doesn't exist
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Verify user exists
            cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
            if not cursor.fetchone():
                raise ValueError(f"User with ID {user_id} not found")

            # Update password
            cursor.execute("""
                UPDATE users
                SET password_hash = ?
                WHERE id = ?
            """, (new_password_hash, user_id))

            conn.commit()

    # ========================================================================
    # RESET TOKEN STORAGE (persistent across restarts)
    # ========================================================================

    def store_reset_token(self, token: str, username: str, expires_at: datetime) -> None:
        """Store a password reset token in the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO reset_tokens (token, username, expires_at) VALUES (?, ?, ?)",
                (token, username, expires_at.isoformat())
            )
            conn.commit()

    def get_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Retrieve a reset token if it exists and hasn't expired."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, expires_at FROM reset_tokens WHERE token = ? AND datetime(expires_at) > datetime('now')",
                (token,)
            )
            row = cursor.fetchone()
            if row:
                return {"username": row[0], "expires_at": row[1]}
            return None

    def delete_reset_token(self, token: str) -> None:
        """Delete a reset token after use."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reset_tokens WHERE token = ?", (token,))
            conn.commit()

    def cleanup_expired_tokens(self) -> None:
        """Remove all expired reset tokens."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reset_tokens WHERE datetime(expires_at) < datetime('now')")
            conn.commit()

    def record_user_activity(self, user_id: int, activity_date: str) -> None:
        """Record user activity for engagement metrics (DAU/WAU/MAU)."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_activity (user_id, activity_date, login_count)
                VALUES (?, ?, 1)
                ON CONFLICT(user_id, activity_date) DO UPDATE SET
                    login_count = login_count + 1
            """, (user_id, activity_date))
            conn.commit()

    def close(self) -> None:
        """Close database connection (cleanup)."""
        # SQLite connections are closed automatically with context managers
        pass


# Alias for backwards compatibility and clearer naming
BudgetDatabase = EncryptedDatabase
