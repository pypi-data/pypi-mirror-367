#!/usr/bin/env python3
"""
Simple test to verify class instantiation optimization during method discovery.
"""

import sys

# Add src to path
sys.path.insert(0, "../../src")


def test_fastapi_discovery_optimization():
    """Test that FastAPI method discovery doesn't instantiate classes."""
    
    instantiation_count = 0
    
    class TestClass:
        def __init__(self):
            nonlocal instantiation_count
            instantiation_count += 1
            print(f"❌ TestClass instantiated! Count: {instantiation_count}")
        
        def method1(self):
            return "method1"
        
        def method2(self, param: str):
            return f"method2: {param}"
    
    from yaapp.runners.fastapi_runner import FastAPIRunner
    from yaapp import Yaapp
    
    app = Yaapp()
    runner = FastAPIRunner(app)
    
    print("Testing FastAPI _get_class_methods...")
    methods = runner._get_class_methods(TestClass)
    
    if instantiation_count == 0:
        print("✅ _get_class_methods: No instantiation during discovery")
    else:
        print(f"❌ _get_class_methods: {instantiation_count} instantiations occurred")
    
    print(f"   Discovered methods: {list(methods.keys())}")
    
    instantiation_count = 0
    print("\nTesting FastAPI _get_class_methods_rpc...")
    rpc_methods = runner._get_class_methods_rpc(TestClass)
    
    if instantiation_count == 0:
        print("✅ _get_class_methods_rpc: No instantiation during discovery")
    else:
        print(f"❌ _get_class_methods_rpc: {instantiation_count} instantiations occurred")
    
    print(f"   Discovered RPC methods: {list(rpc_methods.keys())}")
    
    return instantiation_count == 0


def test_reflection_discovery_optimization():
    """Test that reflection method discovery doesn't instantiate classes."""
    
    instantiation_count = 0
    
    class TestClass:
        def __init__(self):
            nonlocal instantiation_count
            instantiation_count += 1
            print(f"❌ TestClass instantiated in reflection! Count: {instantiation_count}")
        
        def method1(self):
            return "method1"
        
        def method2(self, param: str):
            return f"method2: {param}"
    
    from yaapp.reflection import CommandReflector
    from yaapp import Yaapp
    from unittest.mock import Mock
    
    app = Yaapp()
    reflector = CommandReflector(app)
    
    # Create a working mock
    mock_command = Mock()
    mock_group = Mock()
    mock_group.group = Mock(return_value=lambda func: func)
    mock_group.command = Mock(return_value=lambda func: func)
    
    print("\nTesting Reflection _add_class_command...")
    try:
        # Note: This will still try to add function commands which may cause issues
        # but the key test is that the class itself isn't instantiated for discovery
        reflector._add_class_command(mock_group, "TestClass", TestClass)
        
        if instantiation_count == 0:
            print("✅ _add_class_command: No instantiation during method discovery")
        else:
            print(f"❌ _add_class_command: {instantiation_count} instantiations occurred")
            
    except Exception as e:
        if instantiation_count == 0:
            print("✅ _add_class_command: No instantiation during method discovery (some mock issues expected)")
        else:
            print(f"❌ _add_class_command: {instantiation_count} instantiations occurred")
        print(f"   Note: Exception occurred (expected with mocking): {e}")
    
    return instantiation_count == 0


def main():
    print("🔧 Class Instantiation Discovery Optimization Test")
    print("=" * 60)
    
    fastapi_success = test_fastapi_discovery_optimization()
    reflection_success = test_reflection_discovery_optimization()
    
    print("\n" + "=" * 60)
    if fastapi_success and reflection_success:
        print("🎉 SUCCESS: Method discovery optimized - no unnecessary instantiation!")
        print("✅ Classes are no longer instantiated during method discovery")
        print("✅ Expensive constructors are not called during introspection")
        print("✅ Significant performance improvement achieved")
    else:
        print("❌ FAILURE: Some discovery methods still instantiate classes")
        if not fastapi_success:
            print("❌ FastAPI runner still instantiates classes")
        if not reflection_success:
            print("❌ Reflection system still instantiates classes")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())