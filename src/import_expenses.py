"""
Expense import functionality for The Number app.

Supports importing expenses from CSV and Excel files.
"""

import csv
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path


def parse_csv_expenses(file_path: str) -> Tuple[List[Dict], List[str]]:
    """
    Parse expenses from a CSV file.

    Expected CSV format:
        name,amount,is_fixed
        Rent,1500,yes
        Groceries,300,no

    Alternative formats also supported:
        - name,amount (defaults to fixed=yes)
        - expense,cost,fixed
        - description,price,type

    Args:
        file_path: Path to CSV file

    Returns:
        Tuple of (expenses_list, errors_list)
        expenses_list: List of expense dictionaries
        errors_list: List of error messages for invalid rows
    """
    expenses = []
    errors = []

    if not os.path.exists(file_path):
        return [], [f"File not found: {file_path}"]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Try to detect delimiter
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter

            reader = csv.DictReader(f, delimiter=delimiter)

            # Normalize header names (case-insensitive, flexible matching)
            if reader.fieldnames:
                normalized_headers = {}
                for header in reader.fieldnames:
                    lower_header = header.lower().strip()
                    if lower_header in ['name', 'expense', 'description', 'item']:
                        normalized_headers['name'] = header
                    elif lower_header in ['amount', 'cost', 'price', 'value']:
                        normalized_headers['amount'] = header
                    elif lower_header in ['is_fixed', 'fixed', 'type', 'category']:
                        normalized_headers['is_fixed'] = header

                if 'name' not in normalized_headers or 'amount' not in normalized_headers:
                    return [], ["CSV must have 'name' and 'amount' columns (or similar)"]

                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    try:
                        name = row[normalized_headers['name']].strip()
                        amount_str = row[normalized_headers['amount']].strip()

                        # Parse amount (remove currency symbols, commas)
                        amount_str = amount_str.replace('$', '').replace(',', '').strip()
                        amount = float(amount_str)

                        if amount < 0:
                            errors.append(f"Row {row_num}: Amount cannot be negative ({name})")
                            continue

                        # Parse is_fixed
                        is_fixed = True  # Default to fixed
                        if 'is_fixed' in normalized_headers:
                            fixed_value = row[normalized_headers['is_fixed']].lower().strip()
                            is_fixed = fixed_value in ['yes', 'y', 'true', '1', 'fixed']

                        expenses.append({
                            'name': name,
                            'amount': amount,
                            'is_fixed': is_fixed
                        })

                    except ValueError as e:
                        errors.append(f"Row {row_num}: Invalid amount format - {str(e)}")
                    except KeyError as e:
                        errors.append(f"Row {row_num}: Missing required field - {str(e)}")

    except Exception as e:
        return [], [f"Error reading CSV file: {str(e)}"]

    return expenses, errors


def parse_excel_expenses(file_path: str) -> Tuple[List[Dict], List[str]]:
    """
    Parse expenses from an Excel file (.xlsx or .xls).

    Expected format (first sheet):
        | name      | amount | is_fixed |
        |-----------|--------|----------|
        | Rent      | 1500   | yes      |
        | Groceries | 300    | no       |

    Args:
        file_path: Path to Excel file

    Returns:
        Tuple of (expenses_list, errors_list)
    """
    try:
        import openpyxl
    except ImportError:
        return [], ["openpyxl library not installed. Run: pip install openpyxl"]

    expenses = []
    errors = []

    if not os.path.exists(file_path):
        return [], [f"File not found: {file_path}"]

    try:
        workbook = openpyxl.load_workbook(file_path, read_only=True)
        sheet = workbook.active

        # Read header row
        headers = []
        for cell in sheet[1]:
            if cell.value:
                headers.append(str(cell.value).lower().strip())

        # Find column indices
        name_col = None
        amount_col = None
        fixed_col = None

        for idx, header in enumerate(headers):
            if header in ['name', 'expense', 'description', 'item']:
                name_col = idx
            elif header in ['amount', 'cost', 'price', 'value']:
                amount_col = idx
            elif header in ['is_fixed', 'fixed', 'type', 'category']:
                fixed_col = idx

        if name_col is None or amount_col is None:
            return [], ["Excel file must have 'name' and 'amount' columns (or similar)"]

        # Read data rows
        for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            try:
                if not row or all(cell is None for cell in row):
                    continue  # Skip empty rows

                name = str(row[name_col]).strip() if row[name_col] else ""
                if not name:
                    continue  # Skip rows without name

                amount = row[amount_col]
                if isinstance(amount, str):
                    amount = amount.replace('$', '').replace(',', '').strip()
                amount = float(amount)

                if amount < 0:
                    errors.append(f"Row {row_num}: Amount cannot be negative ({name})")
                    continue

                # Parse is_fixed
                is_fixed = True  # Default
                if fixed_col is not None and row[fixed_col] is not None:
                    fixed_value = str(row[fixed_col]).lower().strip()
                    is_fixed = fixed_value in ['yes', 'y', 'true', '1', 'fixed']

                expenses.append({
                    'name': name,
                    'amount': amount,
                    'is_fixed': is_fixed
                })

            except (ValueError, TypeError) as e:
                errors.append(f"Row {row_num}: Invalid data - {str(e)}")

        workbook.close()

    except Exception as e:
        return [], [f"Error reading Excel file: {str(e)}"]

    return expenses, errors


def import_expenses_from_file(file_path: str) -> Tuple[List[Dict], List[str]]:
    """
    Import expenses from a file (auto-detects CSV or Excel).

    Args:
        file_path: Path to file

    Returns:
        Tuple of (expenses_list, errors_list)
    """
    if not os.path.exists(file_path):
        return [], [f"File not found: {file_path}"]

    file_ext = Path(file_path).suffix.lower()

    if file_ext == '.csv':
        return parse_csv_expenses(file_path)
    elif file_ext in ['.xlsx', '.xls']:
        return parse_excel_expenses(file_path)
    else:
        return [], [f"Unsupported file type: {file_ext}. Use .csv, .xlsx, or .xls"]


def create_sample_csv(output_path: str = "sample_expenses.csv") -> None:
    """
    Create a sample CSV file showing the expected format.

    Args:
        output_path: Where to save the sample file
    """
    sample_data = [
        ["name", "amount", "is_fixed"],
        ["Rent", "1500", "yes"],
        ["Utilities", "200", "yes"],
        ["Phone Bill", "80", "yes"],
        ["Internet", "60", "yes"],
        ["Groceries", "400", "no"],
        ["Transportation", "150", "no"],
        ["Entertainment", "100", "no"],
    ]

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(sample_data)

    print(f"Sample CSV created: {output_path}")


def validate_expenses(expenses: List[Dict]) -> Tuple[bool, List[str]]:
    """
    Validate imported expenses for common issues.

    Args:
        expenses: List of expense dictionaries

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    if not expenses:
        errors.append("No expenses found in file")
        return False, errors

    # Check for duplicates
    names = [exp['name'].lower() for exp in expenses]
    duplicates = [name for name in set(names) if names.count(name) > 1]
    if duplicates:
        errors.append(f"Duplicate expense names found: {', '.join(duplicates)}")

    # Check for suspiciously large amounts
    for exp in expenses:
        if exp['amount'] > 100000:
            errors.append(f"Suspiciously large amount for '{exp['name']}': ${exp['amount']:,.2f}")

    # Check total expenses
    total = sum(exp['amount'] for exp in expenses)
    if total == 0:
        errors.append("Total expenses is $0")
    elif total > 1000000:
        errors.append(f"Total expenses seems very high: ${total:,.2f}")

    return len(errors) == 0, errors
