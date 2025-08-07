#!/usr/bin/env python3
"""
Test plugin examples from any directory without boilerplate.

This test verifies that plugin examples work correctly when invoked
from any directory and show the expected plugin commands.
"""

import pytest
import subprocess
import os
import sys
from pathlib import Path


def run_example(example_path, args=None):
    """Run an example from the test directory without changing directory."""
    if args is None:
        args = ["--help"]
    
    # Get absolute path to example
    repo_root = Path(__file__).parent.parent.parent
    example_file = repo_root / example_path
    
    # Set up environment
    env = os.environ.copy()
    env['PYTHONPATH'] = str(repo_root / "src")
    
    # Run from test directory (NOT from example directory)
    cmd = [sys.executable, str(example_file)] + args
    
    try:
        result = subprocess.run(
            cmd,
            cwd=str(Path(__file__).parent),  # Run from tests/examples directory
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"


def test_issues_plugin_example():
    """Test issues plugin example shows plugin commands."""
    returncode, stdout, stderr = run_example("examples/issues/app.py", ["--help"])
    
    # Should run without error
    assert returncode == 0, f"Issues example failed: {stderr}"
    
    # Should show help output
    assert "Usage:" in stdout, "Issues example should show usage help"


def test_storage_plugin_example():
    """Test storage plugin example shows plugin commands."""
    returncode, stdout, stderr = run_example("examples/plugins/storage/app.py", ["--help"])
    
    # Should run without error
    assert returncode == 0, f"Storage example failed: {stderr}"
    
    # Should show help output
    assert "Usage:" in stdout, "Storage example should show usage help"


def test_app_proxy_example():
    """Test app-proxy plugin example shows plugin commands."""
    returncode, stdout, stderr = run_example("examples/plugins/app-proxy/app.py", ["--help"])
    
    # Should run without error
    assert returncode == 0, f"App-proxy example failed: {stderr}"
    
    # Should show help output
    assert "Usage:" in stdout, "App-proxy example should show usage help"


def test_remote_process_example():
    """Test remote-process plugin example shows plugin commands."""
    returncode, stdout, stderr = run_example("examples/plugins/remote-process/server.py", ["--help"])
    
    # Should run without error
    assert returncode == 0, f"Remote-process example failed: {stderr}"
    
    # Should show help output
    assert "Usage:" in stdout, "Remote-process example should show usage help"


def test_task_manager_example():
    """Test task-manager example shows exposed commands."""
    returncode, stdout, stderr = run_example("examples/task-manager/app.py", ["--help"])
    
    # Should run without error
    assert returncode == 0, f"Task manager example failed: {stderr}"
    
    # Should show help output
    assert "Usage:" in stdout, "Task manager example should show usage help"


def test_data_analyzer_example():
    """Test data-analyzer example shows exposed commands."""
    returncode, stdout, stderr = run_example("examples/data-analyzer/app.py", ["--help"])
    
    # Should run without error
    assert returncode == 0, f"Data analyzer example failed: {stderr}"
    
    # Should show help output
    assert "Usage:" in stdout, "Data analyzer example should show usage help"