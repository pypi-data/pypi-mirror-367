#!/usr/bin/env python3
"""
Simple test runner for real integration tests.
Can be run without pytest for environments where pytest is not available.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

# Import the test functions
from test_remote_process_real_integration import (
    test_basic_rpc_calls,
    test_process_lifecycle,
    test_interactive_process,
    test_streaming_endpoint,
    test_terminal_client
)

async def run_all_tests():
    """Run all real integration tests"""
    print("🧪 REMOTE PROCESS REAL INTEGRATION TESTS")
    print("=" * 60)
    print("Starting REAL tests with actual server and client!")
    print("=" * 60)
    
    tests = [
        ("Basic RPC Calls", test_basic_rpc_calls),
        ("Process Lifecycle", test_process_lifecycle),
        ("Interactive Process", test_interactive_process),
        ("Streaming Endpoint", test_streaming_endpoint),
        ("Terminal Client", test_terminal_client),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            print(f"\n🏃 Running: {test_name}")
            await test_func()
            print(f"✅ PASSED: {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_name}")
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🏁 TEST RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed > 0:
        print("❌ Some tests failed!")
        print("\n💡 Common issues:")
        print("   - Missing dependencies: pip install fastapi uvicorn pydantic")
        print("   - System Python vs virtual environment")
        print("   - Firewall blocking localhost connections")
        return 1
    else:
        print("✅ ALL TESTS PASSED!")
        print("\n🎉 The RemoteProcess plugin is working correctly!")
        return 0

if __name__ == "__main__":
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(result)
    except KeyboardInterrupt:
        print("\n🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test runner failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)