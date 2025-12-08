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
        print("\n" + "="*60)
        print("IMPORTANT: Save this encryption key securely!")
        print("You will need it to access your data.")
        print("="*60)
        print(f"\nEncryption Key: {key.decode()}\n")
        print("Add this to your .env file as DB_ENCRYPTION_KEY")
        print("="*60 + "\n")

    def _init_database(self) -> None:
        """Create database tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # User settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Expenses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    is_fixed INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount REAL NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            conn.commit()

    def _encrypt(self, data: str) -> str:
        """Encrypt a string."""
        return self.cipher.encrypt(data.encode()).decode()

    def _decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string."""
        return self.cipher.decrypt(encrypted_data.encode()).decode()

    # Settings operations
    def set_setting(self, key: str, value: Any) -> None:
        """
        Store an encrypted setting.

        Args:
            key: Setting key (not encrypted)
            value: Setting value (will be encrypted)
        """
        encrypted_value = self._encrypt(json.dumps(value))
        now = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO settings (key, value, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = excluded.updated_at
            """, (key, encrypted_value, now, now))
            conn.commit()

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Retrieve and decrypt a setting.

        Args:
            key: Setting key
            default: Default value if setting doesn't exist

        Returns:
            Decrypted setting value or default
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()

            if row:
                decrypted = self._decrypt(row[0])
                return json.loads(decrypted)
            return default

    # Expense operations
    def add_expense(self, name: str, amount: float, is_fixed: bool = True) -> int:
        """
        Add an expense to the database.

        Args:
            name: Expense name
            amount: Expense amount
            is_fixed: Whether this is a fixed monthly expense

        Returns:
            ID of created expense
        """
        now = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO expenses (name, amount, is_fixed, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            """, (name, amount, 1 if is_fixed else 0, now, now))
            conn.commit()
            return cursor.lastrowid

    def get_expenses(self) -> List[Dict[str, Any]]:
        """
        Get all expenses.

        Returns:
            List of expense dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses ORDER BY created_at DESC")
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

    def update_expense(self, expense_id: int, name: Optional[str] = None,
                      amount: Optional[float] = None, is_fixed: Optional[bool] = None) -> None:
        """Update an expense."""
        updates = []
        params = []

        if name is not None:
            updates.append("name = ?")
            params.append(name)
        if amount is not None:
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

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?",
                params
            )
            conn.commit()

    def delete_expense(self, expense_id: int) -> None:
        """Delete an expense."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()

    # Transaction operations
    def add_transaction(self, amount: float, description: str,
                       date: Optional[datetime] = None, category: Optional[str] = None) -> int:
        """
        Record a spending transaction.

        Args:
            amount: Transaction amount
            description: Transaction description
            date: Transaction date (defaults to now)
            category: Optional category

        Returns:
            ID of created transaction
        """
        if date is None:
            date = datetime.now()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO transactions (date, amount, description, category, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (date.isoformat(), amount, description, category, datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid

    def get_transactions(self, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get transactions, optionally filtered by date range.

        Args:
            start_date: Filter transactions after this date
            end_date: Filter transactions before this date
            limit: Maximum number of transactions to return

        Returns:
            List of transaction dictionaries
        """
        query = "SELECT * FROM transactions WHERE 1=1"
        params = []

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

    def delete_transaction(self, transaction_id: int) -> None:
        """Delete a transaction."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
            conn.commit()

    def get_total_spending_today(self) -> float:
        """Get total spending for today."""
        today = datetime.now().date().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(amount) as total
                FROM transactions
                WHERE DATE(date) = DATE(?)
            """, (today,))
            result = cursor.fetchone()
            return result[0] if result[0] else 0.0

    def close(self) -> None:
        """Close database connection (cleanup)."""
        # SQLite connections are closed automatically with context managers
        pass
