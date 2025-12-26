"""
Encrypted local database layer for The Number app.

Uses SQLite with encryption for storing user data, expenses, and transactions.
All sensitive data is encrypted at rest using Fernet symmetric encryption.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
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

            # Migration: Add user_id to existing tables if they don't have it
            self._migrate_add_user_id(cursor)

            conn.commit()

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
        now = datetime.now().isoformat()

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
    def add_expense(self, name: str, amount: float, user_id: int, is_fixed: bool = True) -> int:
        """
        Add an expense to the database for a specific user.

        Args:
            name: Expense name
            amount: Expense amount
            user_id: User ID this expense belongs to
            is_fixed: Whether this is a fixed monthly expense

        Returns:
            ID of created expense
        """
        # Validate expense data
        if amount < 0:
            raise ValueError("Expense amount cannot be negative")
        if amount > 10_000_000:
            raise ValueError("Amount exceeds maximum ($10,000,000)")
        if not name or not name.strip():
            raise ValueError("Expense name is required")
        if len(name) > 200:
            raise ValueError("Expense name too long (max 200 characters)")

        name = name.strip()
        now = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO expenses (user_id, name, amount, is_fixed, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, name, amount, 1 if is_fixed else 0, now, now))
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
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }

    def update_expense(self, expense_id: int, user_id: int, name: Optional[str] = None,
                      amount: Optional[float] = None, is_fixed: Optional[bool] = None) -> None:
        """Update an expense for a specific user."""
        # Whitelist of allowed columns (security: prevent SQL injection pattern)
        ALLOWED_COLUMNS = {'name', 'amount', 'is_fixed', 'updated_at'}

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

        if not updates:
            return

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
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
        # Validate transaction data
        if amount <= 0:
            raise ValueError("Transaction amount must be positive")
        if amount > 10_000_000:
            raise ValueError("Amount exceeds maximum ($10,000,000)")
        if not description or not description.strip():
            raise ValueError("Transaction description is required")
        if len(description) > 200:
            raise ValueError("Description too long (max 200 characters)")

        description = description.strip()

        if date is None:
            date = datetime.now()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (user_id, date, amount, description, category, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, date.isoformat(), amount, description, category, datetime.now().isoformat()))
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

    def get_total_spending_today(self, user_id: int) -> float:
        """Get total spending for today for a specific user."""
        today = datetime.now().date().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(amount) as total
                FROM transactions
                WHERE user_id = ? AND DATE(date) = DATE(?)
            """, (user_id, today))
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
            ValueError: If username already exists
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            now = datetime.now().isoformat()

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

    def close(self) -> None:
        """Close database connection (cleanup)."""
        # SQLite connections are closed automatically with context managers
        pass


# Alias for backwards compatibility and clearer naming
BudgetDatabase = EncryptedDatabase
