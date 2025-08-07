#!/usr/bin/env python3
"""
Git Storage Test Runner

Run Git storage tests with proper configuration and reporting.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run Git storage tests."""
    
    # Base pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Test directory
    test_dir = Path(__file__).parent
    
    # Add test selection
    if test_type == "unit":
        cmd.append(str(test_dir / "test_git_backend.py"))
    elif test_type == "integration":
        cmd.append(str(test_dir / "test_integration.py"))
    elif test_type == "performance":
        cmd.append(str(test_dir / "test_performance.py"))
    elif test_type == "fast":
        cmd.extend([str(test_dir), "-m", "not slow"])
    else:  # all
        cmd.append(str(test_dir))
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage
    if coverage:
        cmd.extend([
            "--cov=yaapp.plugins.storage.git",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    
    # Add other useful options
    cmd.extend([
        "--tb=short",  # Shorter traceback format
        "--strict-markers",  # Strict marker checking
        "-ra",  # Show all test results
    ])
    
    print(f"Running command: {' '.join(cmd)}")
    print("=" * 60)
    
    try:
        result = subprocess.run(cmd, cwd=test_dir.parent.parent.parent.parent)
        return result.returncode
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        return 130
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run Git storage tests")
    
    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration", "performance", "fast"],
        help="Type of tests to run (default: all)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )
    
    args = parser.parse_args()
    
    print("🧪 Git Storage Test Runner")
    print("=" * 60)
    print(f"Test type: {args.test_type}")
    print(f"Verbose: {args.verbose}")
    print(f"Coverage: {args.coverage}")
    print()
    
    # Check if Git is available
    try:
        subprocess.run(
            ["git", "--version"],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Git is not available - cannot run Git storage tests")
        return 1
    
    # Run tests
    exit_code = run_tests(args.test_type, args.verbose, args.coverage)
    
    if exit_code == 0:
        print("\n🎉 All tests passed!")
        
        if args.test_type == "all":
            print("\n✅ Test Coverage:")
            print("   • Unit tests: Core functionality")
            print("   • Integration tests: YAAPP integration")
            print("   • Performance tests: Speed and efficiency")
            
        if args.coverage:
            print("\n📊 Coverage report generated in htmlcov/")
            
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")
        
        if args.test_type == "performance":
            print("\n💡 Performance test tips:")
            print("   • Performance tests may be sensitive to system load")
            print("   • Run on a quiet system for consistent results")
            print("   • Adjust performance thresholds if needed")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())