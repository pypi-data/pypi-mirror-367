#!/usr/bin/env python3
"""
Release script for yapp using uv
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Command: {cmd}")
        print(f"Error: {e.stderr}")
        sys.exit(1)


def main():
    """Main release process."""
    print("🚀 yapp Release Process")
    print("=" * 40)

    # Ensure we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ pyproject.toml not found. Run from project root.")
        sys.exit(1)

    # Run quality checks
    run_command("uv run ruff check src/ tests/", "Running linter")
    run_command("uv run black --check src/ tests/", "Checking code format")
    run_command("uv run mypy src/", "Running type checker")

    # Run tests
    run_command("uv run pytest", "Running tests")

    # Clean previous builds
    run_command("rm -rf dist/ build/ *.egg-info/", "Cleaning previous builds")

    # Build package
    run_command("uv build", "Building package")

    print("\n✅ Release preparation complete!")
    print("\nNext steps:")
    print("1. Review the built package in dist/")
    print("2. Test upload: make upload-test")
    print("3. Production upload: make upload")
    print("\nBuilt files:")

    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            print(f"  - {file.name}")


if __name__ == "__main__":
    main()
