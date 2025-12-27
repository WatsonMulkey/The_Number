# Expense Import Guide

Import your expenses from CSV or Excel files into The Number app.

## Supported File Formats

- **CSV** (.csv) - Comma-separated values
- **Excel** (.xlsx, .xls) - Microsoft Excel files

## File Format

### Required Columns

Your file must have these columns (names are flexible):

1. **Name** (or: expense, description, item)
   - The expense name/description
   - Example: "Rent", "Groceries", "Phone Bill"

2. **Amount** (or: cost, price, value)
   - The monthly expense amount
   - Can include currency symbols ($) and commas
   - Example: "$1,500.00" or "1500" or "1500.00"

### Optional Column

3. **Is Fixed** (or: fixed, type, category)
   - Whether this is a fixed monthly expense
   - Values: "yes", "y", "true", "1", "fixed" = Fixed expense
   - Values: "no", "n", "false", "0", "variable" = Variable expense
   - **Default**: If column is missing, all expenses are treated as fixed

## Example Files

### CSV Format

```csv
name,amount,is_fixed
Rent,1500,yes
Utilities,200,yes
Phone Bill,80,yes
Internet,60,yes
Car Insurance,120,yes
Groceries,400,no
Transportation,150,no
Entertainment,100,no
Dining Out,200,no
```

### With Currency Symbols

```csv
name,amount,is_fixed
Rent,"$1,500.00",yes
Utilities,$200.00,yes
Groceries,$400,no
```

### Minimal Format (no is_fixed column)

```csv
name,amount
Rent,1500
Utilities,200
Groceries,400
```

### Alternative Column Names

```csv
expense,cost,fixed
Rent,1500,yes
Groceries,400,no
```

```csv
description,price,type
Monthly Rent,1500,fixed
Weekly Groceries,400,variable
```

## How to Import

### Step 1: Prepare Your File

Create a CSV or Excel file with your expenses using the format above.

**Tips:**
- Use consistent formatting for amounts
- Remove any header rows except the column names
- Make sure there are no blank rows in the middle of your data
- Save Excel files as .xlsx or .xls

### Step 2: Open The Number App

```bash
python main.py
```

### Step 3: Navigate to Import

1. Select "Manage Expenses" from the main menu
2. Select "Import from CSV/Excel"

### Step 4: Create Sample (Optional)

The app can create a sample CSV file for you:
- Answer "yes" when asked to create a sample file
- Edit `sample_expenses.csv` with your data
- Use it as a template

### Step 5: Enter File Path

Provide the path to your file:
- Absolute path: `C:\Users\YourName\expenses.csv`
- Relative path: `expenses.csv` (if in the same folder)
- Can drag & drop file to get path (in some terminals)

### Step 6: Review Preview

The app will show you:
- All expenses that will be imported
- Total amount
- Number of expenses
- Any errors or warnings

### Step 7: Choose Import Mode

1. **Add to existing** - Keeps your current expenses and adds new ones
2. **Replace all** - Clears current expenses and imports new ones

### Step 8: Confirm

Review the preview and confirm the import.

## Validation & Error Checking

The import system checks for:

### Errors (will prevent import)
- Missing required columns (name, amount)
- Invalid amount format (not a number)
- Negative amounts
- File not found

### Warnings (will show but allow import)
- Duplicate expense names (case-insensitive)
- Suspiciously large amounts (> $100,000)
- Very high total expenses (> $1,000,000)
- Empty file or zero total

## Examples

### Example 1: Import from CSV

```
File: monthly_expenses.csv

name,amount,is_fixed
Rent,1500,yes
Electric,120,yes
Water,45,yes
Groceries,400,no

→ Imports 4 expenses
→ Total: $2,065/month
→ 3 fixed, 1 variable
```

### Example 2: Import from Excel

```
File: budget.xlsx (Sheet 1)

| Expense          | Amount | Fixed |
|------------------|--------|-------|
| Mortgage         | 2200   | yes   |
| HOA Fees         | 350    | yes   |
| Utilities        | 250    | yes   |
| Groceries        | 600    | no    |
| Gas              | 200    | no    |

→ Imports 5 expenses
→ Total: $3,600/month
→ 3 fixed, 2 variable
```

### Example 3: Replace Existing Expenses

```
Current expenses: Rent ($1,200), Groceries ($300)
Import file: new_budget.csv (5 expenses)

Select mode: 2 (Replace all)

→ Deletes Rent and Groceries
→ Imports all 5 new expenses
```

## Troubleshooting

### "File not found"
- Check the file path is correct
- Use quotes around paths with spaces: `"C:\My Files\expenses.csv"`
- Verify the file exists in that location

### "Must have 'name' and 'amount' columns"
- Check your column headers
- Make sure header row is the first row
- Use one of the supported column names

### "Invalid amount format"
- Remove any text from amount cells
- Make sure amounts are numbers
- Use only numbers, decimals, $, and commas

### "Duplicate expense names found"
- You have multiple expenses with the same name
- Decide if you want to:
  - Combine them (sum the amounts manually)
  - Keep both (rename one of them)
  - Remove one

### Excel file error
- Make sure openpyxl is installed: `pip install openpyxl`
- Check the file isn't corrupted
- Try saving as a new .xlsx file

## Tips for Success

1. **Start with sample file**
   - Use the app's sample file generator
   - It shows the correct format
   - Easy to edit and import

2. **Export from your current system**
   - Many budgeting apps can export CSV
   - Spreadsheet apps can save as CSV
   - Just rename the columns to match

3. **Test with a few expenses first**
   - Import 2-3 expenses to verify format
   - Once it works, import the full list
   - Use "Add to existing" to build incrementally

4. **Keep a backup**
   - Save your import file
   - You can re-import if needed
   - Useful for monthly updates

5. **Review before confirming**
   - Check the preview carefully
   - Verify amounts are correct
   - Look for any errors/warnings

## Advanced: Batch Updates

You can use import to update your expenses monthly:

1. Export current expenses to CSV (manually for now)
2. Update amounts in the CSV file
3. Import with "Replace all" mode
4. Your expenses are updated!

This is useful if your expenses change frequently or you track them in Excel.

## File Format Reference

### CSV (Comma-Separated Values)
- Text file with .csv extension
- Each line is a row
- Columns separated by commas
- First row is header (column names)
- Can open/edit in Excel, Google Sheets, or text editor

### Excel (.xlsx/.xls)
- Microsoft Excel format
- Can have multiple sheets (only first sheet is read)
- Supports formulas (values are imported, not formulas)
- More features than CSV but CSV is simpler

## Getting Help

If you encounter issues:
1. Check this guide for troubleshooting tips
2. Verify your file format matches the examples
3. Try the sample file generator to see correct format
4. Create a minimal test file (2-3 rows) to isolate the issue

---

*Happy importing! Make budgeting easier by importing all your expenses at once.*
