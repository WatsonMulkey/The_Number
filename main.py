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


def main():
    """Main entry point for The Number app."""
    # Load environment variables
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    else:
        print("\n⚠️  Warning: No .env file found.")
        print("Creating .env file with new encryption key...\n")

        # Generate new encryption key
        from cryptography.fernet import Fernet
        key = Fernet.generate_key().decode()

        # Create .env file
        with open(env_path, 'w') as f:
            f.write(f"DB_ENCRYPTION_KEY={key}\n")

        # Load the new .env file
        load_dotenv(env_path)

        print("✅ Created .env file with encryption key.\n")

    # Start CLI
    cli = CLI()
    cli.run()


if __name__ == "__main__":
    main()
