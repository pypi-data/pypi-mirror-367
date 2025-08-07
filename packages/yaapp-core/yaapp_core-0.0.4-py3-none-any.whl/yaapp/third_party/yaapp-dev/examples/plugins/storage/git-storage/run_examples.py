#!/usr/bin/env python3
"""
Git Storage Examples Runner

Run all Git storage examples with proper error handling and output formatting.
"""

import sys
import subprocess
import time
from pathlib import Path


def run_example(script_name: str, description: str):
    """Run a single example script."""
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ {script_name} not found")
        return False
    
    print(f"\n{'='*60}")
    print(f"🚀 Running: {script_name}")
    print(f"📝 {description}")
    print(f"{'='*60}")
    
    try:
        start_time = time.time()
        
        # Run the example
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=False,  # Show output in real-time
            text=True,
            cwd=script_path.parent
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            print(f"\n✅ {script_name} completed successfully in {duration:.1f}s")
            return True
        else:
            print(f"\n❌ {script_name} failed with exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n💥 Error running {script_name}: {e}")
        return False


def main():
    """Run all Git storage examples."""
    print("🎯 Git Storage Examples Runner")
    print("=" * 60)
    
    examples = [
        ("basic_usage.py", "Basic storage operations and TTL functionality"),
        ("audit_trail.py", "Audit trail and history features demonstration"),
        ("issue_tracker.py", "Complete issue tracking system implementation"),
        ("performance_demo.py", "Performance characteristics and optimization"),
    ]
    
    results = []
    total_start_time = time.time()
    
    for script_name, description in examples:
        success = run_example(script_name, description)
        results.append((script_name, success))
        
        if not success:
            print(f"\n⚠️  Continuing with remaining examples...")
        
        time.sleep(1)  # Brief pause between examples
    
    total_duration = time.time() - total_start_time
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 Examples Summary")
    print(f"{'='*60}")
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for script_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status} {script_name}")
    
    print(f"\nResults: {successful}/{total} examples passed")
    print(f"Total time: {total_duration:.1f}s")
    
    if successful == total:
        print("\n🎉 All examples completed successfully!")
        print("\n💡 What you've seen:")
        print("   • Basic Git storage operations")
        print("   • Immutable audit trails")
        print("   • Complete issue tracking system")
        print("   • Performance characteristics")
        print("   • Caching and optimization")
        print("   • Backup and recovery")
        print("   • Data integrity verification")
        
        print("\n🚀 Next steps:")
        print("   • Integrate Git storage into your YAAPP applications")
        print("   • Explore the test suite for more examples")
        print("   • Check the documentation for advanced features")
        print("   • Consider your specific use cases and requirements")
        
        return 0
    else:
        print(f"\n⚠️  {total - successful} examples failed")
        print("   Check the output above for error details")
        return 1


if __name__ == "__main__":
    sys.exit(main())