"""
Unit tests for expense import functionality.
"""

import pytest
import os
import csv
from pathlib import Path
from src.import_expenses import (
    parse_csv_expenses,
    import_expenses_from_file,
    validate_expenses,
    create_sample_csv
)


class TestCSVImport:
    """Test CSV expense import functionality."""

    def test_parse_valid_csv(self, tmp_path):
        """Test parsing a valid CSV file."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("""name,amount,is_fixed
Rent,1500,yes
Groceries,300,no
""")

        expenses, errors = parse_csv_expenses(str(csv_file))

        assert len(expenses) == 2
        assert len(errors) == 0
        assert expenses[0]['name'] == 'Rent'
        assert expenses[0]['amount'] == 1500.0
        assert expenses[0]['is_fixed'] is True
        assert expenses[1]['name'] == 'Groceries'
        assert expenses[1]['amount'] == 300.0
        assert expenses[1]['is_fixed'] is False

    def test_parse_csv_with_currency(self, tmp_path):
        """Test parsing CSV with currency symbols."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("""name,amount
Rent,$1500.00
Utilities,$200
""")

        expenses, errors = parse_csv_expenses(str(csv_file))

        assert len(expenses) == 2
        assert expenses[0]['amount'] == 1500.0
        assert expenses[1]['amount'] == 200.0

    def test_parse_csv_missing_fixed_column(self, tmp_path):
        """Test CSV without is_fixed column defaults to fixed=True."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("""name,amount
Rent,1500
""")

        expenses, errors = parse_csv_expenses(str(csv_file))

        assert len(expenses) == 1
        assert expenses[0]['is_fixed'] is True

    def test_parse_csv_alternative_headers(self, tmp_path):
        """Test CSV with alternative column names."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("""expense,cost,fixed
Rent,1500,yes
""")

        expenses, errors = parse_csv_expenses(str(csv_file))

        assert len(expenses) == 1
        assert expenses[0]['name'] == 'Rent'

    def test_parse_csv_negative_amount(self, tmp_path):
        """Test that negative amounts generate errors."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("""name,amount
Rent,-1500
""")

        expenses, errors = parse_csv_expenses(str(csv_file))

        assert len(expenses) == 0
        assert len(errors) == 1
        assert "negative" in errors[0].lower()

    def test_parse_csv_invalid_amount(self, tmp_path):
        """Test that invalid amounts generate errors."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("""name,amount
Rent,not_a_number
""")

        expenses, errors = parse_csv_expenses(str(csv_file))

        assert len(expenses) == 0
        assert len(errors) == 1

    def test_parse_csv_file_not_found(self):
        """Test handling of non-existent file."""
        expenses, errors = parse_csv_expenses("nonexistent.csv")

        assert len(expenses) == 0
        assert len(errors) == 1
        assert "not found" in errors[0].lower()

    def test_parse_csv_missing_columns(self, tmp_path):
        """Test CSV with missing required columns."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("""description,price
Some expense,100
""")

        # Should work with alternative names
        expenses, errors = parse_csv_expenses(str(csv_file))
        assert len(expenses) == 1


class TestValidation:
    """Test expense validation."""

    def test_validate_empty_list(self):
        """Test validation of empty expense list."""
        is_valid, errors = validate_expenses([])

        assert not is_valid
        assert any("no expenses" in err.lower() for err in errors)

    def test_validate_duplicates(self):
        """Test detection of duplicate expense names."""
        expenses = [
            {'name': 'Rent', 'amount': 1500, 'is_fixed': True},
            {'name': 'rent', 'amount': 1500, 'is_fixed': True},  # Case-insensitive duplicate
        ]

        is_valid, errors = validate_expenses(expenses)

        assert not is_valid
        assert any("duplicate" in err.lower() for err in errors)

    def test_validate_large_amount(self):
        """Test warning for suspiciously large amounts."""
        expenses = [
            {'name': 'House', 'amount': 500000, 'is_fixed': True},
        ]

        is_valid, errors = validate_expenses(expenses)

        assert not is_valid
        assert any("suspiciously large" in err.lower() for err in errors)

    def test_validate_valid_expenses(self):
        """Test validation passes for valid expenses."""
        expenses = [
            {'name': 'Rent', 'amount': 1500, 'is_fixed': True},
            {'name': 'Groceries', 'amount': 300, 'is_fixed': False},
        ]

        is_valid, errors = validate_expenses(expenses)

        assert is_valid
        assert len(errors) == 0


class TestAutoDetect:
    """Test file type auto-detection."""

    def test_import_csv(self, tmp_path):
        """Test importing CSV file."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("""name,amount
Rent,1500
""")

        expenses, errors = import_expenses_from_file(str(csv_file))

        assert len(expenses) == 1

    def test_import_unsupported_type(self, tmp_path):
        """Test error for unsupported file type."""
        # Create a .txt file that exists
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("some content")
        
        expenses, errors = import_expenses_from_file(str(txt_file))

        assert len(expenses) == 0
        assert any("unsupported" in err.lower() for err in errors)


class TestSampleFile:
    """Test sample file generation."""

    def test_create_sample_csv(self, tmp_path):
        """Test creating a sample CSV file."""
        sample_path = tmp_path / "sample.csv"
        create_sample_csv(str(sample_path))

        assert sample_path.exists()

        # Verify it's valid CSV
        expenses, errors = parse_csv_expenses(str(sample_path))
        assert len(expenses) > 0
        assert len(errors) == 0
