#!/usr/bin/env python3
"""
Git Storage Performance Demo

Demonstrates performance characteristics and optimization strategies:
- Bulk operations performance
- Caching effectiveness
- Memory usage patterns
- Repository size growth
- Optimization techniques
"""

import tempfile
import time
import random
import string
from pathlib import Path
from typing import List, Dict

# Import YAAPP storage
from yaapp.plugins.storage import create_git_storage_manager


def generate_test_data(count: int) -> List[Dict]:
    """Generate test data for performance testing."""
    data = []
    
    for i in range(count):
        item = {
            "id": f"item_{i:06d}",
            "name": f"Test Item {i}",
            "description": f"This is test item number {i} with some description text.",
            "category": random.choice(["electronics", "books", "clothing", "home", "sports"]),
            "price": round(random.uniform(10.0, 1000.0), 2),
            "in_stock": random.choice([True, False]),
            "tags": random.sample(["new", "popular", "sale", "featured", "limited"], k=random.randint(1, 3)),
            "metadata": {
                "created_by": random.choice(["user1", "user2", "user3"]),
                "weight": round(random.uniform(0.1, 10.0), 2),
                "dimensions": {
                    "length": random.randint(1, 100),
                    "width": random.randint(1, 100),
                    "height": random.randint(1, 100)
                }
            },
            "reviews": [
                {
                    "rating": random.randint(1, 5),
                    "comment": f"Review {j} for item {i}",
                    "reviewer": f"reviewer_{random.randint(1, 100)}"
                }
                for j in range(random.randint(0, 3))
            ]
        }
        data.append(item)
    
    return data


def measure_time(func, *args, **kwargs):
    """Measure execution time of a function."""
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time


def print_section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_subsection(title: str):
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")


def format_time(seconds: float) -> str:
    """Format time in human-readable format."""
    if seconds < 0.001:
        return f"{seconds*1000000:.1f}μs"
    elif seconds < 1:
        return f"{seconds*1000:.1f}ms"
    else:
        return f"{seconds:.2f}s"


