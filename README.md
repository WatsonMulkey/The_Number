# The Number

A simple, gamified budgeting app that gives you one number: how much you can spend today.

## Philosophy

Budgeting can be overwhelming with complex spreadsheets and detailed tracking. **The Number** simplifies it by answering one question: *"How much can I spend today?"*

Perfect for people with planning challenges who want a straightforward, gamified approach to daily budgeting.

## Features

- **Two Budgeting Modes:**
  - **Paycheck Mode**: Calculate daily spending based on your income and days until next paycheck
  - **Fixed Pool Mode**: Calculate how long your current money will last with your expenses

- **Expense Management**:
  - Track fixed and variable monthly expenses
  - Import expenses from CSV or Excel files
  - Export budget data for backup or sharing

- **Transaction Logging**: Record daily spending and see how much you have left

- **Guided Onboarding**: First-time setup wizard walks you through configuration

- **Secure Local Storage**: All data encrypted at rest with Fernet encryption

- **Simple CLI**: Clean, intuitive command-line interface

- **Comprehensive Testing**: 236 passing tests covering security, error handling, and functionality

## Installation

1. **Clone the repository:**
   ```bash
   git clone git@github.com:WatsonMulkey/The_Number.git
   cd The_Number
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the app:**
   ```bash
   python main.py
   ```

   On first run, the app will automatically create an encrypted `.env` file with your encryption key.

## Usage

### First Time Setup

1. Run `python main.py`
2. The guided onboarding wizard will walk you through:
   - Choosing your budgeting mode (Paycheck or Fixed Pool)
   - Entering your income or available money
   - Adding your monthly expenses
   - Getting your first daily budget number!

Alternatively, you can manually configure later via **"Setup Budget Mode"** from the main menu.

### Daily Usage

1. Run `python main.py`
2. Select **"Get The Number"** to see your daily spending limit
3. Record spending throughout the day with **"Record Spending"**
4. Check your remaining budget anytime

## Project Structure

```
The_Number/
├── src/
│   ├── calculator.py       # Budget calculation engine
│   ├── database.py         # Encrypted SQLite database
│   ├── cli.py              # Command-line interface
│   ├── onboarding.py       # First-time setup wizard
│   ├── import_expenses.py  # CSV/Excel import functionality
│   ├── export_expenses.py  # Data export functionality
│   └── utils.py            # Utility functions
├── tests/                  # Comprehensive test suite (236 tests)
│   ├── test_calculator.py
│   ├── test_database.py
│   ├── test_database_errors.py
│   ├── test_cli.py
│   ├── test_import_expenses.py
│   ├── test_export_expenses.py
│   ├── test_integration.py
│   └── test_security.py
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env                    # Encryption key (auto-generated, git-ignored)
└── README.md              # This file
```

## Security

- All sensitive data is encrypted at rest using Fernet symmetric encryption
- Database file and encryption key are stored locally
- No network connections or external services
- `.env` file with encryption key is automatically git-ignored

**Important**: Keep your `.env` file secure. If you lose it, you won't be able to access your encrypted data.

## Future Enhancements

- Email/SMS notifications with daily budget
- Bank API integration (Plaid) for automatic transaction import
- Web interface
- Mobile app
- Budget reports and spending analytics
- Category-based budgeting

## Contributing

This is a personal project, but suggestions and improvements are welcome! Please open an issue or submit a pull request.

## License

MIT License - Feel free to use and modify as needed.

## Author

Built with Claude Code
