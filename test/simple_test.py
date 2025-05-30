#!/usr/bin/env python3
"""
Simple test script to verify MCP server functionality
"""

import json
import subprocess
import sys
import time
import os

def test_minimal_server():
    """Test the minimal MCP server"""
    print("=== Testing Minimal MCP Server ===")
    
    # Start the minimal server
    cmd = [sys.executable, "test/minimal_mcp_server.py"]
    print(f"Starting server: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Wait a moment for server to start
        time.sleep(1)
        
        if process.poll() is not None:
            stderr = process.stderr.read()
            print(f"❌ Server failed to start. Error: {stderr}")
            return False
        
        print("✅ Server started successfully")
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "simple-test-client", "version": "1.0.0"}
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        print(f"📤 Sending initialize: {request_json.strip()}")
        
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read response with timeout
        start_time = time.time()
        timeout = 5.0
        
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                stderr = process.stderr.read()
                print(f"❌ Server terminated unexpectedly. Error: {stderr}")
                return False
            
            response_line = process.stdout.readline()
            if response_line:
                print(f"📥 Received: {response_line.strip()}")
                try:
                    response = json.loads(response_line)
                    if "result" in response:
                        print("✅ Initialize successful")
                        break
                    else:
                        print(f"❌ Initialize failed: {response}")
                        return False
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    return False
            
            time.sleep(0.1)
        else:
            print("❌ Timeout waiting for initialize response")
            return False
        
        # Send tools/list request
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        request_json = json.dumps(tools_request) + "\n"
        print(f"📤 Sending tools/list: {request_json.strip()}")
        
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read tools response
        start_time = time.time()
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                stderr = process.stderr.read()
                print(f"❌ Server terminated unexpectedly. Error: {stderr}")
                return False
            
            response_line = process.stdout.readline()
            if response_line:
                print(f"📥 Received: {response_line.strip()}")
                try:
                    response = json.loads(response_line)
                    if "result" in response:
                        tools = response["result"].get("tools", [])
                        print(f"✅ Tools list received: {len(tools)} tools")
                        for tool in tools:
                            print(f"  • {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                        return True
                    else:
                        print(f"❌ Tools list failed: {response}")
                        return False
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    return False
            
            time.sleep(0.1)
        else:
            print("❌ Timeout waiting for tools/list response")
            return False
            
    finally:
        # Clean up
        try:
            if process.stdin:
                process.stdin.close()
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()
            
            process.terminate()
            process.wait(timeout=2)
        except:
            process.kill()
            process.wait()

def test_main_server():
    """Test the main MCP server"""
    print("\n=== Testing Main MCP Server ===")
    
    # Start the main server
    cmd = [sys.executable, "mcp_server.py"]
    print(f"Starting server: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Wait a moment for server to start
        time.sleep(2)
        
        if process.poll() is not None:
            stderr = process.stderr.read()
            print(f"❌ Server failed to start. Error: {stderr}")
            return False
        
        print("✅ Server started successfully")
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "simple-test-client", "version": "1.0.0"}
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        print(f"📤 Sending initialize: {request_json.strip()}")
        
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read response with timeout
        start_time = time.time()
        timeout = 10.0
        
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                stderr = process.stderr.read()
                print(f"❌ Server terminated unexpectedly. Error: {stderr}")
                return False
            
            response_line = process.stdout.readline()
            if response_line:
                print(f"📥 Received: {response_line.strip()}")
                try:
                    response = json.loads(response_line)
                    if "result" in response:
                        print("✅ Initialize successful")
                        server_info = response["result"].get("serverInfo", {})
                        print(f"Server: {server_info.get('name', 'Unknown')} v{server_info.get('version', 'Unknown')}")
                        return True
                    else:
                        print(f"❌ Initialize failed: {response}")
                        return False
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    return False
            
            time.sleep(0.1)
        else:
            print("❌ Timeout waiting for initialize response")
            return False
            
    finally:
        # Clean up
        try:
            if process.stdin:
                process.stdin.close()
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()
            
            process.terminate()
            process.wait(timeout=2)
        except:
            process.kill()
            process.wait()

if __name__ == "__main__":
    print("🧪 Starting MCP Server Tests")
    
    # Test minimal server first
    minimal_success = test_minimal_server()
    
    # Test main server
    main_success = test_main_server()
    
    print(f"\n📊 Test Results:")
    print(f"  Minimal Server: {'✅ PASS' if minimal_success else '❌ FAIL'}")
    print(f"  Main Server: {'✅ PASS' if main_success else '❌ FAIL'}")
    
    if minimal_success and main_success:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)
