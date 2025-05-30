#!/usr/bin/env python3
"""
Quick test script for MCP ADT Server
Performs essential tests to verify server functionality
"""

import sys
import subprocess
import time
import json

def run_test(test_name, test_command):
    """Run a test and return result"""
    print(f"\n🧪 {test_name}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            test_command,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ PASSED")
            return True
        else:
            print("❌ FAILED")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}...")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 CRASHED: {e}")
        return False

def test_server_startup():
    """Test if server can start and respond to initialize"""
    print("\n🚀 Testing server startup and initialization...")
    
    # Start server
    cmd = [sys.executable, "mcp_server.py"]
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        time.sleep(2)  # Wait for startup
        
        if process.poll() is not None:
            stderr = process.stderr.read()
            print(f"❌ Server failed to start: {stderr[:200]}...")
            return False
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "quick-test", "version": "1.0.0"}
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        process.stdin.write(request_json)
        process.stdin.flush()
        
        # Wait for response
        start_time = time.time()
        while time.time() - start_time < 5:
            if process.poll() is not None:
                print("❌ Server terminated unexpectedly")
                return False
            
            response_line = process.stdout.readline()
            if response_line:
                try:
                    response = json.loads(response_line)
                    if "result" in response:
                        server_info = response["result"].get("serverInfo", {})
                        print(f"✅ Server initialized: {server_info.get('name', 'Unknown')}")
                        return True
                    else:
                        print(f"❌ Initialize failed: {response}")
                        return False
                except json.JSONDecodeError:
                    print(f"❌ Invalid response: {response_line[:100]}...")
                    return False
            
            time.sleep(0.1)
        
        print("⏰ Timeout waiting for initialize response")
        return False
        
    finally:
        # Cleanup
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

def main():
    """Main test function"""
    print("⚡ Quick MCP ADT Server Test")
    print("=" * 40)
    
    tests = [
        ("Import Test", [sys.executable, "-m", "test.test_imports"]),
        ("Server Components Test", [sys.executable, "-m", "test.test_server_imports"]),
    ]
    
    results = {}
    
    # Run standard tests
    for test_name, test_command in tests:
        results[test_name] = run_test(test_name, test_command)
    
    # Run server startup test
    results["Server Startup Test"] = test_server_startup()
    
    # Print summary
    print("\n📊 Quick Test Summary")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All quick tests passed!")
        print("💡 Server appears to be working correctly.")
        print("📝 See test/test_report.md for detailed analysis.")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed!")
        print("🔍 Run individual tests for more details:")
        print("   python -m test.test_server_imports")
        print("   python test/simple_test.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())
