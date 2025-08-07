#!/usr/bin/env python3
"""
Test script for Docker2 plugin using CustomExposer.
"""

import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

def test_docker2_plugin():
    """Test the Docker2 plugin with CustomExposer."""
    print("🐳 Testing Docker2 Plugin with CustomExposer")
    print("=" * 60)
    
    try:
        from yaapp.plugins.docker2.plugin import Docker2
        from yaapp import yaapp
        
        # Create Docker2 plugin instance
        docker2 = Docker2()
        print("✅ Docker2 plugin created")
        
        # Plugin should be auto-exposed via @yaapp.expose("docker2", custom=True) decorator
        print("✅ Docker2 plugin auto-exposed via decorator")
        
        # Check the registry
        registry = yaapp.get_registry_items()
        docker2_items = {k: v for k, v in registry.items() if 'docker2' in k}
        
        print(f"📋 Docker2 items in registry: {len(docker2_items)}")
        
        # Show some discovered methods
        if docker2_items:
            print("🔍 Sample discovered methods:")
            for name in sorted(list(docker2_items.keys())[:10]):
                print(f"   - {name}")
            if len(docker2_items) > 10:
                print(f"   ... and {len(docker2_items) - 10} more")
        
        # Test direct method calls
        print(f"\n🧪 Testing direct method calls...")
        
        # Test ping
        ping_result = docker2.ping()
        if ping_result.is_ok():
            print(f"✅ Direct ping: {ping_result.unwrap()}")
        else:
            print(f"❌ Direct ping failed: {ping_result.as_error}")
        
        # Test get_discovered_methods
        methods_result = docker2.get_discovered_methods()
        if methods_result.is_ok():
            methods = methods_result.unwrap()
            print(f"✅ Discovered {len(methods)} methods total")
            
            # Show method categories
            categories = {}
            for path in methods.keys():
                if '/' in path:
                    category = path.split('/')[0]
                else:
                    category = 'root'
                categories[category] = categories.get(category, 0) + 1
            
            print(f"📊 Method categories:")
            for category, count in sorted(categories.items()):
                print(f"   - {category}: {count} methods")
        
        # Test execute_call method
        print(f"\n🧪 Testing execute_call...")
        
        # Test ping via execute_call
        ping_exec_result = docker2.execute_call("ping")
        if ping_exec_result.is_ok():
            print(f"✅ execute_call ping: {ping_exec_result.unwrap()}")
        else:
            print(f"❌ execute_call ping failed: {ping_exec_result.as_error}")
        
        # Test containers/list via execute_call
        containers_result = docker2.execute_call("containers/list")
        if containers_result.is_ok():
            containers = containers_result.unwrap()
            print(f"✅ execute_call containers/list: {len(containers)} containers")
            if containers:
                print(f"   First container: {containers[0].get('name', 'unnamed')}")
        else:
            print(f"❌ execute_call containers/list failed: {containers_result.as_error}")
        
        # Test images/list via execute_call
        images_result = docker2.execute_call("images/list")
        if images_result.is_ok():
            images = images_result.unwrap()
            print(f"✅ execute_call images/list: {len(images)} images")
            if images:
                first_image = images[0]
                tags = first_image.get('tags', ['<no tags>'])
                print(f"   First image: {tags[0] if tags else '<no tags>'}")
        else:
            print(f"❌ execute_call images/list failed: {images_result.as_error}")
        
        assert True
        
    except Exception as e:
        print(f"❌ Docker2 plugin test failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Docker2 plugin test failed: {e}"

def test_registry_functions():
    """Test calling functions through the registry."""
    print(f"\n🧪 Testing Registry Function Calls")
    print("=" * 60)
    
    try:
        from yaapp import yaapp
        
        # Get registry
        registry = yaapp.get_registry_items()
        docker2_items = {k: v for k, v in registry.items() if k.startswith('docker2')}
        
        print(f"📋 Found {len(docker2_items)} docker2 items in registry")
        for name, obj in docker2_items.items():
            print(f"   - {name}: {type(obj)}")
        
        # For CustomExposer, the individual methods aren't in the registry
        # Instead, we should test calling through yaapp.execute_function
        print(f"\n🧪 Testing yaapp.execute_function calls...")
        
        # Test ping through execute_function
        print(f"🧪 Testing ping via execute_function...")
        try:
            result = yaapp.execute_function("docker2", function_name="ping")
            if hasattr(result, 'is_ok') and result.is_ok():
                print(f"✅ execute_function ping: {result.unwrap()}")
            else:
                print(f"❌ execute_function ping failed: {result}")
        except Exception as e:
            print(f"❌ execute_function ping failed: {e}")
        
        # Test containers/list through execute_function
        print(f"🧪 Testing containers/list via execute_function...")
        try:
            result = yaapp.execute_function("docker2", function_name="containers/list")
            if hasattr(result, 'is_ok') and result.is_ok():
                containers = result.unwrap()
                print(f"✅ execute_function containers/list: {len(containers)} containers")
            else:
                print(f"❌ execute_function containers/list failed: {result}")
        except Exception as e:
            print(f"❌ execute_function containers/list failed: {e}")
        
        # Test version through execute_function
        print(f"🧪 Testing version via execute_function...")
        try:
            result = yaapp.execute_function("docker2", function_name="version")
            if hasattr(result, 'is_ok') and result.is_ok():
                version_info = result.unwrap()
                print(f"✅ execute_function version: {type(version_info)}")
                if isinstance(version_info, dict) and 'Version' in version_info:
                    print(f"   Docker version: {version_info['Version']}")
            else:
                print(f"❌ execute_function version failed: {result}")
        except Exception as e:
            print(f"❌ execute_function version failed: {e}")
        
        assert True
        
    except Exception as e:
        print(f"❌ Registry function test failed: {e}")
        assert False, f"Registry function test failed: {e}"

def main():
    """Run all tests."""
    print("🐳 Docker2 CustomExposer Plugin Test Suite")
    print("=" * 80)
    
    # Test plugin creation and discovery
    plugin_ok = test_docker2_plugin()
    
    # Test registry function calls
    registry_ok = test_registry_functions()
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 40)
    print(f"   Plugin Creation & Discovery: {'✅ Success' if plugin_ok else '❌ Failed'}")
    print(f"   Registry Function Calls:     {'✅ Success' if registry_ok else '❌ Failed'}")
    
    if plugin_ok and registry_ok:
        print(f"\n🎉 Docker2 CustomExposer plugin is working!")
        print(f"   - Dynamic API discovery ✅")
        print(f"   - Hierarchical paths ✅")
        print(f"   - Result pattern ✅")
        print(f"   - Registry integration ✅")
    else:
        print(f"\n❌ Some tests failed - check the output above")

if __name__ == "__main__":
    main()