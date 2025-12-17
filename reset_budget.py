#!/usr/bin/env python
"""Reset budget configuration to trigger onboarding."""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, '.')

from src.database import EncryptedDatabase
from dotenv import load_dotenv

# Load environment
env_path = Path(".env")
load_dotenv(env_path)

# Get encryption key
encryption_key = os.getenv("DB_ENCRYPTION_KEY")

# Connect to database
db = EncryptedDatabase(encryption_key=encryption_key)

# Clear budget configuration
db.set_setting("budget_mode", None)
db.set_setting("monthly_income", None)
db.set_setting("days_until_paycheck", None)
db.set_setting("total_money", None)

# Clear expenses
expenses = db.get_expenses()
for exp in expenses:
    db.delete_expense(exp['id'])

print("Budget configuration reset successfully!")
print("Reload your browser to see the onboarding flow.")
