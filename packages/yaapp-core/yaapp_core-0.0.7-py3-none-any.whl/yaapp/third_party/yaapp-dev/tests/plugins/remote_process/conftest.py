"""
Pytest configuration and fixtures for RemoteProcess plugin tests.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

# Add src to path for testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_process():
    """Create a mock process for testing."""
    process = Mock()
    process.pid = 12345
    process.returncode = None
    process.terminate = Mock()
    process.kill = Mock()
    process.wait = Mock(return_value=0)
    return process


@pytest.fixture
def mock_pty():
    """Create mock PTY file descriptors."""
    with patch('yaapp.plugins.remote_process.plugin.pty.openpty') as mock_openpty:
        mock_openpty.return_value = (5, 6)  # master_fd, slave_fd
        yield mock_openpty


@pytest.fixture
def remote_process():
    """Create a RemoteProcess instance for testing."""
    from yaapp.plugins.remote_process.plugin import RemoteProcess
    return RemoteProcess()


@pytest.fixture
def yaapp_with_remote_process():
    """Create a YApp instance with RemoteProcess plugin exposed."""
    import yaapp
    from yaapp.plugins.remote_process.plugin import create_remote_process
    
    app = yaapp.YApp()
    remote_process = create_remote_process()
    app.expose(remote_process)
    return app, remote_process


@pytest.fixture
def mock_subprocess():
    """Mock asyncio.create_subprocess_exec."""
    with patch('yaapp.plugins.remote_process.plugin.asyncio.create_subprocess_exec') as mock:
        yield mock


@pytest.fixture
def mock_os_write():
    """Mock os.write for PTY operations."""
    with patch('yaapp.plugins.remote_process.plugin.os.write') as mock:
        yield mock


@pytest.fixture
def mock_os_read():
    """Mock os.read for PTY operations."""
    with patch('yaapp.plugins.remote_process.plugin.os.read') as mock:
        yield mock


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture
def mock_pty_reader():
    """Create a mock PTY reader with test data."""
    from yaapp.plugins.remote_process.plugin import PtyReader, OutputLine
    
    reader = PtyReader()
    
    # Add some test output lines
    test_lines = [
        "Welcome to test shell",
        "$ echo hello",
        "hello",
        "$ ls",
        "file1.txt  file2.txt",
        "$ "
    ]
    
    for line in test_lines:
        reader.add_output(line)
    
    return reader


@pytest.fixture
def streaming_test_data():
    """Provide test data for streaming tests."""
    return {
        "commands": ["echo hello", "ls -la", "pwd", "whoami"],
        "expected_outputs": [
            "hello",
            "total 0",
            "/tmp",
            "testuser"
        ],
        "sse_events": [
            "data: Successfully started subprocess: echo hello\n\n",
            "data: hello\n\n",
            "data: Process ended\n\n"
        ]
    }


@pytest.fixture
def http_client_mock():
    """Mock HTTP client for testing client interactions."""
    class MockHTTPClient:
        def __init__(self):
            self.responses = {}
            self.requests = []
        
        def set_response(self, url, response):
            self.responses[url] = response
        
        async def get(self, url, **kwargs):
            self.requests.append(("GET", url, kwargs))
            return self.responses.get(url, {"status": 200, "data": {}})
        
        async def post(self, url, **kwargs):
            self.requests.append(("POST", url, kwargs))
            return self.responses.get(url, {"status": 200, "data": {}})
    
    return MockHTTPClient()


@pytest.fixture
def fastapi_test_client():
    """Create a test client for FastAPI integration tests."""
    try:
        from fastapi.testclient import TestClient
        from yaapp.runners.fastapi_runner import FastAPIRunner
        
        def create_test_client(yaapp_instance):
            runner = FastAPIRunner(yaapp_instance.core)
            # Build the FastAPI app without starting the server
            runner._setup_fastapi_app()
            return TestClient(runner.fastapi_app)
        
        return create_test_client
    except ImportError:
        pytest.skip("FastAPI not available for testing")


@pytest.fixture
def streaming_fastapi_test_client():
    """Create a test client for streaming FastAPI integration tests."""
    try:
        from fastapi.testclient import TestClient
        from yaapp.runners.streaming_runner import StreamingFastAPIRunner
        
        def create_streaming_test_client(yaapp_instance):
            runner = StreamingFastAPIRunner(yaapp_instance.core)
            # Build the FastAPI app without starting the server
            runner._setup_fastapi_app()
            return TestClient(runner.fastapi_app)
        
        return create_streaming_test_client
    except ImportError:
        pytest.skip("FastAPI not available for streaming tests")


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "subprocess: mark test as requiring subprocess execution"
    )
    config.addinivalue_line(
        "markers", "network: mark test as requiring network access"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if "slow" in item.nodeid.lower() or "performance" in item.nodeid.lower():
            item.add_marker(pytest.mark.slow)
        
        # Mark subprocess tests
        if "subprocess" in item.nodeid.lower() or "process" in item.nodeid.lower():
            item.add_marker(pytest.mark.subprocess)
        
        # Mark network tests
        if "client" in item.nodeid.lower() or "http" in item.nodeid.lower():
            item.add_marker(pytest.mark.network)


# Async test configuration
@pytest.fixture(scope="session")
def event_loop_policy():
    """Set the event loop policy for the test session."""
    return asyncio.DefaultEventLoopPolicy()


# Skip conditions for different environments
def pytest_runtest_setup(item):
    """Setup function to skip tests based on environment."""
    # Skip subprocess tests in restricted environments
    if item.get_closest_marker("subprocess"):
        try:
            import subprocess
            subprocess.run(["echo", "test"], capture_output=True, timeout=1)
        except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError):
            pytest.skip("Subprocess execution not available in test environment")
    
    # Skip network tests if no network access
    if item.get_closest_marker("network"):
        try:
            import socket
            socket.create_connection(("8.8.8.8", 53), timeout=1)
        except (socket.timeout, socket.error):
            pytest.skip("Network access not available in test environment")


# Custom assertions
def assert_sse_format(data):
    """Assert that data is in proper SSE format."""
    assert isinstance(data, str)
    assert "data: " in data
    assert data.endswith("\n\n")


def assert_json_response(data):
    """Assert that data is a valid JSON response."""
    import json
    if isinstance(data, str):
        json.loads(data)  # Should not raise exception
    elif isinstance(data, dict):
        json.dumps(data)  # Should not raise exception
    else:
        raise AssertionError(f"Expected JSON-serializable data, got {type(data)}")


# Add custom assertions to pytest namespace
pytest.assert_sse_format = assert_sse_format
pytest.assert_json_response = assert_json_response