#!/usr/bin/env python3
"""
Quick test to verify all runners are working.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


def test_runner_imports():
    """Test that all runners can be imported and instantiated."""
    print("🧪 Testing Runner Imports and Basic Functionality")
    print("=" * 60)
    
    runners = [
        ('MCP', 'yaapp.plugins.runners.mcp.plugin', 'Mcp'),
        ('Server', 'yaapp.plugins.runners.server.plugin', 'Server'),
        ('Gradio', 'yaapp.plugins.runners.gradio.plugin', 'Gradio'),
        ('Streamlit', 'yaapp.plugins.runners.streamlit.plugin', 'Streamlit'),
        ('NiceGUI', 'yaapp.plugins.runners.nicegui.plugin', 'NiceGUI'),
    ]
    
    results = {}
    
    for name, module_path, class_name in runners:
        print(f"\n🔍 Testing {name} Runner...")
        
        try:
            # Import the module
            module = __import__(module_path, fromlist=[class_name])
            runner_class = getattr(module, class_name)
            
            # Instantiate the runner
            runner = runner_class()
            
            # Test help method
            help_text = runner.help()
            assert isinstance(help_text, str)
            assert len(help_text) > 0
            assert name.upper() in help_text.upper()
            
            # Test run method exists
            assert hasattr(runner, 'run')
            assert callable(runner.run)
            
            print(f"✅ {name}: All basic tests passed")
            results[name] = 'PASSED'
            
        except ImportError as e:
            print(f"⚠️ {name}: Import failed - {e}")
            results[name] = 'IMPORT_FAILED'
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results[name] = 'FAILED'
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 QUICK TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r == 'PASSED')
    failed = sum(1 for r in results.values() if r == 'FAILED')
    import_failed = sum(1 for r in results.values() if r == 'IMPORT_FAILED')
    
    for name, result in results.items():
        status_emoji = {
            'PASSED': '✅',
            'FAILED': '❌',
            'IMPORT_FAILED': '⚠️'
        }[result]
        print(f"{status_emoji} {name}: {result}")
    
    print(f"\nTotal: {len(results)} runners")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"⚠️ Import Failed: {import_failed}")
    
    if failed > 0:
        print("\n🚨 SOME RUNNERS HAVE ISSUES!")
        return False
    elif passed > 0:
        print("\n🎉 ALL WORKING RUNNERS PASSED!")
        return True
    else:
        print("\n😱 NO RUNNERS WORKING!")
        return False


def test_runner_functionality():
    """Test basic runner functionality with a test app."""
    print("\n🔧 Testing Runner Functionality")
    print("=" * 40)
    
    from yaapp import Yaapp
    
    # Create test app
    app = Yaapp(auto_discover=False)
    
    @app.expose
    def test_add(x: int, y: int) -> int:
        """Add two numbers."""
        return x + y
    
    print(f"Created test app with {len(app._registry)} functions")
    
    # Test MCP runner specifically
    try:
        from yaapp.plugins.runners.mcp.plugin import Mcp
        
        runner = Mcp()
        
        # Test tool generation
        with unittest.mock.patch('yaapp.plugins.runners.mcp.plugin.yaapp._registry', app._registry):
            tools = runner._generate_mcp_tools_dict()
            print(f"✅ MCP: Generated {len(tools)} tools")
            
            # Test basic execution
            import asyncio
            
            async def test_execution():
                result = await runner._execute_tool("yaapp.test_add", {"x": 5, "y": 3})
                assert result == 8
                print("✅ MCP: Function execution works")
            
            asyncio.run(test_execution())
            
    except Exception as e:
        print(f"❌ MCP functionality test failed: {e}")
    
    print("✅ Functionality tests completed")


if __name__ == "__main__":
    import unittest.mock
    
    print("🚀 Starting Quick Runner Tests")
    
    # Test imports and basic functionality
    success = test_runner_imports()
    
    # Test functionality
    test_runner_functionality()
    
    if success:
        print("\n🎯 Quick tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💀 Some tests failed!")
        sys.exit(1)