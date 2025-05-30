
#!/usr/bin/env python3
"""
Simple MCP Client for testing the SAP ADT MCP Server.
This client connects to the MCP server and allows testing various tools.
"""

import json
import subprocess
import sys
import time
from typing import Dict, Any


class MCPTestClient:
    """Simple MCP test client using stdio transport."""
    
    def __init__(self, server_script: str, env_file: str = None):
        """Initialize the MCP test client.
        
        Args:
            server_script: Path to the MCP server script
            env_file: Optional path to environment file
        """
        self.server_script = server_script
        self.env_file = env_file
        self.process = None
        self.request_id = 1
    
    def start_server(self):
        """Start the MCP server process."""
        cmd = [sys.executable, self.server_script]
        if self.env_file:
            cmd.extend(['--env', self.env_file])
        
        print(f"[*] Starting MCP server: {' '.join(cmd)}")
        
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0
        )
        
        # Wait a moment for server to start
        time.sleep(1)
        
        if self.process.poll() is not None:
            stderr = self.process.stderr.read()
            raise RuntimeError(f"Server failed to start. Error: {stderr}")
        
        print("[+] Server started successfully")
    
    def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("[+] Server stopped")
    
    def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server.
        
        Args:
            method: The method name to call
            params: Optional parameters for the method
            
        Returns:
            The response from the server
        """
        if not self.process:
            raise RuntimeError("Server not started")
        
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }
        
        if params:
            request["params"] = params
        
        self.request_id += 1
        
        # Send request
        request_json = json.dumps(request) + "\n"
        print(f"📤 Sending: {request_json.strip()}")
        
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline()
        if not response_line:
            stderr = self.process.stderr.read()
            raise RuntimeError(f"No response from server. Error: {stderr}")
        
        print(f"📥 Received: {response_line.strip()}")
        
        try:
            response = json.loads(response_line)
            return response
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response: {response_line}. Error: {e}")
    
    def initialize(self):
        """Initialize the MCP session."""
        response = self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "mcp-test-client",
                "version": "1.0.0"
            }
        })
        
        if "error" in response:
            raise RuntimeError(f"Initialization failed: {response['error']}")
        
        print("[+] MCP session initialized")
        return response
    
    def list_tools(self):
        """List available tools."""
        response = self.send_request("tools/list")
        
        if "error" in response:
            raise RuntimeError(f"Failed to list tools: {response['error']}")
        
        return response.get("result", {}).get("tools", [])
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None):
        """Call a specific tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Optional arguments for the tool
            
        Returns:
            Tool response
        """
        params = {"name": tool_name}
        if arguments:
            params["arguments"] = arguments
        
        response = self.send_request("tools/call", params)
        
        if "error" in response:
            raise RuntimeError(f"Tool call failed: {response['error']}")
        
        return response.get("result", {})


def test_basic_functionality(client: MCPTestClient):
    """Test basic MCP functionality."""
    print("\n=== Testing Basic MCP Functionality ===")
    
    # Initialize
    init_response = client.initialize()
    print(f"Server capabilities: {init_response.get('result', {}).get('capabilities', {})}")
    
    # List tools
    tools = client.list_tools()
    print(f"\n📋 Available tools ({len(tools)}):")
    for tool in tools:
        name = tool.get("name", "Unknown")
        description = tool.get("description", "No description")
        print(f"  • {name}: {description}")
    
    return tools


def test_btp_tools(client: MCPTestClient):
    """Test BTP-specific tools."""
    print("\n=== Testing BTP Tools ===")
    
    try:
        # Test connection status
        print("\n🔍 Testing BTP connection status...")
        result = client.call_tool("get_btp_connection_status")
        print("Connection status result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ BTP connection test failed: {e}")


def test_abap_tools(client: MCPTestClient):
    """Test ABAP-specific tools."""
    print("\n=== Testing ABAP Tools ===")
    
    try:
        # Test search objects
        print("\n🔍 Testing ABAP object search...")
        result = client.call_tool("get_search_objects", {"query": "CL_*", "max_results": 5})
        print("Search result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ ABAP search test failed: {e}")


def main():
    """Main test function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MCP ADT Server")
    parser.add_argument("--server", default="mcp_server.py", help="Path to MCP server script")
    parser.add_argument("--env", help="Path to environment file")
    parser.add_argument("--test", choices=["basic", "btp", "abap", "all"], default="all",
                       help="Which tests to run")
    
    args = parser.parse_args()
    
    client = MCPTestClient(args.server, args.env)
    
    try:
        # Start server
        client.start_server()
        
        # Run tests
        if args.test in ["basic", "all"]:
            tools = test_basic_functionality(client)
        
        if args.test in ["btp", "all"]:
            test_btp_tools(client)
        
        if args.test in ["abap", "all"]:
            test_abap_tools(client)
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    finally:
        client.stop_server()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
