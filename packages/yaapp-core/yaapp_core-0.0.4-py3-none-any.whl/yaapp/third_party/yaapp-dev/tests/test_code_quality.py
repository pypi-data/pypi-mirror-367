"""
Code quality tests for yaapp project.

This module contains tests that verify code quality standards including:
- PEP 8 compliance (flake8)
- Code formatting (black)
- Import sorting (isort)
- Type checking (mypy)
- Static analysis (yaapp custom rules)
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestCodeQuality:
    """Test suite for code quality standards."""

    @pytest.fixture(scope="class")
    def project_root(self):
        """Get the project root directory."""
        return Path(__file__).parent.parent

    def test_flake8_src_compliance(self, project_root):
        """Test that src/ directory complies with PEP 8 via flake8."""
        src_dir = project_root / "src"
        if not src_dir.exists():
            pytest.skip("src/ directory not found")

        result = subprocess.run(
            [sys.executable, "-m", "flake8", str(src_dir)],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode != 0:
            pytest.fail(
                f"flake8 found PEP 8 violations in src/:\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}\n"
                f"Fix these issues or configure flake8 exceptions in setup.cfg"
            )

    def test_flake8_tests_compliance(self, project_root):
        """Test that tests/ directory complies with PEP 8 via flake8."""
        tests_dir = project_root / "tests"
        if not tests_dir.exists():
            pytest.skip("tests/ directory not found")

        result = subprocess.run(
            [sys.executable, "-m", "flake8", str(tests_dir)],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode != 0:
            pytest.fail(
                f"flake8 found PEP 8 violations in tests/:\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}\n"
                f"Fix these issues or configure flake8 exceptions in setup.cfg"
            )

    def test_black_formatting_src(self, project_root):
        """Test that src/ directory is properly formatted with black."""
        src_dir = project_root / "src"
        if not src_dir.exists():
            pytest.skip("src/ directory not found")

        result = subprocess.run(
            [sys.executable, "-m", "black", "--check", "--diff", str(src_dir)],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode != 0:
            pytest.fail(
                f"black found formatting issues in src/:\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}\n"
                f"Run 'black src/' to fix formatting issues"
            )

    def test_black_formatting_tests(self, project_root):
        """Test that tests/ directory is properly formatted with black."""
        tests_dir = project_root / "tests"
        if not tests_dir.exists():
            pytest.skip("tests/ directory not found")

        result = subprocess.run(
            [sys.executable, "-m", "black", "--check", "--diff", str(tests_dir)],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode != 0:
            pytest.fail(
                f"black found formatting issues in tests/:\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}\n"
                f"Run 'black tests/' to fix formatting issues"
            )

    def test_isort_imports_src(self, project_root):
        """Test that src/ directory has properly sorted imports."""
        src_dir = project_root / "src"
        if not src_dir.exists():
            pytest.skip("src/ directory not found")

        result = subprocess.run(
            [sys.executable, "-m", "isort", "--check-only", "--diff", str(src_dir)],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode != 0:
            pytest.fail(
                f"isort found import sorting issues in src/:\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}\n"
                f"Run 'isort src/' to fix import sorting"
            )

    def test_isort_imports_tests(self, project_root):
        """Test that tests/ directory has properly sorted imports."""
        tests_dir = project_root / "tests"
        if not tests_dir.exists():
            pytest.skip("tests/ directory not found")

        result = subprocess.run(
            [sys.executable, "-m", "isort", "--check-only", "--diff", str(tests_dir)],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode != 0:
            pytest.fail(
                f"isort found import sorting issues in tests/:\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}\n"
                f"Run 'isort tests/' to fix import sorting"
            )

    def test_mypy_type_checking_src(self, project_root):
        """Test that src/ directory passes mypy type checking."""
        src_dir = project_root / "src"
        if not src_dir.exists():
            pytest.skip("src/ directory not found")

        result = subprocess.run(
            [sys.executable, "-m", "mypy", str(src_dir)],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode != 0:
            pytest.fail(
                f"mypy found type checking issues in src/:\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}\n"
                f"Fix type annotations or configure mypy exceptions in setup.cfg"
            )

    def test_yaapp_static_analysis(self, project_root):
        """Test that yaapp static analysis passes with zero critical violations."""
        static_analysis_tool = project_root / "tools" / "run_static_analysis.py"
        if not static_analysis_tool.exists():
            pytest.skip("YApp static analysis tool not found")

        result = subprocess.run(
            [sys.executable, str(static_analysis_tool), "--fail-on-violations"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode != 0:
            pytest.fail(
                f"YApp static analysis found critical violations:\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}\n"
                f"Fix critical violations before merging"
            )


class TestCodeQualityTools:
    """Test that required code quality tools are available."""

    def test_flake8_available(self):
        """Test that flake8 is installed and available."""
        result = subprocess.run(
            [sys.executable, "-m", "flake8", "--version"],
            capture_output=True,
            text=True,
        )
        assert (
            result.returncode == 0
        ), "flake8 is not installed. Run: pip install flake8"

    def test_black_available(self):
        """Test that black is installed and available."""
        result = subprocess.run(
            [sys.executable, "-m", "black", "--version"], capture_output=True, text=True
        )
        assert result.returncode == 0, "black is not installed. Run: pip install black"

    def test_isort_available(self):
        """Test that isort is installed and available."""
        result = subprocess.run(
            [sys.executable, "-m", "isort", "--version"], capture_output=True, text=True
        )
        assert result.returncode == 0, "isort is not installed. Run: pip install isort"

    def test_mypy_available(self):
        """Test that mypy is installed and available."""
        result = subprocess.run(
            [sys.executable, "-m", "mypy", "--version"], capture_output=True, text=True
        )
        assert result.returncode == 0, "mypy is not installed. Run: pip install mypy"


def test_code_quality_comprehensive():
    """Comprehensive code quality test that can be run standalone."""
    project_root = Path(__file__).parent.parent

    print("\n🔍 Running comprehensive code quality checks...")

    # Check if tools are available
    tools = ["flake8", "black", "isort", "mypy"]
    missing_tools = []

    for tool in tools:
        result = subprocess.run(
            [sys.executable, "-m", tool, "--version"], capture_output=True, text=True
        )
        if result.returncode != 0:
            missing_tools.append(tool)

    if missing_tools:
        print(f"❌ Missing tools: {', '.join(missing_tools)}")
        print(f"Install with: pip install {' '.join(missing_tools)}")
        return False

    # Run checks
    checks = [
        ("flake8 src", ["flake8", "src"]),
        ("flake8 tests", ["flake8", "tests"]),
        ("black src", ["black", "--check", "src"]),
        ("black tests", ["black", "--check", "tests"]),
        ("isort src", ["isort", "--check-only", "src"]),
        ("isort tests", ["isort", "--check-only", "tests"]),
        ("mypy src", ["mypy", "src"]),
    ]

    all_passed = True

    for check_name, cmd in checks:
        print(f"  Running {check_name}...")
        result = subprocess.run(
            [sys.executable, "-m"] + cmd,
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode == 0:
            print(f"  ✅ {check_name} passed")
        else:
            print(f"  ❌ {check_name} failed")
            if result.stdout:
                print(f"     STDOUT: {result.stdout}")
            if result.stderr:
                print(f"     STDERR: {result.stderr}")
            all_passed = False

    # Run yaapp static analysis
    static_analysis_tool = project_root / "tools" / "run_static_analysis.py"
    if static_analysis_tool.exists():
        print("  Running yaapp static analysis...")
        result = subprocess.run(
            [sys.executable, str(static_analysis_tool), "--fail-on-violations"],
            capture_output=True,
            text=True,
            cwd=project_root,
        )

        if result.returncode == 0:
            print("  ✅ yaapp static analysis passed")
        else:
            print("  ❌ yaapp static analysis failed")
            if result.stdout:
                print(f"     STDOUT: {result.stdout}")
            if result.stderr:
                print(f"     STDERR: {result.stderr}")
            all_passed = False
    else:
        print("  ⚠️  yaapp static analysis tool not found")

    if all_passed:
        print("\n🎉 All code quality checks passed!")
    else:
        print("\n💥 Some code quality checks failed. Please fix the issues above.")

    return all_passed


if __name__ == "__main__":
    # Run comprehensive test when executed directly
    success = test_code_quality_comprehensive()
    sys.exit(0 if success else 1)
