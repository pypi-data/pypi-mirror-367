#!/usr/bin/env python3
"""
Comprehensive test to verify all major fixes are working together.
"""

import sys

# Additional imports with proper path handling
sys.path.insert(0, "../../src")
from yaapp import Yaapp
from yaapp.exposers.function import FunctionExposer
from yaapp.exposers.class_exposer import ClassExposer

def test_comprehensive():
    """Test that all major fixes work together."""
    
    # Test function exposure and execution
    def sample_function(message: str = "test"):
        return f"Function result: {message}"
    
    # Test class exposure and caching
    class SampleClass:
        def __init__(self):
            self.counter = 0
        
        def increment(self):
            self.counter += 1
            return f"Counter: {self.counter}"
    
    app = Yaapp()
    app.expose(sample_function)
    app.expose(SampleClass)
    
    print("=== Comprehensive Integration Test ===")
    
    # Test function exposer
    func_obj, func_exposer = app._registry['sample_function']
    result1 = func_exposer.run(func_obj, message="Hello World")
    
    if result1.is_ok() and "Function result: Hello World" in result1.unwrap():
        print("✅ Function exposure and execution working")
    else:
        print("❌ Function exposure failed")
        return False
    
    # Test class exposer caching behavior (production design)
    class_obj, class_exposer = app._registry['SampleClass']
    
    # First call - should create cached instance
    instance1 = class_exposer.run(class_obj)
    if not instance1.is_ok():
        print("❌ Class instantiation failed")
        return False
    
    result1 = instance1.unwrap().increment()
    
    # Second call - should reuse cached instance
    instance2 = class_exposer.run(class_obj)
    result2 = instance2.unwrap().increment()
    
    # Third call - should reuse cached instance
    instance3 = class_exposer.run(class_obj)
    result3 = instance3.unwrap().increment()
    
    # With caching design, state is preserved across calls
    if result1 == "Counter: 1" and result2 == "Counter: 2" and result3 == "Counter: 3":
        print("✅ Class caching behavior working - state preserved across calls")
    else:
        print(f"❌ Class caching behavior failed: {result1}, {result2}, {result3}")
        return False
    
    # Verify instances are the same object (caching design)
    if instance1.unwrap() is instance2.unwrap() and instance2.unwrap() is instance3.unwrap():
        print("✅ Same instance returned - caching design working")
    else:
        print("❌ Different instances returned - caching design broken")
        return False
    
    print("✅ All comprehensive tests passed!")

if __name__ == "__main__":
    success = test_comprehensive()
    sys.exit(0 if success else 1)