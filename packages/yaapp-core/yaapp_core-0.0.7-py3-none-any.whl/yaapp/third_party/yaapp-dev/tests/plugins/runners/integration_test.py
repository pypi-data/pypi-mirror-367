#!/usr/bin/env python3
"""
Integration test for all yaapp runners.
Tests actual functionality without hanging.
"""

import sys
import os
import asyncio
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


def test_mcp_runner():
    """Test MCP runner functionality."""
    print("🔍 Testing MCP Runner...")
    
    try:
        from yaapp import Yaapp
        from yaapp.plugins.runners.mcp.plugin import Mcp
        
        # Create test app
        app = Yaapp(auto_discover=False)
        
        @app.expose
        def add(x: int, y: int) -> int:
            return x + y
        
        @app.expose
        class Calculator:
            def multiply(self, x: float, y: float) -> float:
                return x * y
        
        runner = Mcp()
        
        # Test tool generation
        with patch('yaapp.plugins.runners.mcp.plugin.yaapp._registry', app._registry):
            tools = runner._generate_mcp_tools_dict()
            assert len(tools) >= 1  # at least add function
            
            # Test simple tool execution
            async def test_execution():
                result = await runner._execute_tool("yaapp.add", {"x": 10, "y": 20})
                assert result == 30
            
            asyncio.run(test_execution())
        
        print("✅ MCP Runner: All tests passed")
        
    except Exception as e:
        print(f"MCP Runner error: {e}")
        import traceback
        traceback.print_exc()
        raise


def test_server_runner():
    """Test Server runner functionality."""
    print("🔍 Testing Server Runner...")
    
    from yaapp import Yaapp
    from yaapp.plugins.runners.server.plugin import ServerRunner as Server
    
    # Create test app
    app = Yaapp(auto_discover=False)
    
    @app.expose
    def greet(name: str) -> str:
        return f"Hello, {name}!"
    
    runner = Server()
    
    # Test command tree building
    with patch('yaapp.plugins.runners.server.plugin.yaapp._registry', app._registry):
        tree = runner._build_command_tree()
        assert 'greet' in tree
        assert tree['greet']['type'] == 'function'
        
        # Test function execution
        async def test_execution():
            result = await runner._call_function_async("greet", {"name": "World"})
            assert "Hello, World!" in result
        
        asyncio.run(test_execution())
    
    print("✅ Server Runner: All tests passed")


def test_gradio_runner():
    """Test Gradio runner functionality."""
    print("🔍 Testing Gradio Runner...")
    
    from yaapp import Yaapp
    from yaapp.plugins.runners.gradio.plugin import Gradio
    
    # Create test app
    app = Yaapp(auto_discover=False)
    
    @app.expose
    def subtract(x: int, y: int) -> int:
        return x - y
    
    runner = Gradio()
    
    # Test function execution
    with patch('yaapp.plugins.runners.gradio.plugin.yaapp._registry', app._registry):
        async def test_execution():
            result = await runner._call_function_async("subtract", {"x": 15, "y": 5})
            assert result == 10
        
        asyncio.run(test_execution())
    
    # Test example parameter generation
    import inspect
    def test_func(x: int, y: str, z: bool) -> str:
        return f"{x}: {y} ({z})"
    
    sig = inspect.signature(test_func)
    example = runner._generate_example_params(sig)
    
    import json
    parsed = json.loads(example)
    assert 'x' in parsed
    assert 'y' in parsed
    assert 'z' in parsed
    
    print("✅ Gradio Runner: All tests passed")


def test_streamlit_runner():
    """Test Streamlit runner functionality."""
    print("🔍 Testing Streamlit Runner...")
    
    from yaapp import Yaapp
    from yaapp.plugins.runners.streamlit.plugin import Streamlit
    
    # Create test app
    app = Yaapp(auto_discover=False)
    
    @app.expose
    def power(base: float, exp: float) -> float:
        return base ** exp
    
    runner = Streamlit()
    
    # Test app generation
    with patch('yaapp.plugins.runners.streamlit.plugin.yaapp._registry', app._registry):
        app_content = runner._generate_streamlit_app()
        
        assert 'import streamlit as st' in app_content
        assert 'FUNCTIONS_DATA' in app_content
        assert 'power' in app_content
        assert 'yaapp Streamlit Interface' in app_content
        
        # Test function execution
        async def test_execution():
            result = await runner._call_function_async("power", {"base": 2, "exp": 3})
            assert result == 8
        
        asyncio.run(test_execution())
    
    print("✅ Streamlit Runner: All tests passed")


def test_nicegui_runner():
    """Test NiceGUI runner (disabled)."""
    print("🔍 Testing NiceGUI Runner...")
    
    from yaapp import Yaapp
    from yaapp.plugins.runners.nicegui.plugin import NiceGUI
    
    app = Yaapp(auto_discover=False)
    runner = NiceGUI()
    
    # Test that it shows disabled message
    with patch('builtins.print') as mock_print:
        result = runner.run(app)
        assert result is None  # Should return early
        mock_print.assert_called()
        
        # Check that disabled message was printed
        calls = [str(call) for call in mock_print.call_args_list]
        disabled_mentioned = any("Disabled" in call for call in calls)
        assert disabled_mentioned
    
    print("✅ NiceGUI Runner: Correctly disabled with helpful message")


def test_runner_discovery():
    """Test runner discovery system."""
    print("🔍 Testing Runner Discovery...")
    
    from yaapp.discovery import PluginDiscovery
    
    discovery = PluginDiscovery()
    discovered_runners = discovery.discover_runners()
    
    # Should discover at least the main runners
    expected_runners = ['mcp', 'server', 'gradio', 'streamlit', 'nicegui']
    
    found_runners = []
    for runner in expected_runners:
        if runner in discovered_runners:
            found_runners.append(runner)
    
    assert len(found_runners) >= 3  # At least 3 runners should be discovered
    
    print(f"✅ Runner Discovery: Found {len(found_runners)} runners: {found_runners}")


def test_runner_help_consistency():
    """Test that all runners have consistent help format."""
    print("🔍 Testing Runner Help Consistency...")
    
    from yaapp.plugins.runners.mcp.plugin import Mcp
    from yaapp.plugins.runners.server.plugin import Server
    from yaapp.plugins.runners.gradio.plugin import Gradio
    from yaapp.plugins.runners.streamlit.plugin import Streamlit
    from yaapp.plugins.runners.nicegui.plugin import NiceGUI
    
    runners = [
        ('MCP', Mcp()),
        ('Server', Server()),
        ('Gradio', Gradio()),
        ('Streamlit', Streamlit()),
        ('NiceGUI', NiceGUI()),
    ]
    
    for name, runner in runners:
        help_text = runner.help()
        
        # Should be a string
        assert isinstance(help_text, str)
        
        # Should not be empty
        assert len(help_text) > 0
        
        # Should contain the runner name
        assert name.upper() in help_text.upper()
        
        # Should contain "HELP"
        assert "HELP" in help_text.upper()
    
    print("✅ Runner Help: All runners have consistent help format")


def main():
    """Run all integration tests."""
    print("🚀 Starting Comprehensive Runner Integration Tests")
    print("=" * 70)
    
    tests = [
        test_mcp_runner,
        test_server_runner,
        test_gradio_runner,
        test_streamlit_runner,
        test_nicegui_runner,
        test_runner_discovery,
        test_runner_help_consistency,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ALL INTEGRATION TESTS PASSED!")
        print("\n🚀 ALL RUNNERS ARE WORKING CORRECTLY!")
        return True
    else:
        print(f"\n🚨 {failed} TESTS FAILED!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)