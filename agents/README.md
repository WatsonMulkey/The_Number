# Custom Agents for The Number App

This directory contains specialized AI agents for testing, security scanning, and performance profiling of The Number budgeting application.

## Available Agents

### 1. Budget Tester Agent (`budget_tester.py`)

Tests budget calculations with comprehensive edge cases and real-world scenarios.

**Usage:**
```bash
# Run all tests
python agents/budget_tester.py

# Test specific mode
python agents/budget_tester.py --mode paycheck
python agents/budget_tester.py --mode fixed_pool

# Verbose output
python agents/budget_tester.py --verbose
```

**What it tests:**
- Paycheck mode calculations (basic, deficit, edge cases)
- Fixed pool mode calculations (zero money, no expenses, etc.)
- Expense validation (max amounts, negative values)
- Real-world scenarios (college student budget, emergency fund, overspending)
- Floating point precision
- Boundary conditions (1 day remaining, 365 days, etc.)

**Example output:**
```
[+] PASS: Paycheck: Basic Calculation
[+] PASS: Paycheck: Deficit Scenario
[+] PASS: Fixed Pool: Zero Money
...
RESULTS: 17 passed, 0 failed
```

---

### 2. Security Scanner Agent (`security_scanner.py`)

Scans codebase for security vulnerabilities and insecure patterns.

**Usage:**
```bash
# Scan all security categories
python agents/security_scanner.py

# Scan specific category
python agents/security_scanner.py --category injection
python agents/security_scanner.py --category validation
python agents/security_scanner.py --category crypto
python agents/security_scanner.py --category files

# Verbose output
python agents/security_scanner.py --verbose
```

**What it scans for:**
- **SQL Injection**: f-strings in queries, string concatenation
- **Input Validation**: Missing validation, unbounded strings
- **Cryptography**: Weak algorithms (MD5, SHA1), hardcoded keys, exposed secrets
- **Path Traversal**: Insecure file operations, missing path validation
- **Exception Handling**: Bare except clauses, overly broad catches
- **Hardcoded Secrets**: API keys, tokens, credentials in code

**Example output:**
```
SUMMARY:
  Critical: 0
  High:     1
  Medium:   3
  Low:      2
  TOTAL:    6

HIGH ISSUES:
[Cryptography] src/database.py:48
  Sensitive data may be exposed in logs/output
  Code: print(f"Key: {encryption_key}")
```

---

### 3. Performance Profiler Agent (`performance_profiler.py`)

Benchmarks application performance and identifies bottlenecks.

**Usage:**
```bash
# Profile all categories
python agents/performance_profiler.py

# Profile specific category
python agents/performance_profiler.py --benchmark calculator
python agents/performance_profiler.py --benchmark database
python agents/performance_profiler.py --benchmark import

# Adjust iterations (default: 100)
python agents/performance_profiler.py --iterations 1000

# Verbose output
python agents/performance_profiler.py --verbose
```

**What it benchmarks:**
- **Calculator**: Simple/complex budget calculations, fixed pool mode
- **Database**: Insert/query operations for expenses and transactions
- **Import**: CSV parsing performance
- **Memory**: Memory usage analysis for core operations

**Example output:**
```
Benchmark                                     Avg (ms)     Med (ms)     StdDev
--------------------------------------------------------------------------------
Database: Query 100 Transactions              12.34        11.98        1.23       [GOOD]
Calculator: Simple Paycheck Mode              0.45         0.43         0.08       [EXCELLENT]
Import: Parse CSV (50 rows)                   8.76         8.50         0.95       [GOOD]

BOTTLENECK ANALYSIS:
[!] SLOWEST: Database: Query 100 Transactions
    Average: 12.34ms
    Recommendation: Consider optimization

RECOMMENDATIONS:
  [+] Calculator performance is excellent
  [+] Database performance is good
  [+] Import performance is acceptable
```

---

## Integration with Development Workflow

### Pre-Commit Testing

Add to your pre-commit workflow:

```bash
# Run budget tests before committing
python agents/budget_tester.py || exit 1
```

### CI/CD Pipeline

Include in your CI/CD:

```yaml
# .github/workflows/ci.yml
- name: Run Budget Tests
  run: python agents/budget_tester.py

- name: Security Scan
  run: python agents/security_scanner.py

- name: Performance Benchmark
  run: python agents/performance_profiler.py --iterations 50
```

### Weekly Security Audits

Schedule weekly security scans:

```bash
#!/bin/bash
# weekly_security_audit.sh

echo "Running security scan..."
python agents/security_scanner.py > security_report_$(date +%Y%m%d).txt

if [ $? -ne 0 ]; then
    echo "Security issues found! Check report."
    exit 1
fi
```

### Performance Regression Testing

Compare performance over time:

```bash
# Baseline performance
python agents/performance_profiler.py --iterations 1000 > baseline.txt

# After changes
python agents/performance_profiler.py --iterations 1000 > current.txt

# Compare (manual review)
diff baseline.txt current.txt
```

---

## Agent Architecture

All agents follow a consistent pattern:

```python
class Agent:
    def __init__(self, verbose: bool = False):
        """Initialize agent with optional verbose logging."""

    def log(self, message: str, level: str = "INFO"):
        """Log messages when verbose mode is enabled."""

    def run(self):
        """Execute the agent's primary function."""

    def report(self):
        """Generate and display results."""
```

This makes it easy to:
- Run agents from command line or import as modules
- Integrate with CI/CD pipelines
- Extend with new functionality
- Compose agents together

---

## Extending the Agents

### Adding New Tests to Budget Tester

```python
def test_your_scenario(self):
    """Test your specific scenario."""
    calc = BudgetCalculator()
    # Your test logic here
    assert expected == actual

# Add to run_all_tests():
self.run_test("Your Test Name", self.test_your_scenario)
```

### Adding New Security Checks

```python
def check_your_vulnerability(self, file_path, content, lines):
    """Check for your specific vulnerability."""
    issues = []
    # Your scanning logic here
    return issues

# Add to scan_file():
issues.extend(self.check_your_vulnerability(file_path, content, lines))
```

### Adding New Benchmarks

```python
def bench_your_operation(self):
    """Benchmark your operation."""
    def run():
        # Operation to benchmark
        pass

    return self.benchmark("Your Benchmark Name", run)

# Add to run_benchmarks():
self.bench_your_operation()
```

---

## Requirements

All agents use only standard library and existing project dependencies:

- Python 3.8+
- src/calculator.py
- src/database.py
- src/import_expenses.py

No additional packages required!

---

## Exit Codes

All agents follow standard exit code conventions:

- **0**: Success (all tests passed, no critical issues, benchmarks completed)
- **1**: Failure (tests failed, critical/high security issues found)

This makes them CI/CD friendly:

```bash
python agents/budget_tester.py && echo "Tests passed!" || echo "Tests failed!"
```

---

## Tips

1. **Run agents regularly**: Don't wait for issues to accumulate
2. **Use verbose mode** during development to understand what's being tested
3. **Track performance over time**: Save benchmark results to detect regressions
4. **Customize for your needs**: These agents are templates - extend them!
5. **Integrate with git hooks**: Catch issues before they're committed

---

## Future Enhancements

Potential additions:

- **Code Coverage Agent**: Analyze test coverage gaps
- **Dependency Scanner**: Check for vulnerable dependencies
- **Documentation Checker**: Ensure code is well-documented
- **API Tester**: Test CLI interface and user workflows
- **Stress Tester**: Test with extreme data volumes

Want to contribute? These agents are easy to extend!
