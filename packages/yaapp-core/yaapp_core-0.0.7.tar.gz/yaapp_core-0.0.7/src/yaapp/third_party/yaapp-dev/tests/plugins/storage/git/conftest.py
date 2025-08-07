"""
Pytest configuration for Git storage tests.
"""

import pytest
import subprocess
import shutil


def pytest_configure(config):
    """Configure pytest for Git storage tests."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


@pytest.fixture(scope="session", autouse=True)
def check_git_available():
    """Check if Git is available for testing."""
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"Git version: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        pytest.skip("Git is not available - skipping Git storage tests")


@pytest.fixture(scope="session")
def git_config():
    """Configure Git for testing if needed."""
    try:
        # Check if Git is configured
        subprocess.run(
            ["git", "config", "--global", "user.name"],
            capture_output=True,
            check=True
        )
        subprocess.run(
            ["git", "config", "--global", "user.email"],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError:
        # Configure Git for testing
        subprocess.run(
            ["git", "config", "--global", "user.name", "Test User"],
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "--global", "user.email", "test@example.com"],
            capture_output=True
        )


@pytest.fixture
def clean_git_config(git_config):
    """Ensure clean Git configuration for each test."""
    # This fixture ensures git_config is applied
    # and provides a clean state for each test
    yield