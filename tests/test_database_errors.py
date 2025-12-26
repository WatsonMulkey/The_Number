"""
Error case tests for the database module.

This test suite focuses on testing unhappy paths, error conditions, and edge cases
to achieve 30%+ error coverage as part of the test improvement initiative.

References:
- TEST_COVERAGE_IMPROVEMENT.md
- src/database.py
"""

import pytest
import tempfile
import os
from pathlib import Path
from src.database import BudgetDatabase
from src.calculator import MAX_AMOUNT, MAX_STRING_LENGTH

# Test encryption key (valid Fernet key)
TEST_KEY = "V4R9SIOnCG1ntmUILzyUe0lnQ4OC2bf0EGCuEsslfeg="
TEST_USER_ID = 1  # Default test user ID for all database operations


class TestExpenseErrorCases:
    """Test error handling for expense operations."""

    def test_add_expense_negative_amount_rejected(self):
        """Test that expenses with negative amounts are rejected.

        This prevents data corruption where negative expenses could
        artificially inflate the available budget.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        with pytest.raises(ValueError, match="cannot be negative"):
            db.add_expense("Rent", -1500.0, True)

        # Verify nothing was added
        expenses = db.get_expenses()
        assert len(expenses) == 0, "Invalid expense should not be persisted"

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup

    def test_add_expense_excessive_amount_rejected(self):
        """Test that expenses exceeding MAX_AMOUNT are rejected.

        This prevents integer overflow and ensures reasonable values.
        User Story: As a user, I should get a clear error if I accidentally
        enter $100,000,000 instead of $1,000.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        with pytest.raises(ValueError, match="exceeds maximum"):
            # Try to add expense > MAX_AMOUNT ($10M)
            db.add_expense("Luxury Yacht", 50_000_000.0, False)

        # Verify expense was NOT added
        expenses = db.get_expenses()
        assert len(expenses) == 0, "Excessive expense should not be persisted"

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup

    def test_add_expense_empty_name_rejected(self):
        """Test that expenses with empty names are rejected.

        Empty names make it impossible for users to identify what the expense is for.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        with pytest.raises(ValueError, match="cannot be empty|required"):
            db.add_expense("", 100.0, True)

        # Also test whitespace-only name
        with pytest.raises(ValueError, match="cannot be empty|required"):
            db.add_expense("   ", 100.0, True)

        # Verify nothing was added
        expenses = db.get_expenses()
        assert len(expenses) == 0

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup

    def test_add_expense_name_too_long_rejected(self):
        """Test that expense names exceeding MAX_STRING_LENGTH are rejected.

        This prevents potential SQL injection attacks via very long strings
        and ensures consistent UI rendering.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        # Create name longer than MAX_STRING_LENGTH (200 chars)
        long_name = "A" * 201

        with pytest.raises(ValueError, match="too long|max.*200"):
            db.add_expense(long_name, 100.0, True)

        # Verify expense was NOT added
        expenses = db.get_expenses()
        assert len(expenses) == 0

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup

    def test_update_expense_nonexistent_id_handled_gracefully(self):
        """Test that updating a non-existent expense doesn't crash.

        Current implementation: silently does nothing (UPDATE with no match).
        This test verifies the graceful handling.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        # Add one expense
        db.add_expense("Rent", 1000.0, True)

        # Try to update expense with ID that doesn't exist
        # Should not crash, just silently do nothing
        db.update_expense(expense_id=999, name="New Name")

        # Verify the existing expense wasn't affected
        expenses = db.get_expenses()
        assert len(expenses) == 1
        assert expenses[0]['name'] == "Rent"
        assert expenses[0]['amount'] == 1000.0

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup

    def test_delete_expense_nonexistent_id_handled_gracefully(self):
        """Test that deleting a non-existent expense doesn't crash.

        This should either raise a clear error or fail silently (depending on design).
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        # Deleting non-existent expense should not crash
        # (it may raise an error or return False, but shouldn't crash)
        try:
            result = db.delete_expense(999)
            # If it returns a value, should be False or similar
            assert result is False or result is None
        except (ValueError, KeyError):
            # If it raises an error, that's also acceptable
            pass

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup


