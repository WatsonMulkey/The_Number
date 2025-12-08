"""
Pytest configuration and shared fixtures for The_Number tests.
"""
import pytest
import os
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_db_path():
    """Provide a temporary database path for testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_budget.db")
    yield db_path
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def temp_env_file():
    """Provide a temporary .env file for testing."""
    temp_dir = tempfile.mkdtemp()
    env_path = os.path.join(temp_dir, ".env")
    yield env_path
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


@pytest.fixture
def mock_encryption_key():
    """Provide a mock encryption key for testing."""
    from cryptography.fernet import Fernet
    return Fernet.generate_key()


@pytest.fixture
def sample_transactions():
    """Provide sample transaction data for testing."""
    return [
        {"date": "2025-12-01", "amount": -50.00, "category": "groceries", "description": "Whole Foods"},
        {"date": "2025-12-02", "amount": -25.50, "category": "transportation", "description": "Gas"},
        {"date": "2025-12-03", "amount": -100.00, "category": "utilities", "description": "Electric bill"},
        {"date": "2025-12-04", "amount": 3000.00, "category": "income", "description": "Paycheck"},
        {"date": "2025-12-05", "amount": -15.75, "category": "entertainment", "description": "Movie ticket"},
    ]


@pytest.fixture
def sample_budget_config():
    """Provide sample budget configuration for testing."""
    return {
        "monthly_income": 3000.00,
        "expenses": {
            "rent": 1200.00,
            "utilities": 150.00,
            "groceries": 400.00,
            "transportation": 200.00,
            "insurance": 100.00,
        },
        "mode": "paycheck",  # or "fixed_pool"
        "days_until_paycheck": 14
    }