def format_size(bytes_size: int) -> str:
    """Format size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f}{unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f}TB"


def main():
    print_section("Git Storage Performance Demo")
    
    # Create temporary directory for this demo
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "performance_test"
        
        print(f"📁 Repository: {repo_path}")
        
        # Create Git storage manager
        storage = create_git_storage_manager(
            repo_path=str(repo_path),
            author_name="Performance Test",
            author_email="perf@test.com"
        )
        
        git_backend = storage.get_backend("default")
        
        print_subsection("Bulk Write Performance")
        
        # Test different batch sizes
        batch_sizes = [10, 50, 100, 500]
        
        for batch_size in batch_sizes:
            print(f"\n📝 Testing batch size: {batch_size}")
            
            # Generate test data
            test_data = generate_test_data(batch_size)
            
            # Measure individual writes
            def write_individual():
                for item in test_data:
                    storage.set(f"perf_test_{item['id']}", item)
            
            _, write_time = measure_time(write_individual)
            
            write_rate = batch_size / write_time if write_time > 0 else 0
            avg_time_per_item = write_time / batch_size if batch_size > 0 else 0
            
            print(f"   Write time: {format_time(write_time)}")
            print(f"   Rate: {write_rate:.1f} items/sec")
            print(f"   Avg per item: {format_time(avg_time_per_item)}")
            
            # Clean up for next test
            for item in test_data:
                storage.delete(f"perf_test_{item['id']}")
        
        print_subsection("Read Performance and Caching")
        
        # Create test data for read performance
        read_test_data = generate_test_data(100)
        
        print("📝 Setting up test data...")
        for item in read_test_data:
            storage.set(f"read_test_{item['id']}", item)
        
        # Test cold reads (no cache)
        print("\n🧊 Cold read performance (no cache):")
        
        def read_all_cold():
            # Clear cache first
            if hasattr(git_backend, '_cache'):
                git_backend._cache.clear()
                git_backend._cache_timestamps.clear()
            
            results = []
            for item in read_test_data:
                result = storage.get(f"read_test_{item['id']}")
                results.append(result)
            return results
        
        cold_results, cold_time = measure_time(read_all_cold)
        cold_rate = len(read_test_data) / cold_time if cold_time > 0 else 0
        
        print(f"   Read time: {format_time(cold_time)}")
        print(f"   Rate: {cold_rate:.1f} items/sec")
        print(f"   Avg per item: {format_time(cold_time / len(read_test_data))}")
        
        # Test warm reads (with cache)
        print("\n🔥 Warm read performance (with cache):")
        
        def read_all_warm():
            results = []
            for item in read_test_data:
                result = storage.get(f"read_test_{item['id']}")
                results.append(result)
            return results
        
        warm_results, warm_time = measure_time(read_all_warm)
        warm_rate = len(read_test_data) / warm_time if warm_time > 0 else 0
        
        print(f"   Read time: {format_time(warm_time)}")
        print(f"   Rate: {warm_rate:.1f} items/sec")
        print(f"   Avg per item: {format_time(warm_time / len(read_test_data))}")
        print(f"   Speedup: {cold_time / warm_time:.1f}x faster")
        
        print_subsection("Memory Usage Analysis")
        
        # Analyze cache usage
        if hasattr(git_backend, '_cache'):
            cache_size = len(git_backend._cache)
            print(f"📊 Cache Statistics:")
            print(f"   Cached items: {cache_size}")
            print(f"   Cache hit ratio: ~{(warm_rate / cold_rate):.1f}x improvement")
            
            # Estimate memory usage
            import sys
            total_cache_size = sum(sys.getsizeof(item) for item in git_backend._cache.values())
            print(f"   Estimated cache memory: {format_size(total_cache_size)}")
        
        print_subsection("Repository Growth Analysis")
        
        # Analyze repository size growth
        if hasattr(git_backend, 'get_repository_stats'):
            initial_stats = git_backend.get_repository_stats()
            
            print(f"📈 Repository Growth:")
            print(f"   Initial size: {format_size(initial_stats.get('repository_size_bytes', 0))}")
            print(f"   Initial commits: {initial_stats.get('total_commits', 0)}")
            print(f"   Initial keys: {initial_stats.get('total_keys', 0)}")
            
            # Add more data and measure growth
            growth_test_data = generate_test_data(200)
            
            print(f"\n   Adding {len(growth_test_data)} more items...")
            for item in growth_test_data:
                storage.set(f"growth_test_{item['id']}", item)
            
            final_stats = git_backend.get_repository_stats()
            
            size_growth = final_stats.get('repository_size_bytes', 0) - initial_stats.get('repository_size_bytes', 0)
            commit_growth = final_stats.get('total_commits', 0) - initial_stats.get('total_commits', 0)
            
            print(f"   Final size: {format_size(final_stats.get('repository_size_bytes', 0))}")
            print(f"   Size growth: {format_size(size_growth)}")
            print(f"   Commits added: {commit_growth}")
            print(f"   Avg size per item: {format_size(size_growth / len(growth_test_data)) if growth_test_data else '0B'}")
        
        print_subsection("Query Performance")
        
        # Test key listing performance
        print("🔍 Key listing performance:")
        
        def list_all_keys():
            return storage.keys()
        
        all_keys, list_time = measure_time(list_all_keys)
        
        print(f"   Listed {len(all_keys)} keys in {format_time(list_time)}")
        print(f"   Rate: {len(all_keys) / list_time:.1f} keys/sec")
        
        # Test pattern matching
        print(f"\n🎯 Pattern matching performance:")
        
        def list_pattern_keys():
            return storage.keys("read_test_*")
        
        pattern_keys, pattern_time = measure_time(list_pattern_keys)
        
        print(f"   Found {len(pattern_keys)} matching keys in {format_time(pattern_time)}")
        print(f"   Pattern match rate: {len(pattern_keys) / pattern_time:.1f} keys/sec")
        
        print_subsection("Cleanup Performance")
        
        # Test cleanup operations
        print("🧹 Cleanup performance:")
        
        # Add some items with TTL
        ttl_items = 50
        print(f"   Adding {ttl_items} items with TTL...")
        
        for i in range(ttl_items):
            storage.set(f"ttl_test_{i}", {"data": f"temporary_{i}"}, ttl_seconds=1)
        
        # Wait for expiration
        time.sleep(2)
        
        # Test cleanup
        def cleanup_expired():
            if hasattr(git_backend, 'cleanup_expired'):
                return git_backend.cleanup_expired()
            return 0
        
        cleaned_count, cleanup_time = measure_time(cleanup_expired)
        
        print(f"   Cleaned {cleaned_count} expired items in {format_time(cleanup_time)}")
        if cleaned_count > 0:
            print(f"   Cleanup rate: {cleaned_count / cleanup_time:.1f} items/sec")
        
        print_subsection("Optimization Recommendations")
        
        # Provide optimization recommendations based on results
        print("💡 Performance Optimization Tips:")
        
        if cold_time > 0 and warm_time > 0:
            cache_improvement = cold_time / warm_time
            if cache_improvement > 2:
                print(f"   ✅ Caching is very effective ({cache_improvement:.1f}x speedup)")
            else:
                print(f"   ⚠️  Caching provides modest improvement ({cache_improvement:.1f}x speedup)")
        
        if hasattr(git_backend, '_cache'):
            cache_size = len(git_backend._cache)
            if cache_size > 1000:
                print("   💾 Consider cache size limits for memory management")
            
        # Repository size recommendations
        if hasattr(git_backend, 'get_repository_stats'):
            stats = git_backend.get_repository_stats()
            repo_size = stats.get('repository_size_bytes', 0)
            
            if repo_size > 100 * 1024 * 1024:  # 100MB
                print("   📦 Repository is large - consider periodic git gc")
            
            commits = stats.get('total_commits', 0)
            if commits > 10000:
                print("   🗂️  Many commits - consider repository maintenance")
        
        print("\n🚀 Performance Best Practices:")
        print("   • Use caching for frequently accessed data")
        print("   • Batch operations when possible")
        print("   • Monitor repository size growth")
        print("   • Use TTL for temporary data")
        print("   • Regular cleanup of expired items")
        print("   • Consider sharding for very large datasets")
        
        print_section("Performance Demo Complete")
        
        # Final statistics summary
        if hasattr(git_backend, 'get_repository_stats'):
            final_stats = git_backend.get_repository_stats()
            
            print("📊 Final Performance Summary:")
            print(f"   Total operations performed: ~{final_stats.get('total_commits', 0)}")
            print(f"   Repository size: {format_size(final_stats.get('repository_size_bytes', 0))}")
            print(f"   Items stored: {final_stats.get('total_keys', 0)}")
            print(f"   Cache efficiency: {cache_improvement:.1f}x improvement" if 'cache_improvement' in locals() else "")
            
            if cold_time > 0:
                print(f"   Best read rate: {warm_rate:.1f} items/sec (cached)")
                print(f"   Cold read rate: {cold_rate:.1f} items/sec (uncached)")


if __name__ == "__main__":
    main()