#!/usr/bin/env python3
"""
Skeptical Senior Dev Agent for The Number App

This agent critically reviews code, architecture, and processes with a focus on
identifying AI-generated code antipatterns, over-engineering, and technical debt.

The agent is specifically aware of common AI coding pitfalls:
- Over-abstraction and premature optimization
- Incomplete error handling (happy path bias)
- Missing edge cases despite tests
- Security vulnerabilities hidden in "clean" code
- Inconsistent patterns across codebase
- Copy-paste code with subtle bugs

Usage:
    python agents/skeptical_senior_dev.py [--review code|architecture|process|all] [--verbose]
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
import re


class CodeReview:
    """Represents a code review finding."""

    SEVERITY_BLOCKER = "BLOCKER"
    SEVERITY_CRITICAL = "CRITICAL"
    SEVERITY_MAJOR = "MAJOR"
    SEVERITY_MINOR = "MINOR"
    SEVERITY_NITPICK = "NITPICK"

    def __init__(self, severity: str, category: str, file: str, line: int,
                 finding: str, recommendation: str, ai_pattern: bool = False):
        self.severity = severity
        self.category = category
        self.file = file
        self.line = line
        self.finding = finding
        self.recommendation = recommendation
        self.ai_pattern = ai_pattern  # Flag for AI-specific antipatterns

    def __repr__(self):
        ai_flag = " [AI PATTERN]" if self.ai_pattern else ""
        return f"[{self.severity}]{ai_flag} {self.file}:{self.line} - {self.finding}"


class SkepticalSeniorDevAgent:
    """
    Agent that critically reviews code with knowledge of AI coding pitfalls.

    This agent is NOT impressed by:
    - Clever abstractions that add complexity
    - "Clean code" that sacrifices clarity
    - Tests that only verify happy paths
    - Documentation that states the obvious
    - Over-engineered solutions to simple problems
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.reviews: List[CodeReview] = []
        self.project_root = Path(__file__).parent.parent

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            prefix = {
                "INFO": "[*]",
                "REVIEW": "[>]",
                "CONCERN": "[!]",
                "BLOCKER": "[BLOCK]",
                "CRITICAL": "[CRIT]",
                "RESULT": "[+]"
            }.get(level, "[?]")
            print(f"{prefix} {message}")

    # ===== CODE QUALITY REVIEWS =====

    def review_ai_antipatterns(self, file_path: Path, content: str, lines: List[str]) -> List[CodeReview]:
        """
        Check for common AI-generated code antipatterns.

        AI code often:
        - Has perfect formatting but logical flaws
        - Includes todos/comments that were never addressed
        - Has overly generic variable names
        - Duplicates patterns instead of abstracting
        - Has error handling that catches but doesn't handle
        """
        reviews = []

        # Check for TODO comments (AI loves leaving these)
        for i, line in enumerate(lines, start=1):
            if 'TODO' in line or 'FIXME' in line or 'HACK' in line:
                reviews.append(CodeReview(
                    severity=CodeReview.SEVERITY_MAJOR,
                    category="Technical Debt",
                    file=str(file_path.relative_to(self.project_root)),
                    line=i,
                    finding="TODO/FIXME comment found - AI often generates these and forgets",
                    recommendation="Either implement the TODO or remove it. Don't ship with TODOs.",
                    ai_pattern=True
                ))

        # Check for overly generic error messages
        generic_errors = [
            "An error occurred",
            "Something went wrong",
            "Error processing",
            "Invalid input",
            "Failed to"
        ]

        for i, line in enumerate(lines, start=1):
            for generic in generic_errors:
                if generic.lower() in line.lower() and ('raise' in line or 'print' in line or 'log' in line):
                    reviews.append(CodeReview(
                        severity=CodeReview.SEVERITY_MINOR,
                        category="Error Handling",
                        file=str(file_path.relative_to(self.project_root)),
                        line=i,
                        finding=f"Generic error message: '{generic}' - not actionable for users",
                        recommendation="Be specific: what failed? why? what can user do?",
                        ai_pattern=True
                    ))

        # Check for pass in except (AI loves to do this)
        for i, line in enumerate(lines, start=1):
            if 'except' in line:
                # Check next line for just 'pass'
                if i < len(lines) and lines[i].strip() == 'pass':
                    reviews.append(CodeReview(
                        severity=CodeReview.SEVERITY_CRITICAL,
                        category="Error Handling",
                        file=str(file_path.relative_to(self.project_root)),
                        line=i,
                        finding="Exception caught but silently ignored with 'pass'",
                        recommendation="At minimum log the error. Better: handle it properly.",
                        ai_pattern=True
                    ))

        # Check for magic numbers (AI often hardcodes these)
        magic_number_pattern = re.compile(r'[^0-9](100|200|404|500|1000|10000)\b')
        for i, line in enumerate(lines, start=1):
            if magic_number_pattern.search(line) and 'MAX_' not in line and 'MIN_' not in line:
                if not line.strip().startswith('#'):  # Ignore comments
                    reviews.append(CodeReview(
                        severity=CodeReview.SEVERITY_MINOR,
                        category="Magic Numbers",
                        file=str(file_path.relative_to(self.project_root)),
                        line=i,
                        finding="Magic number detected - unclear what it represents",
                        recommendation="Define as named constant with clear meaning",
                        ai_pattern=True
                    ))

        return reviews

    def review_over_engineering(self, file_path: Path, content: str, lines: List[str]) -> List[CodeReview]:
        """
        Check for over-engineering patterns.

        Common AI over-engineering:
        - Abstract base classes with one implementation
        - Design patterns where simple functions would work
        - Layers of indirection for simple operations
        - "Extensibility" that will never be used
        """
        reviews = []

        # Check for ABC (Abstract Base Class) with only one implementation
        if 'ABC' in content or 'abstractmethod' in content:
            # Count how many classes inherit from this ABC
            # This is a simplification - real check would need AST parsing
            reviews.append(CodeReview(
                severity=CodeReview.SEVERITY_MAJOR,
                category="Over-Engineering",
                file=str(file_path.relative_to(self.project_root)),
                line=0,
                finding="Abstract Base Class found - verify you actually need it",
                recommendation="ABCs are only useful with 2+ implementations. YAGNI principle.",
                ai_pattern=True
            ))

        # Check for Factory pattern (often over-used by AI)
        if 'Factory' in content and 'create' in content.lower():
            reviews.append(CodeReview(
                severity=CodeReview.SEVERITY_MINOR,
                category="Over-Engineering",
                file=str(file_path.relative_to(self.project_root)),
                line=0,
                finding="Factory pattern detected - is it needed?",
                recommendation="Factory is often overkill. Simple function usually works.",
                ai_pattern=True
            ))

        # Check for excessive class hierarchy
        inheritance_count = content.count('class') + content.count('(ABC)')
        if inheritance_count > 5:
            reviews.append(CodeReview(
                severity=CodeReview.SEVERITY_MAJOR,
                category="Over-Engineering",
                file=str(file_path.relative_to(self.project_root)),
                line=0,
                finding=f"Many classes ({inheritance_count}) in one file - likely over-engineered",
                recommendation="Prefer composition over inheritance. Keep it simple.",
                ai_pattern=True
            ))

        return reviews

    def review_test_quality(self, file_path: Path, content: str, lines: List[str]) -> List[CodeReview]:
        """
        Review test files for quality issues.

        AI tests often:
        - Only test happy path
        - Have weak assertions (assert True, assert not None)
        - Don't test actual business logic
        - Have descriptive names but trivial checks
        """
        reviews = []

        if 'test_' not in str(file_path):
            return reviews

        # Check for weak assertions
        weak_assertions = ['assert True', 'assert not None', 'assert x']
        for i, line in enumerate(lines, start=1):
            for weak in weak_assertions:
                if weak in line:
                    reviews.append(CodeReview(
                        severity=CodeReview.SEVERITY_MAJOR,
                        category="Test Quality",
                        file=str(file_path.relative_to(self.project_root)),
                        line=i,
                        finding=f"Weak assertion: '{weak}' - tests nothing meaningful",
                        recommendation="Assert specific values/behavior, not just 'not None'",
                        ai_pattern=True
                    ))

        # Check if file only tests happy path (no 'raise', 'except', 'error' in test names)
        test_names = [line for line in lines if 'def test_' in line]
        error_tests = [t for t in test_names if 'error' in t.lower() or 'invalid' in t.lower() or 'fail' in t.lower()]

        if test_names and len(error_tests) < len(test_names) * 0.3:
            reviews.append(CodeReview(
                severity=CodeReview.SEVERITY_CRITICAL,
                category="Test Quality",
                file=str(file_path.relative_to(self.project_root)),
                line=0,
                finding=f"Only {len(error_tests)}/{len(test_names)} tests check error cases - happy path bias",
                recommendation="Test unhappy paths: invalid input, edge cases, errors",
                ai_pattern=True
            ))

        return reviews

    def review_security_oversights(self, file_path: Path, content: str, lines: List[str]) -> List[CodeReview]:
        """
        Check for security issues AI might introduce.

        AI security blindspots:
        - Validates format but not semantics
        - Uses string operations on sensitive data
        - Logs sensitive information "for debugging"
        - Trusts deserialized data
        """
        reviews = []

        # Check for eval/exec (AI sometimes suggests these)
        dangerous_funcs = ['eval(', 'exec(', '__import__']
        for i, line in enumerate(lines, start=1):
            for func in dangerous_funcs:
                if func in line and not line.strip().startswith('#'):
                    reviews.append(CodeReview(
                        severity=CodeReview.SEVERITY_BLOCKER,
                        category="Security",
                        file=str(file_path.relative_to(self.project_root)),
                        line=i,
                        finding=f"Dangerous function '{func}' used - code injection risk",
                        recommendation="Never use eval/exec. Find alternative approach.",
                        ai_pattern=True
                    ))

        # Check for pickle (AI might suggest for "convenience")
        if 'pickle' in content.lower():
            reviews.append(CodeReview(
                severity=CodeReview.SEVERITY_CRITICAL,
                category="Security",
                file=str(file_path.relative_to(self.project_root)),
                line=0,
                finding="pickle module used - arbitrary code execution risk",
                recommendation="Use json or msgpack instead. Never unpickle untrusted data.",
                ai_pattern=True
            ))

        # Check for hardcoded credentials (even in "examples")
        cred_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
        ]

        for i, line in enumerate(lines, start=1):
            for pattern in cred_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if 'getenv' not in line and 'example' not in line.lower():
                        reviews.append(CodeReview(
                            severity=CodeReview.SEVERITY_BLOCKER,
                            category="Security",
                            file=str(file_path.relative_to(self.project_root)),
                            line=i,
                            finding="Hardcoded credential detected",
                            recommendation="Use environment variables or secret management",
                            ai_pattern=True
                        ))

        return reviews

    def review_file(self, file_path: Path) -> List[CodeReview]:
        """Run all reviews on a single file."""
        reviews = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            self.log(f"Reviewing {file_path.relative_to(self.project_root)}", "REVIEW")

            reviews.extend(self.review_ai_antipatterns(file_path, content, lines))
            reviews.extend(self.review_over_engineering(file_path, content, lines))
            reviews.extend(self.review_test_quality(file_path, content, lines))
            reviews.extend(self.review_security_oversights(file_path, content, lines))

        except Exception as e:
            self.log(f"Error reviewing {file_path}: {e}", "CONCERN")

        return reviews

    def review_project_structure(self) -> List[CodeReview]:
        """Review overall project architecture and structure."""
        reviews = []

        src_dir = self.project_root / 'src'

        # Check for circular dependencies (AI often creates these)
        # This is simplified - real check needs import graph analysis

        # Check for missing __init__.py files
        python_dirs = [d for d in src_dir.rglob('*') if d.is_dir() and any(d.glob('*.py'))]
        for dir_path in python_dirs:
            init_file = dir_path / '__init__.py'
            if not init_file.exists() and dir_path.name != '__pycache__':
                reviews.append(CodeReview(
                    severity=CodeReview.SEVERITY_MINOR,
                    category="Project Structure",
                    file=str(dir_path.relative_to(self.project_root)),
                    line=0,
                    finding=f"Missing __init__.py in {dir_path.name}",
                    recommendation="Add __init__.py to make it a proper Python package",
                    ai_pattern=False
                ))

        # Check for duplicate code (AI often copy-pastes instead of abstracting)
        # This would need more sophisticated analysis

        return reviews

    def review_documentation(self) -> List[CodeReview]:
        """Review documentation quality."""
        reviews = []

        # Check README
        readme = self.project_root / 'README.md'
        if readme.exists():
            with open(readme, 'r', encoding='utf-8') as f:
                content = f.read()

            # AI often generates READMEs with lots of emojis and fluff
            if content.count('🚀') + content.count('✨') + content.count('🎉') > 5:
                reviews.append(CodeReview(
                    severity=CodeReview.SEVERITY_NITPICK,
                    category="Documentation",
                    file="README.md",
                    line=0,
                    finding="Excessive emojis in README - typical AI-generated doc",
                    recommendation="Emojis are fine, but content matters more than decoration",
                    ai_pattern=True
                ))

            # Check if README actually explains the project
            required_sections = ['install', 'usage', 'contribute']
            missing = [s for s in required_sections if s not in content.lower()]
            if missing:
                reviews.append(CodeReview(
                    severity=CodeReview.SEVERITY_MAJOR,
                    category="Documentation",
                    file="README.md",
                    line=0,
                    finding=f"README missing sections: {', '.join(missing)}",
                    recommendation="Add practical getting-started information",
                    ai_pattern=True
                ))

        return reviews

    def run_code_review(self) -> Dict[str, int]:
        """Review all code in the project."""
        print("\n" + "="*60)
        print("SKEPTICAL SENIOR DEV - Code Review")
        print("="*60 + "\n")

        self.log("Running comprehensive code review...")
        self.log("Specifically looking for AI coding antipatterns...")

        # Review all Python files
        src_dir = self.project_root / 'src'
        test_dir = self.project_root / 'tests'

        for py_file in src_dir.glob('**/*.py'):
            file_reviews = self.review_file(py_file)
            self.reviews.extend(file_reviews)

        for py_file in test_dir.glob('**/*.py'):
            file_reviews = self.review_file(py_file)
            self.reviews.extend(file_reviews)

        # Review project structure
        struct_reviews = self.review_project_structure()
        self.reviews.extend(struct_reviews)

        # Review documentation
        doc_reviews = self.review_documentation()
        self.reviews.extend(doc_reviews)

        # Generate report
        self.generate_review_report()

        return {
            'blocker': sum(1 for r in self.reviews if r.severity == CodeReview.SEVERITY_BLOCKER),
            'critical': sum(1 for r in self.reviews if r.severity == CodeReview.SEVERITY_CRITICAL),
            'major': sum(1 for r in self.reviews if r.severity == CodeReview.SEVERITY_MAJOR),
            'minor': sum(1 for r in self.reviews if r.severity == CodeReview.SEVERITY_MINOR),
            'nitpick': sum(1 for r in self.reviews if r.severity == CodeReview.SEVERITY_NITPICK),
        }

    def generate_review_report(self):
        """Generate detailed review report."""
        print("\n" + "="*60)
        print("CODE REVIEW RESULTS")
        print("="*60 + "\n")

        # Summary
        by_severity = {
            CodeReview.SEVERITY_BLOCKER: [],
            CodeReview.SEVERITY_CRITICAL: [],
            CodeReview.SEVERITY_MAJOR: [],
            CodeReview.SEVERITY_MINOR: [],
            CodeReview.SEVERITY_NITPICK: []
        }

        ai_patterns = [r for r in self.reviews if r.ai_pattern]

        for review in self.reviews:
            by_severity[review.severity].append(review)

        print("SUMMARY:")
        print(f"  [BLOCK] Blocker:  {len(by_severity[CodeReview.SEVERITY_BLOCKER])}")
        print(f"  [CRIT]  Critical: {len(by_severity[CodeReview.SEVERITY_CRITICAL])}")
        print(f"  [MAJOR] Major:    {len(by_severity[CodeReview.SEVERITY_MAJOR])}")
        print(f"  [MINOR] Minor:    {len(by_severity[CodeReview.SEVERITY_MINOR])}")
        print(f"  [NITS]  Nitpick:  {len(by_severity[CodeReview.SEVERITY_NITPICK])}")
        print(f"  [AI]    AI Antipatterns: {len(ai_patterns)}\n")

        # Show blockers and critical first
        for severity in [CodeReview.SEVERITY_BLOCKER, CodeReview.SEVERITY_CRITICAL]:
            if by_severity[severity]:
                print(f"\n{severity} ISSUES:")
                print("-" * 60)
                for review in by_severity[severity]:
                    ai_flag = " [AI PATTERN]" if review.ai_pattern else ""
                    print(f"\n[{review.category}]{ai_flag} {review.file}:{review.line}")
                    print(f"  Finding: {review.finding}")
                    print(f"  Fix: {review.recommendation}")

        # Detailed AI pattern analysis
        if ai_patterns:
            print("\n" + "="*60)
            print("AI CODING ANTIPATTERNS DETECTED")
            print("="*60 + "\n")
            print("These patterns are common in AI-generated code and should be reviewed:\n")

            ai_by_category = {}
            for pattern in ai_patterns:
                if pattern.category not in ai_by_category:
                    ai_by_category[pattern.category] = []
                ai_by_category[pattern.category].append(pattern)

            for category, patterns in ai_by_category.items():
                print(f"\n{category}: {len(patterns)} instances")
                for p in patterns[:3]:  # Show first 3 examples
                    print(f"  - {p.file}:{p.line} - {p.finding}")

        # Overall assessment
        print("\n" + "="*60)
        print("OVERALL ASSESSMENT")
        print("="*60 + "\n")

        blocker_count = len(by_severity[CodeReview.SEVERITY_BLOCKER])
        critical_count = len(by_severity[CodeReview.SEVERITY_CRITICAL])

        if blocker_count > 0:
            print("[BLOCK] CANNOT SHIP - Blocker issues must be fixed")
        elif critical_count > 5:
            print("[CRIT] HIGH RISK - Too many critical issues")
        elif critical_count > 0:
            print("[!] NEEDS WORK - Address critical issues before release")
        elif len(by_severity[CodeReview.SEVERITY_MAJOR]) > 10:
            print("[!] TECHNICAL DEBT - Many issues to address")
        else:
            print("[OK] LOOKS REASONABLE - Minor issues, but shippable")

        if len(ai_patterns) > 10:
            print("\n[AI] WARNING: High number of AI antipatterns detected")
            print("     Recommend manual review by human developer")

        print("\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Skeptical Senior Dev Code Review Agent")
    parser.add_argument('--review', choices=['code', 'architecture', 'process', 'all'],
                       default='all', help='Type of review to perform')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    agent = SkepticalSeniorDevAgent(verbose=args.verbose)
    stats = agent.run_code_review()

    # Exit with error if blockers or critical issues found
    exit_code = 0 if (stats['blocker'] + stats['critical']) == 0 else 1
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
