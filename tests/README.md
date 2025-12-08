# The_Number Test Suite

## Overview
Comprehensive test suite for The_Number budgeting application, covering security, functionality, integration, and edge cases.

## Test Structure

### Security Tests (`test_security.py`)
- **SQL Injection Prevention**: Tests for SQL injection vulnerabilities
- **Encryption**: Tests for data encryption and key management
- **Input Validation**: Tests for input sanitization and validation
- **File System Security**: Tests for file permissions and security
- **Error Handling**: Tests that errors don't leak sensitive information

### Database Tests (`test_database.py`)
- **Database Setup**: Tests for database initialization
- **CRUD Operations**: Tests for Create, Read, Update, Delete operations
- **Data Integrity**: Tests for data consistency and accuracy
- **Performance**: Tests for query performance and optimization
- **Backup/Restore**: Tests for database backup functionality

### Budget Calculator Tests (`test_budget_calculator.py`)
- **Paycheck Mode**: Tests for paycheck-based budget calculations
- **Fixed Pool Mode**: Tests for fixed money pool calculations
- **Edge Cases**: Tests for edge cases in calculations
- **Decimal Precision**: Tests for accurate monetary arithmetic

### CLI Tests (`test_cli.py`)
- **Command Parsing**: Tests for CLI command parsing
- **User Input**: Tests for input validation and handling
- **Output Formatting**: Tests for display formatting
- **Interactive Flows**: Tests for complete user workflows
- **Error Messages**: Tests for user-friendly error messages

### Integration Tests (`test_integration.py`)
- **End-to-End Workflows**: Tests for complete user journeys
- **Data Persistence**: Tests for data persistence across sessions
- **Component Integration**: Tests for interaction between modules
- **Real-World Scenarios**: Tests for realistic use cases

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_security.py
```

### Run Specific Test Class
```bash
pytest tests/test_security.py::TestSQLInjectionPrevention
```

### Run Specific Test Function
```bash
pytest tests/test_security.py::TestSQLInjectionPrevention::test_malicious_category_input
```

### Run with Coverage
```bash
pytest --cov=src --cov-report=html
```

### Run with Verbose Output
```bash
pytest -v
```

### Run Only Security Tests
```bash
pytest tests/test_security.py -v
```

## Test Coverage Goals
- Minimum 80% code coverage
- 100% coverage for security-critical code
- All edge cases covered
- All user workflows tested

## Security Testing Checklist
- [ ] SQL injection prevention
- [ ] Data encryption (at rest)
- [ ] Input validation and sanitization
- [ ] File permission security
- [ ] No hardcoded secrets
- [ ] Secure error handling
- [ ] Authentication/authorization (if applicable)
- [ ] Sensitive data not in logs
- [ ] .env and database files in .gitignore

## Known Issues to Monitor
*This section will be updated as issues are discovered during testing*

## Testing Best Practices
1. **Isolation**: Each test should be independent
2. **Cleanup**: Use fixtures to ensure proper cleanup
3. **Realistic Data**: Use realistic test data
4. **Edge Cases**: Always test boundary conditions
5. **Security First**: Security tests should never be skipped
6. **Documentation**: Document complex test scenarios

## Fixtures Available
- `temp_db_path`: Temporary database for testing
- `temp_env_file`: Temporary .env file for testing
- `mock_encryption_key`: Mock encryption key
- `sample_transactions`: Sample transaction data
- `sample_budget_config`: Sample budget configuration

## Contributing to Tests
When adding new features:
1. Write tests FIRST (TDD approach)
2. Include security tests for any user input
3. Test edge cases and error conditions
4. Update this README with new test categories
5. Ensure all tests pass before committing

## Test Metrics
*To be updated after first test run*
- Total Tests: TBD
- Passed: TBD
- Failed: TBD
- Coverage: TBD
