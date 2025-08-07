#!/usr/bin/env python3
"""
Simple script to help publish ychatty to PyPI.

Usage:
    python publish.py --test    # Publish to TestPyPI
    python publish.py          # Publish to PyPI
"""

import subprocess
import sys
import argparse
from pathlib import Path


def run_command(cmd, check=True):
    """Run a command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def main():
    parser = argparse.ArgumentParser(description="Publish ychatty to PyPI")
    parser.add_argument("--test", action="store_true", help="Publish to TestPyPI instead of PyPI")
    parser.add_argument("--skip-build", action="store_true", help="Skip building the package")
    args = parser.parse_args()
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("Error: pyproject.toml not found. Run this script from the ychatty directory.")
        sys.exit(1)
    
    # Build the package
    if not args.skip_build:
        print("🔨 Building the package...")
        try:
            run_command(["uv", "build"])
        except subprocess.CalledProcessError:
            print("❌ Build failed!")
            sys.exit(1)
        print("✅ Build successful!")
    
    # Check if twine is available
    try:
        run_command(["python", "-m", "twine", "--version"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 Installing twine...")
        try:
            run_command(["uv", "add", "--dev", "twine"])
        except subprocess.CalledProcessError:
            print("❌ Failed to install twine!")
            sys.exit(1)
    
    # Upload to PyPI
    if args.test:
        print("🚀 Uploading to TestPyPI...")
        repository_url = "https://test.pypi.org/legacy/"
        print("📝 You'll need your TestPyPI credentials.")
        print("   Create an account at: https://test.pypi.org/account/register/")
        print("   Get an API token at: https://test.pypi.org/manage/account/token/")
    else:
        print("🚀 Uploading to PyPI...")
        repository_url = "https://upload.pypi.org/legacy/"
        print("📝 You'll need your PyPI credentials.")
        print("   Create an account at: https://pypi.org/account/register/")
        print("   Get an API token at: https://pypi.org/manage/account/token/")
    
    print("\\n💡 Tip: Use '__token__' as username and your API token as password")
    print()
    
    try:
        if args.test:
            run_command([
                "python", "-m", "twine", "upload", 
                "--repository-url", repository_url,
                "dist/*"
            ])
        else:
            run_command(["python", "-m", "twine", "upload", "dist/*"])
        
        if args.test:
            print("🎉 Successfully uploaded to TestPyPI!")
            print("🔗 Check it out at: https://test.pypi.org/project/ychatty/")
            print("📦 Install with: pip install -i https://test.pypi.org/simple/ ychatty")
        else:
            print("🎉 Successfully uploaded to PyPI!")
            print("🔗 Check it out at: https://pypi.org/project/ychatty/")
            print("📦 Install with: pip install ychatty")
            
    except subprocess.CalledProcessError:
        print("❌ Upload failed!")
        print("💡 Common issues:")
        print("   - Package version already exists (bump version in pyproject.toml)")
        print("   - Invalid credentials")
        print("   - Network issues")
        sys.exit(1)


if __name__ == "__main__":
    main()