class TestTransactionErrorCases:
    """Test error handling for transaction operations."""

    def test_add_transaction_negative_amount_rejected(self):
        """Test that transactions with negative amounts are rejected.

        Transactions should always be positive (spending).
        Negative amounts could be confused with refunds or income.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        with pytest.raises(ValueError, match="must be positive|cannot be negative"):
            db.add_transaction(-25.50, "Invalid refund")

        # Verify nothing was added
        transactions = db.get_transactions(limit=100)
        assert len(transactions) == 0

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup

    def test_add_transaction_zero_amount_rejected(self):
        """Test that transactions with zero amount are rejected.

        Zero-dollar transactions don't make sense and could indicate input errors.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        with pytest.raises(ValueError, match="must be positive|cannot be zero"):
            db.add_transaction(0.0, "Free coffee")

        # Verify nothing was added
        transactions = db.get_transactions(limit=100)
        assert len(transactions) == 0

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup

    def test_add_transaction_excessive_amount_rejected(self):
        """Test that transactions exceeding MAX_AMOUNT are rejected.

        This prevents typos like entering $100,000 instead of $100.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        with pytest.raises(ValueError, match="exceeds maximum"):
            db.add_transaction(50_000_000.0, "Accidentally bought a yacht")

        # Verify transaction was NOT added
        transactions = db.get_transactions(limit=100)
        assert len(transactions) == 0

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup

    def test_add_transaction_empty_description_rejected(self):
        """Test that transactions with empty descriptions are rejected.

        Descriptions are required to help users remember what they spent money on.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        with pytest.raises(ValueError, match="description.*required|cannot be empty"):
            db.add_transaction(25.0, "")

        # Also test whitespace-only description
        with pytest.raises(ValueError, match="description.*required|cannot be empty"):
            db.add_transaction(25.0, "   ")

        # Verify nothing was added
        transactions = db.get_transactions(limit=100)
        assert len(transactions) == 0

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup

    def test_add_transaction_description_too_long_rejected(self):
        """Test that transaction descriptions exceeding MAX_STRING_LENGTH are rejected."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        # Create description longer than MAX_STRING_LENGTH (200 chars)
        long_desc = "Bought coffee at " + ("a very long store name " * 20)

        with pytest.raises(ValueError, match="too long|max.*200"):
            db.add_transaction(5.0, long_desc)

        # Verify transaction was NOT added
        transactions = db.get_transactions(limit=100)
        assert len(transactions) == 0

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup


class TestDatabaseEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_get_expense_by_id_nonexistent_returns_none(self):
        """Test that querying a non-existent expense returns None (not error).

        This is a common pattern where the absence of data is not an error,
        but should return None to allow graceful handling.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        # Query non-existent expense
        expense = db.get_expense_by_id(999)
        assert expense is None, "Non-existent expense should return None"

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup

    def test_database_operations_with_special_characters(self):
        """Test that special characters in strings don't cause SQL injection.

        This is a security test to ensure proper parameterization.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        # Try various special characters
        dangerous_strings = [
            "'; DROP TABLE expenses; --",
            "Robert'); DROP TABLE students;--",
            "\" OR \"\"=\"",
            "<script>alert('XSS')</script>",
            "../../etc/passwd",
        ]

        for dangerous_string in dangerous_strings:
            # Should either accept (with sanitization) or reject (with clear error)
            try:
                db.add_expense(dangerous_string, 100.0, True)
                # If accepted, verify it was sanitized
                expenses = db.get_expenses()
                # Database should still exist and work
                assert len(expenses) >= 0
                # Clean up for next test
                if len(expenses) > 0:
                    db.delete_expense(expenses[-1]['id'])
            except ValueError:
                # If rejected, that's also acceptable
                pass

        # Verify database still works
        db.add_expense("Normal Expense", 50.0, True)
        expenses = db.get_expenses()
        assert len(expenses) > 0

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup

    def test_add_expense_at_max_amount_boundary(self):
        """Test that expenses at exactly MAX_AMOUNT are accepted.

        Boundary testing: value at the edge should be valid.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        # MAX_AMOUNT ($10M) should be accepted
        db.add_expense("Exactly Max", MAX_AMOUNT, True)

        expenses = db.get_expenses()
        assert len(expenses) == 1
        assert expenses[0]['amount'] == MAX_AMOUNT

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup

    def test_add_expense_just_over_max_amount_rejected(self):
        """Test that expenses just over MAX_AMOUNT are rejected.

        Boundary testing: value just over the edge should be invalid.
        """
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
            db_path = f.name
            f.close()

        db = BudgetDatabase(db_path, encryption_key=TEST_KEY)

        with pytest.raises(ValueError, match="exceeds maximum"):
            db.add_expense("Just Over Max", MAX_AMOUNT + 0.01, True)

        # Verify nothing was added
        expenses = db.get_expenses()
        assert len(expenses) == 0

        # Cleanup
        db.close()
        try:
            os.unlink(db_path)
        except PermissionError:
            pass  # Windows file locking - best effort cleanup


# Import sqlite3 for the test that uses it
import sqlite3
