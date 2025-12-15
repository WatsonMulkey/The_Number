#!/usr/bin/env python3
"""
Performance Profiler Agent for The Number App

This agent analyzes performance characteristics of the app, identifies bottlenecks,
and provides recommendations for optimization.

Usage:
    python agents/performance_profiler.py [--benchmark all|calculator|database|import] [--iterations N]
"""

import sys
import os
import time
import statistics
from pathlib import Path
from typing import Dict, List, Tuple, Callable
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from calculator import BudgetCalculator, Expense, Transaction
from database import BudgetDatabase


class PerformanceBenchmark:
    """Represents a performance benchmark result."""

    def __init__(self, name: str, iterations: int, times: List[float]):
        self.name = name
        self.iterations = iterations
        self.times = times
        self.mean = statistics.mean(times)
        self.median = statistics.median(times)
        self.stdev = statistics.stdev(times) if len(times) > 1 else 0
        self.min = min(times)
        self.max = max(times)

    def __repr__(self):
        return f"{self.name}: {self.mean*1000:.2f}ms avg ({self.iterations} iterations)"


class PerformanceProfilerAgent:
    """Agent that profiles and benchmarks application performance."""

    def __init__(self, iterations: int = 100, verbose: bool = False):
        self.iterations = iterations
        self.verbose = verbose
        self.benchmarks: List[PerformanceBenchmark] = []

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled."""
        if self.verbose:
            prefix = {
                "INFO": "[*]",
                "BENCH": "[>]",
                "RESULT": "[+]"
            }.get(level, "[?]")
            print(f"{prefix} {message}")

    def time_function(self, func: Callable, iterations: int = None) -> List[float]:
        """Time a function over multiple iterations."""
        if iterations is None:
            iterations = self.iterations

        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append(end - start)

        return times

    def benchmark(self, name: str, func: Callable, iterations: int = None) -> PerformanceBenchmark:
        """Run a benchmark and record results."""
        if iterations is None:
            iterations = self.iterations

        self.log(f"Benchmarking: {name} ({iterations} iterations)", "BENCH")

        times = self.time_function(func, iterations)
        result = PerformanceBenchmark(name, iterations, times)

        self.benchmarks.append(result)
        self.log(f"Result: {result.mean*1000:.2f}ms average", "RESULT")

        return result

    # ===== CALCULATOR BENCHMARKS =====

    def bench_calculator_simple(self):
        """Benchmark simple budget calculation."""
        def run():
            calc = BudgetCalculator()
            calc.add_expense("Rent", 1500.0,True)
            calc.add_expense("Groceries", 500.0,False)
            calc.calculate_paycheck_mode(3000.0, 15)

        return self.benchmark("Calculator: Simple Paycheck Mode", run)

    def bench_calculator_complex(self):
        """Benchmark complex budget with many expenses."""
        def run():
            calc = BudgetCalculator()
            # Add 20 expenses
            for i in range(20):
                calc.add_expense(f"Expense {i}", 100.0 + i,i % 2 == 0)
            calc.calculate_paycheck_mode(5000.0, 30)

        return self.benchmark("Calculator: Complex Budget (20 expenses)", run)

    def bench_calculator_fixed_pool(self):
        """Benchmark fixed pool mode calculation."""
        def run():
            calc = BudgetCalculator()
            calc.add_expense("Monthly Expenses", 2500.0,True)
            calc.calculate_fixed_pool_mode(15000.0)

        return self.benchmark("Calculator: Fixed Pool Mode", run)

    def bench_calculator_get_number(self):
        """Benchmark getting The Number."""
        calc = BudgetCalculator()
        calc.add_expense("Rent", 1500.0,True)

        def run():
            calc.get_number(mode="paycheck", monthly_income=3000.0, days_until_paycheck=15)

        return self.benchmark("Calculator: Get The Number", run)

    # ===== DATABASE BENCHMARKS =====

    def bench_database_insert_expense(self):
        """Benchmark inserting expenses."""
        import tempfile

        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db = BudgetDatabase(temp_db.name, encryption_key=b'test_key_1234567890123456789012')

        def run():
            db.add_expense("Test Expense", 100.0, True)

        result = self.benchmark("Database: Insert Expense", run, iterations=50)

        # Cleanup
        temp_db.close()
        os.unlink(temp_db.name)

        return result

    def bench_database_query_expenses(self):
        """Benchmark querying expenses."""
        import tempfile

        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db = BudgetDatabase(temp_db.name, encryption_key=b'test_key_1234567890123456789012')

        # Insert test data
        for i in range(50):
            db.add_expense(f"Expense {i}", 100.0 + i, i % 2 == 0)

        def run():
            db.get_expenses()

        result = self.benchmark("Database: Query 50 Expenses", run)

        # Cleanup
        temp_db.close()
        os.unlink(temp_db.name)

        return result

    def bench_database_insert_transaction(self):
        """Benchmark inserting transactions."""
        import tempfile

        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db = BudgetDatabase(temp_db.name, encryption_key=b'test_key_1234567890123456789012')

        def run():
            db.add_transaction(50.0, "Test transaction")

        result = self.benchmark("Database: Insert Transaction", run, iterations=50)

        # Cleanup
        temp_db.close()
        os.unlink(temp_db.name)

        return result

    def bench_database_query_transactions(self):
        """Benchmark querying transactions."""
        import tempfile

        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db = BudgetDatabase(temp_db.name, encryption_key=b'test_key_1234567890123456789012')

        # Insert test data
        for i in range(100):
            db.add_transaction(25.0 + i, f"Transaction {i}")

        def run():
            db.get_transactions(limit=100)

        result = self.benchmark("Database: Query 100 Transactions", run)

        # Cleanup
        temp_db.close()
        os.unlink(temp_db.name)

        return result

    # ===== IMPORT BENCHMARKS =====

    def bench_import_csv(self):
        """Benchmark CSV import."""
        import tempfile
        from import_expenses import parse_csv_expenses

        # Create test CSV
        temp_csv = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        temp_csv.write("name,amount,is_fixed\n")
        for i in range(50):
            temp_csv.write(f"Expense {i},{100 + i},yes\n")
        temp_csv.close()

        def run():
            parse_csv_expenses(temp_csv.name)

        result = self.benchmark("Import: Parse CSV (50 rows)", run, iterations=20)

        # Cleanup
        os.unlink(temp_csv.name)

        return result

    # ===== MEMORY BENCHMARKS =====

    def bench_memory_usage(self):
        """Benchmark memory usage of core operations."""
        import tracemalloc

        print("\n[*] Memory Usage Analysis:")

        # Calculator memory
        tracemalloc.start()
        calc = BudgetCalculator()
        for i in range(100):
            calc.add_expense(f"Expense {i}", 100.0,True)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"  Calculator (100 expenses): {peak / 1024:.2f} KB peak")

        # Database memory
        import tempfile
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')

        tracemalloc.start()
        db = BudgetDatabase(temp_db.name, encryption_key=b'test_key_1234567890123456789012')
        for i in range(100):
            db.add_expense(f"Expense {i}", 100.0, True)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"  Database (100 inserts):    {peak / 1024:.2f} KB peak")

        # Cleanup
        temp_db.close()
        os.unlink(temp_db.name)

    # ===== RUN BENCHMARKS =====

    def run_benchmarks(self, category: str = "all") -> Dict[str, PerformanceBenchmark]:
        """Run all benchmarks and generate report."""
        print("\n" + "="*60)
        print("PERFORMANCE PROFILER AGENT - Benchmarking")
        print("="*60 + "\n")
        print(f"Iterations per benchmark: {self.iterations}\n")

        if category in ["all", "calculator"]:
            print("[*] Benchmarking Calculator...")
            self.bench_calculator_simple()
            self.bench_calculator_complex()
            self.bench_calculator_fixed_pool()
            self.bench_calculator_get_number()

        if category in ["all", "database"]:
            print("\n[*] Benchmarking Database...")
            self.bench_database_insert_expense()
            self.bench_database_query_expenses()
            self.bench_database_insert_transaction()
            self.bench_database_query_transactions()

        if category in ["all", "import"]:
            print("\n[*] Benchmarking Import...")
            self.bench_import_csv()

        if category == "all":
            print("\n[*] Analyzing Memory Usage...")
            self.bench_memory_usage()

        # Generate report
        self.generate_report()

        return {b.name: b for b in self.benchmarks}

    def generate_report(self):
        """Generate performance report."""
        print("\n" + "="*60)
        print("PERFORMANCE REPORT")
        print("="*60 + "\n")

        # Sort by average time (slowest first)
        sorted_benchmarks = sorted(self.benchmarks, key=lambda b: b.mean, reverse=True)

        print(f"{'Benchmark':<45} {'Avg (ms)':<12} {'Med (ms)':<12} {'StdDev':<10}")
        print("-" * 80)

        for bench in sorted_benchmarks:
            avg_ms = bench.mean * 1000
            med_ms = bench.median * 1000
            std_ms = bench.stdev * 1000

            # Color code performance (for terminal)
            if avg_ms < 1:
                perf_indicator = "[EXCELLENT]"
            elif avg_ms < 10:
                perf_indicator = "[GOOD]"
            elif avg_ms < 50:
                perf_indicator = "[ACCEPTABLE]"
            else:
                perf_indicator = "[SLOW]"

            name = bench.name[:45]
            print(f"{name:<45} {avg_ms:<12.2f} {med_ms:<12.2f} {std_ms:<10.2f} {perf_indicator}")

        # Identify bottlenecks
        print("\n" + "="*60)
        print("BOTTLENECK ANALYSIS")
        print("="*60 + "\n")

        slowest = sorted_benchmarks[0]
        if slowest.mean > 0.05:  # > 50ms
            print(f"[!] SLOWEST: {slowest.name}")
            print(f"    Average: {slowest.mean*1000:.2f}ms")
            print(f"    Recommendation: Consider optimization\n")

        # Calculate total operation time
        total_time = sum(b.mean for b in self.benchmarks)
        print(f"Total benchmarked operation time: {total_time*1000:.2f}ms\n")

        # Recommendations
        print("RECOMMENDATIONS:")

        calculator_benches = [b for b in self.benchmarks if "Calculator" in b.name]
        if calculator_benches:
            avg_calc_time = statistics.mean(b.mean for b in calculator_benches)
            if avg_calc_time < 0.001:  # < 1ms
                print("  [+] Calculator performance is excellent")
            else:
                print("  [*] Calculator performance is acceptable")

        database_benches = [b for b in self.benchmarks if "Database" in b.name]
        if database_benches:
            avg_db_time = statistics.mean(b.mean for b in database_benches)
            if avg_db_time > 0.01:  # > 10ms
                print("  [-] Database operations could be optimized")
                print("      Consider: Connection pooling, batch inserts, indexes")
            else:
                print("  [+] Database performance is good")

        import_benches = [b for b in self.benchmarks if "Import" in b.name]
        if import_benches:
            avg_import_time = statistics.mean(b.mean for b in import_benches)
            if avg_import_time > 0.1:  # > 100ms
                print("  [-] Import operations are slow")
                print("      Consider: Streaming parsing, batch processing")
            else:
                print("  [+] Import performance is acceptable")

        print("\n" + "="*60 + "\n")


def main():
    """Main entry point for the performance profiler agent."""
    import argparse

    parser = argparse.ArgumentParser(description="Performance Profiler Agent for The Number App")
    parser.add_argument('--benchmark', choices=['all', 'calculator', 'database', 'import'],
                       default='all', help='Benchmark category to run')
    parser.add_argument('--iterations', type=int, default=100,
                       help='Number of iterations per benchmark (default: 100)')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    agent = PerformanceProfilerAgent(iterations=args.iterations, verbose=args.verbose)
    agent.run_benchmarks(category=args.benchmark)


if __name__ == "__main__":
    main()
