#!/usr/bin/env python3
"""
The Number - Simple Budget App

A gamified daily budgeting tool that calculates how much you can spend each day.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli import CLI
from src.utils import configure_console_encoding, check_database_health, ensure_env_file


def main():
    """Main entry point for The Number app."""
    # Configure console for cross-platform compatibility
    configure_console_encoding()

    # Ensure .env file exists
    ensure_env_file()

    # Load environment variables
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)

    # Validate database health before starting
    check_database_health()

    # Start CLI
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
