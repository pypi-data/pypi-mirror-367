#!/usr/bin/env python3
"""
Comprehensive test runner for all yaapp runners.
Run this to test all runners and see which ones are working.
"""

import sys
import os
import subprocess
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


def run_runner_tests():
    """Run all runner tests and report results."""
    print("🧪 Running Comprehensive Runner Tests")
    print("=" * 50)
    
    test_files = [
        'test_mcp_runner.py',
        'test_server_runner.py', 
        'test_gradio_runner.py',
        'test_streamlit_runner.py',
        'test_nicegui_runner.py',
        'test_cli_runners.py'
    ]
    
    results = {}
    
    for test_file in test_files:
        print(f"\n🔍 Testing {test_file}...")
        
        try:
            # Run pytest on the specific test file
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                test_file, 
                '-v',
                '--tb=short'
            ], 
            cwd=os.path.dirname(__file__),
            capture_output=True, 
            text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {test_file}: PASSED")
                results[test_file] = 'PASSED'
            else:
                print(f"❌ {test_file}: FAILED")
                print(f"Error output:\n{result.stdout}\n{result.stderr}")
                results[test_file] = 'FAILED'
                
        except Exception as e:
            print(f"💥 {test_file}: ERROR - {e}")
            results[test_file] = 'ERROR'
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for r in results.values() if r == 'PASSED')
    failed = sum(1 for r in results.values() if r == 'FAILED')
    errors = sum(1 for r in results.values() if r == 'ERROR')
    
    for test_file, result in results.items():
        status_emoji = {
            'PASSED': '✅',
            'FAILED': '❌', 
            'ERROR': '💥'
        }[result]
        print(f"{status_emoji} {test_file}: {result}")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"💥 Errors: {errors}")
    
    if failed > 0 or errors > 0:
        print("\n🚨 SOME TESTS FAILED!")
        print("Check the output above for details.")
        return False
    else:
        print("\n🎉 ALL TESTS PASSED!")
        return True


def test_individual_runners():
    """Test individual runners manually."""
    print("\n🔧 Manual Runner Tests")
    print("=" * 30)
    
    from yaapp import Yaapp
    
    # Create test app
    app = Yaapp(auto_discover=False)
    
    @app.expose
    def test_func(x: int, y: int) -> int:
        return x + y
    
    # Test each runner
    runners_to_test = [
        ('MCP', 'yaapp.plugins.runners.mcp.plugin', 'Mcp'),
        ('Server', 'yaapp.plugins.runners.server.plugin', 'Server'),
        ('Gradio', 'yaapp.plugins.runners.gradio.plugin', 'Gradio'),
        ('Streamlit', 'yaapp.plugins.runners.streamlit.plugin', 'Streamlit'),
        ('NiceGUI', 'yaapp.plugins.runners.nicegui.plugin', 'NiceGUI'),
    ]
    
    for name, module_path, class_name in runners_to_test:
        try:
            # Import the runner
            module = __import__(module_path, fromlist=[class_name])
            runner_class = getattr(module, class_name)
            
            # Instantiate
            runner = runner_class()
            
            # Test help method
            help_text = runner.help()
            assert isinstance(help_text, str)
            assert len(help_text) > 0
            
            print(f"✅ {name}: Import and instantiation successful")
            
        except ImportError as e:
            print(f"⚠️ {name}: Import failed - {e}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")


if __name__ == "__main__":
    print("🚀 Starting Comprehensive Runner Tests")
    
    # Run pytest tests
    success = run_runner_tests()
    
    # Run manual tests
    test_individual_runners()
    
    if success:
        print("\n🎯 All tests completed successfully!")
        sys.exit(0)
    else:
        print("\n💀 Some tests failed!")
        sys.exit(1)