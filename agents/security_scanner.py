#!/usr/bin/env python3
"""
Security Scanner Agent for The Number App

This agent performs comprehensive security scanning to identify vulnerabilities,
insecure patterns, and potential attack vectors in the codebase.

Usage:
    python agents/security_scanner.py [--category all|injection|validation|crypto|files] [--verbose]
"""

import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class SecurityIssue:
    """Represents a security issue found during scanning."""

    SEVERITY_CRITICAL = "CRITICAL"
    SEVERITY_HIGH = "HIGH"
    SEVERITY_MEDIUM = "MEDIUM"
    SEVERITY_LOW = "LOW"

    def __init__(self, severity: str, category: str, file: str, line: int,
                 description: str, code_snippet: str = None):
        self.severity = severity
        self.category = category
        self.file = file
        self.line = line
        self.description = description
        self.code_snippet = code_snippet

    def __repr__(self):
        return f"[{self.severity}] {self.file}:{self.line} - {self.description}"


class SecurityScannerAgent:
    """Agent that scans code for security vulnerabilities."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.issues: List[SecurityIssue] = []
        self.project_root = Path(__file__).parent.parent

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            prefix = {
                "INFO": "[*]",
                "FOUND": "[!]",
                "SCAN": "[>]"
            }.get(level, "[?]")
            print(f"{prefix} {message}")

    def scan_file(self, file_path: Path) -> List[SecurityIssue]:
        """Scan a single file for security issues."""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            self.log(f"Scanning {file_path.relative_to(self.project_root)}", "SCAN")

            # Run all security checks
            issues.extend(self.check_sql_injection(file_path, content, lines))
            issues.extend(self.check_input_validation(file_path, content, lines))
            issues.extend(self.check_crypto_issues(file_path, content, lines))
            issues.extend(self.check_file_operations(file_path, content, lines))
            issues.extend(self.check_exception_handling(file_path, content, lines))
            issues.extend(self.check_hardcoded_secrets(file_path, content, lines))

        except Exception as e:
            self.log(f"Error scanning {file_path}: {e}", "FOUND")

        return issues

    def check_sql_injection(self, file_path: Path, content: str, lines: List[str]) -> List[SecurityIssue]:
        """Check for SQL injection vulnerabilities."""
        issues = []

        # Check for string formatting in SQL queries
        sql_format_pattern = re.compile(r'(execute|cursor\.execute|query).*[f"\'].*%.*["\']', re.IGNORECASE)
        sql_fstring_pattern = re.compile(r'(execute|cursor\.execute|query).*f["\']', re.IGNORECASE)

        for i, line in enumerate(lines, start=1):
            # f-string in SQL
            if 'execute' in line.lower() and 'f"' in line or "f'" in line:
                # Check if it's using f-string with variables (not just constants)
                if '{' in line:
                    issues.append(SecurityIssue(
                        severity=SecurityIssue.SEVERITY_CRITICAL,
                        category="SQL Injection",
                        file=str(file_path.relative_to(self.project_root)),
                        line=i,
                        description="Potential SQL injection via f-string formatting",
                        code_snippet=line.strip()
                    ))

            # String concatenation in SQL
            if 'execute' in line.lower() and '+' in line and ('SELECT' in line or 'UPDATE' in line or 'INSERT' in line):
                issues.append(SecurityIssue(
                    severity=SecurityIssue.SEVERITY_CRITICAL,
                    category="SQL Injection",
                    file=str(file_path.relative_to(self.project_root)),
                    line=i,
                    description="Potential SQL injection via string concatenation",
                    code_snippet=line.strip()
                ))

        return issues

    def check_input_validation(self, file_path: Path, content: str, lines: List[str]) -> List[SecurityIssue]:
        """Check for missing input validation."""
        issues = []

        # Check for user input without validation
        input_functions = ['input(', 'request.', 'sys.argv', 'os.environ']

        for i, line in enumerate(lines, start=1):
            for input_func in input_functions:
                if input_func in line:
                    # Look ahead to see if there's validation
                    next_lines = lines[i:min(i+5, len(lines))]
                    has_validation = any(
                        'if' in l or 'validate' in l.lower() or 'raise' in l
                        for l in next_lines
                    )

                    if not has_validation and 'test' not in str(file_path):
                        issues.append(SecurityIssue(
                            severity=SecurityIssue.SEVERITY_MEDIUM,
                            category="Input Validation",
                            file=str(file_path.relative_to(self.project_root)),
                            line=i,
                            description=f"User input from {input_func} may lack validation",
                            code_snippet=line.strip()
                        ))

        # Check for missing length limits on strings
        if '.append(' in content or 'input(' in content:
            has_max_length = 'MAX_STRING_LENGTH' in content or 'max_length' in content.lower()
            if not has_max_length and 'test' not in str(file_path):
                issues.append(SecurityIssue(
                    severity=SecurityIssue.SEVERITY_MEDIUM,
                    category="Input Validation",
                    file=str(file_path.relative_to(self.project_root)),
                    line=0,
                    description="No MAX_STRING_LENGTH constant found - string inputs may be unbounded",
                    code_snippet=None
                ))

        return issues

    def check_crypto_issues(self, file_path: Path, content: str, lines: List[str]) -> List[SecurityIssue]:
        """Check for cryptography-related issues."""
        issues = []

        # Check for weak encryption
        weak_crypto = ['md5', 'sha1', 'DES', 'RC4']
        for i, line in enumerate(lines, start=1):
            for weak in weak_crypto:
                if weak.lower() in line.lower():
                    issues.append(SecurityIssue(
                        severity=SecurityIssue.SEVERITY_HIGH,
                        category="Cryptography",
                        file=str(file_path.relative_to(self.project_root)),
                        line=i,
                        description=f"Weak cryptographic algorithm detected: {weak}",
                        code_snippet=line.strip()
                    ))

        # Check for hardcoded encryption keys
        key_patterns = [
            r'key\s*=\s*["\'][^"\']+["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']'
        ]

        for i, line in enumerate(lines, start=1):
            for pattern in key_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Ignore if it's reading from env
                    if 'getenv' not in line and 'environ' not in line:
                        issues.append(SecurityIssue(
                            severity=SecurityIssue.SEVERITY_CRITICAL,
                            category="Cryptography",
                            file=str(file_path.relative_to(self.project_root)),
                            line=i,
                            description="Potential hardcoded secret/key detected",
                            code_snippet=line.strip()
                        ))

        # Check for keys displayed in logs/prints
        for i, line in enumerate(lines, start=1):
            if 'print' in line.lower() or 'log' in line.lower():
                if any(word in line.lower() for word in ['key', 'password', 'secret', 'token']):
                    # Check if it's being masked
                    if 'mask' not in line.lower() and '[:4]' not in line and '[-4:]' not in line:
                        issues.append(SecurityIssue(
                            severity=SecurityIssue.SEVERITY_HIGH,
                            category="Cryptography",
                            file=str(file_path.relative_to(self.project_root)),
                            line=i,
                            description="Sensitive data may be exposed in logs/output",
                            code_snippet=line.strip()
                        ))

        return issues

    def check_file_operations(self, file_path: Path, content: str, lines: List[str]) -> List[SecurityIssue]:
        """Check for insecure file operations."""
        issues = []

        # Check for path traversal vulnerabilities
        file_ops = ['open(', 'Path(', 'os.path.join', 'read_file', 'write_file']

        for i, line in enumerate(lines, start=1):
            for op in file_ops:
                if op in line:
                    # Check if path validation exists
                    has_validation = (
                        'validate_file_path' in line or
                        'resolve()' in line or
                        '..' not in content or
                        'check' in line.lower()
                    )

                    # Check if it's user input
                    is_user_input = any(word in line for word in ['input', 'argv', 'request'])

                    if is_user_input and not has_validation:
                        issues.append(SecurityIssue(
                            severity=SecurityIssue.SEVERITY_HIGH,
                            category="Path Traversal",
                            file=str(file_path.relative_to(self.project_root)),
                            line=i,
                            description="File operation with user input - path traversal risk",
                            code_snippet=line.strip()
                        ))

        return issues

    def check_exception_handling(self, file_path: Path, content: str, lines: List[str]) -> List[SecurityIssue]:
        """Check for insecure exception handling."""
        issues = []

        for i, line in enumerate(lines, start=1):
            # Bare except
            if re.match(r'^\s*except\s*:', line):
                issues.append(SecurityIssue(
                    severity=SecurityIssue.SEVERITY_MEDIUM,
                    category="Exception Handling",
                    file=str(file_path.relative_to(self.project_root)),
                    line=i,
                    description="Bare except clause - may hide errors",
                    code_snippet=line.strip()
                ))

            # Overly broad exception
            if 'except Exception:' in line or 'except Exception as' in line:
                # Check if it's too broad (should use specific exceptions)
                if 'test' not in str(file_path):
                    issues.append(SecurityIssue(
                        severity=SecurityIssue.SEVERITY_LOW,
                        category="Exception Handling",
                        file=str(file_path.relative_to(self.project_root)),
                        line=i,
                        description="Broad Exception catch - consider specific exceptions",
                        code_snippet=line.strip()
                    ))

        return issues

    def check_hardcoded_secrets(self, file_path: Path, content: str, lines: List[str]) -> List[SecurityIssue]:
        """Check for hardcoded secrets and credentials."""
        issues = []

        # Patterns for common secret formats
        secret_patterns = [
            (r'[A-Za-z0-9]{32,}', 'Long alphanumeric string (possible API key)'),
            (r'sk_[a-z]+_[A-Za-z0-9]{20,}', 'Stripe-style secret key'),
            (r'ghp_[A-Za-z0-9]{36}', 'GitHub Personal Access Token'),
            (r'AIza[0-9A-Za-z\\-_]{35}', 'Google API Key'),
        ]

        for i, line in enumerate(lines, start=1):
            # Skip comments and test files
            if line.strip().startswith('#') or 'test' in str(file_path):
                continue

            for pattern, description in secret_patterns:
                if re.search(pattern, line):
                    # Make sure it's not a variable name or placeholder
                    if '=' in line and 'getenv' not in line:
                        issues.append(SecurityIssue(
                            severity=SecurityIssue.SEVERITY_CRITICAL,
                            category="Hardcoded Secrets",
                            file=str(file_path.relative_to(self.project_root)),
                            line=i,
                            description=f"Possible hardcoded secret: {description}",
                            code_snippet=line.strip()
                        ))

        return issues

    def scan_project(self, category: str = "all") -> Dict[str, int]:
        """Scan entire project for security issues."""
        print("\n" + "="*60)
        print("SECURITY SCANNER AGENT - Analyzing Code")
        print("="*60 + "\n")

        # Get all Python files
        src_dir = self.project_root / 'src'
        python_files = list(src_dir.glob('**/*.py'))

        self.log(f"Found {len(python_files)} Python files to scan")

        for py_file in python_files:
            file_issues = self.scan_file(py_file)

            # Filter by category if specified
            if category != "all":
                category_map = {
                    "injection": "SQL Injection",
                    "validation": "Input Validation",
                    "crypto": "Cryptography",
                    "files": "Path Traversal"
                }
                if category in category_map:
                    file_issues = [
                        issue for issue in file_issues
                        if issue.category == category_map[category]
                    ]

            self.issues.extend(file_issues)

        # Report findings
        self.report_findings()

        # Return statistics
        return {
            'critical': sum(1 for i in self.issues if i.severity == SecurityIssue.SEVERITY_CRITICAL),
            'high': sum(1 for i in self.issues if i.severity == SecurityIssue.SEVERITY_HIGH),
            'medium': sum(1 for i in self.issues if i.severity == SecurityIssue.SEVERITY_MEDIUM),
            'low': sum(1 for i in self.issues if i.severity == SecurityIssue.SEVERITY_LOW)
        }

    def report_findings(self):
        """Generate and print security report."""
        print("\n" + "="*60)
        print("SECURITY SCAN RESULTS")
        print("="*60 + "\n")

        # Group by severity
        by_severity = {
            SecurityIssue.SEVERITY_CRITICAL: [],
            SecurityIssue.SEVERITY_HIGH: [],
            SecurityIssue.SEVERITY_MEDIUM: [],
            SecurityIssue.SEVERITY_LOW: []
        }

        for issue in self.issues:
            by_severity[issue.severity].append(issue)

        # Print summary
        print("SUMMARY:")
        print(f"  Critical: {len(by_severity[SecurityIssue.SEVERITY_CRITICAL])}")
        print(f"  High:     {len(by_severity[SecurityIssue.SEVERITY_HIGH])}")
        print(f"  Medium:   {len(by_severity[SecurityIssue.SEVERITY_MEDIUM])}")
        print(f"  Low:      {len(by_severity[SecurityIssue.SEVERITY_LOW])}")
        print(f"  TOTAL:    {len(self.issues)}\n")

        # Print details for each severity level
        for severity in [SecurityIssue.SEVERITY_CRITICAL, SecurityIssue.SEVERITY_HIGH,
                        SecurityIssue.SEVERITY_MEDIUM, SecurityIssue.SEVERITY_LOW]:
            if by_severity[severity]:
                print(f"\n{severity} ISSUES:")
                print("-" * 60)
                for issue in by_severity[severity]:
                    print(f"\n[{issue.category}] {issue.file}:{issue.line}")
                    print(f"  {issue.description}")
                    if issue.code_snippet:
                        print(f"  Code: {issue.code_snippet}")

        print("\n" + "="*60 + "\n")


def main():
    """Main entry point for the security scanner agent."""
    import argparse

    parser = argparse.ArgumentParser(description="Security Scanner Agent for The Number App")
    parser.add_argument('--category', choices=['all', 'injection', 'validation', 'crypto', 'files'],
                       default='all', help='Category of security issues to scan for')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    agent = SecurityScannerAgent(verbose=args.verbose)
    stats = agent.scan_project(category=args.category)

    # Exit with error code if critical or high severity issues found
    critical_or_high = stats['critical'] + stats['high']
    sys.exit(0 if critical_or_high == 0 else 1)


if __name__ == "__main__":
    main()
