#!/usr/bin/env python3
"""
Test script for fixed MCP server
"""

import json
import subprocess
import sys
import time

def test_fixed_server():
    """Test the fixed MCP server with tools/list"""
    print("🧪 Testing Fixed MCP Server with tools/list")
    print("=" * 50)
    
    # Start the fixed server
    cmd = [sys.executable, "mcp_server_fixed.py"]
    print(f"🚀 Starting server: {' '.join(cmd)}")
    
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # Wait for server to start
        time.sleep(3)
        
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
                "clientInfo": {"name": "fixed-test-client", "version": "1.0.0"}
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        print(f"📤 Sending initialize...")
        
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read initialize response
        start_time = time.time()
        timeout = 10.0
        
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                stderr = process.stderr.read()
                print(f"❌ Server terminated unexpectedly. Error: {stderr}")
                return False
            
            response_line = process.stdout.readline()
            if response_line:
                print(f"📥 Initialize response: {response_line.strip()}")
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
        print(f"📤 Sending tools/list...")
        
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Read tools response with timeout
        start_time = time.time()
        timeout = 15.0
        
        print("⏳ Waiting for tools/list response...")
        
        while time.time() - start_time < timeout:
            if process.poll() is not None:
                stderr = process.stderr.read()
                print(f"❌ Server terminated unexpectedly. Error: {stderr}")
                return False
            
            response_line = process.stdout.readline()
            if response_line:
                print(f"📥 Tools response: {response_line.strip()}")
                try:
                    response = json.loads(response_line)
                    if "result" in response:
                        tools = response["result"].get("tools", [])
                        print(f"✅ Tools list received: {len(tools)} tools")
                        for tool in tools:
                            print(f"  • {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')[:50]}...")
                        
                        # Test calling a tool if available
                        if tools:
                            return test_tool_call(process, tools[0]["name"])
                        return True
                    else:
                        print(f"❌ Tools list failed: {response}")
                        return False
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    return False
            
            # Show progress every 3 seconds
            elapsed = time.time() - start_time
            if int(elapsed) % 3 == 0 and elapsed > 2:
                print(f"⏳ Still waiting... ({elapsed:.1f}s elapsed)")
            
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

def test_tool_call(process, tool_name):
    """Test calling a specific tool"""
    print(f"\n🔧 Testing tool call: {tool_name}")
    
    # Prepare tool call based on tool name
    if "btp_connection_status" in tool_name:
        arguments = {}
    elif "search_objects" in tool_name:
        arguments = {"query": "CL_*", "max_results": 3}
    elif "program_source" in tool_name:
        arguments = {"program_name": "TEST_PROGRAM"}
    elif "class_source" in tool_name:
        arguments = {"class_name": "CL_TEST"}
    else:
        arguments = {}
    
    tool_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    request_json = json.dumps(tool_request) + "\n"
    print(f"📤 Calling tool {tool_name}...")
    
    process.stdin.write(request_json)
    process.stdin.flush()
    
    # Read tool response
    start_time = time.time()
    timeout = 10.0
    
    while time.time() - start_time < timeout:
        if process.poll() is not None:
            stderr = process.stderr.read()
            print(f"❌ Server terminated unexpectedly. Error: {stderr}")
            return False
        
        response_line = process.stdout.readline()
        if response_line:
            print(f"📥 Tool response: {response_line.strip()}")
            try:
                response = json.loads(response_line)
                if "result" in response:
                    print(f"✅ Tool {tool_name} executed successfully")
                    return True
                else:
                    print(f"❌ Tool {tool_name} failed: {response}")
                    return False
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON response: {e}")
                return False
        
        time.sleep(0.1)
    else:
        print(f"❌ Timeout waiting for {tool_name} response")
        return False

if __name__ == "__main__":
    success = test_fixed_server()
    
    if success:
        print("\n🎉 Fixed server test PASSED!")
        print("💡 The fixed server works correctly with tools/list and tool calls")
        sys.exit(0)
    else:
        print("\n💥 Fixed server test FAILED!")
        print("🔍 The issue persists even with fixed imports")
        sys.exit(1)
