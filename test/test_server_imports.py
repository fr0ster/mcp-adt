#!/usr/bin/env python3
"""
Test script to check if all imports in mcp_server.py work correctly
"""

import sys
import traceback

def test_imports():
    """Test all imports from mcp_server.py"""
    print("🔍 Testing imports from mcp_server.py...")
    
    try:
        print("  • Testing argparse...")
        import argparse
        print("    ✅ argparse OK")
        
        print("  • Testing os...")
        import os
        print("    ✅ os OK")
        
        print("  • Testing FastMCP...")
        from mcp.server.fastmcp import FastMCP
        print("    ✅ FastMCP OK")
        
        print("  • Testing dotenv...")
        from dotenv import load_dotenv
        print("    ✅ dotenv OK")
        
        print("  • Testing tool imports...")
        
        # Test each tool import individually
        tools_to_test = [
            ("function_group_source", "get_function_group_source"),
            ("cds_source", "get_cds_source"),
            ("class_source", "get_class_source"),
            ("behavior_definition_source", "get_behavior_definition_source"),
            ("function_source", "get_function_source"),
            ("include_source", "get_include_source"),
            ("interface_source", "get_interface_source"),
            ("package_structure", "get_package_structure"),
            ("program_source", "get_program_source"),
            ("structure_source", "get_structure_source"),
            ("table_source", "get_table_source"),
            ("transaction_properties", "get_transaction_properties"),
            ("type_info", "get_type_info"),
            ("search_objects", "get_search_objects"),
            ("usage_references", "get_usage_references"),
            ("metadata_extension_source", "get_metadata_extension_source"),
            ("table_contents", "get_table_contents"),
            ("sql_query", "get_sql_query"),
            ("enhancements", "get_enhancements"),
        ]
        
        for module_name, function_name in tools_to_test:
            try:
                print(f"    • Testing {module_name}...")
                module = __import__(f"src.tools.{module_name}", fromlist=[function_name])
                func = getattr(module, function_name)
                print(f"      ✅ {module_name}.{function_name} OK")
            except Exception as e:
                print(f"      ❌ {module_name}.{function_name} FAILED: {e}")
                traceback.print_exc()
                return False
        
        print("  • Testing BTP tools...")
        try:
            from src.tools.btp_tools import (
                generate_env_from_service_key_file,
                generate_env_from_service_key_json,
                parse_btp_service_key,
                get_btp_connection_status
            )
            print("    ✅ BTP tools OK")
        except Exception as e:
            print(f"    ❌ BTP tools FAILED: {e}")
            traceback.print_exc()
            return False
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import test failed: {e}")
        traceback.print_exc()
        return False

def test_server_creation():
    """Test creating the MCP server instance"""
    print("\n🔧 Testing MCP server creation...")
    
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("Test Server")
        print("✅ MCP server instance created successfully")
        return True
    except Exception as e:
        print(f"❌ MCP server creation failed: {e}")
        traceback.print_exc()
        return False

def test_tool_registration():
    """Test registering a simple tool"""
    print("\n🛠️ Testing tool registration...")
    
    try:
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP("Test Server")
        
        @mcp.tool()
        def test_tool() -> str:
            """Test tool"""
            return "test"
        
        print("✅ Tool registration successful")
        return True
    except Exception as e:
        print(f"❌ Tool registration failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing MCP Server Components")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Server Creation Test", test_server_creation),
        ("Tool Registration Test", test_tool_registration),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results[test_name] = False
    
    print("\n📊 Test Results:")
    print("=" * 20)
    
    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All component tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 {total - passed} test(s) failed!")
        sys.exit(1)
