#!/usr/bin/env python3
"""
Test script for minimal MCP server to debug tools/list issue
"""

import json
import subprocess
import sys
import time

def test_minimal_server():
    """Test the minimal MCP server with tools/list"""
    print("🧪 Testing Minimal MCP Server with tools/list")
    print("=" * 50)
    
    # Start the minimal server
    cmd = [sys.executable, "mcp_server_minimal.py"]
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
                "clientInfo": {"name": "minimal-test-client", "version": "1.0.0"}
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
        
        # Read tools response with longer timeout
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
                        return True
                    else:
                        print(f"❌ Tools list failed: {response}")
                        return False
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON response: {e}")
                    return False
            
            # Show progress every 2 seconds
            elapsed = time.time() - start_time
            if int(elapsed) % 2 == 0 and elapsed > 1:
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

if __name__ == "__main__":
    success = test_minimal_server()
    
    if success:
        print("\n🎉 Minimal server test PASSED!")
        print("💡 The minimal server works correctly with tools/list")
        sys.exit(0)
    else:
        print("\n💥 Minimal server test FAILED!")
        print("🔍 There's still an issue with tools/list")
        sys.exit(1)
