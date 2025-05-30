#!/usr/bin/env python3
"""
Very simple MCP server for debugging and identifying protocol issues.
"""
import os
import sys
import time
import json
import argparse
from dotenv import load_dotenv

def main():
    """Run the debug server."""
    parser = argparse.ArgumentParser(
        description="Debug MCP Server",
    )
    parser.add_argument(
        '--env',
        default='.env',
        help='Path to environment file (default: .env)'
    )
    args = parser.parse_args()
    
    # Load environment file if specified
    if args.env and os.path.exists(args.env):
        load_dotenv(args.env)
        print(f"[+] Loaded environment from: {args.env}")
    
    print("[*] Starting Debug MCP Server")
    print("[*] Waiting for input on stdin...")
    
    try:
        # Basic protocol implementation
        while True:
            # Read request
            line = sys.stdin.readline()
            if not line:
                print("[!] Input stream closed, exiting", file=sys.stderr)
                break
            
            print(f"[<] Received: {line.strip()}", file=sys.stderr)
            
            try:
                request = json.loads(line)
                request_id = request.get("id", 0)
                method = request.get("method", "")
                params = request.get("params", {})
                
                # Process different method types
                if method == "initialize":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "experimental": {},
                                "prompts": {"listChanged": False},
                                "resources": {"subscribe": False, "listChanged": False},
                                "tools": {"listChanged": False}
                            },
                            "serverInfo": {
                                "name": "Debug MCP Server",
                                "version": "1.0.0"
                            }
                        }
                    }
                elif method == "tools/list":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "tools": [
                                {
                                    "name": "hello_world",
                                    "description": "Simple test tool that returns a hello world message."
                                },
                                {
                                    "name": "echo",
                                    "description": "Echoes back the input message."
                                }
                            ]
                        }
                    }
                elif method == "tools/call":
                    tool_name = params.get("name", "")
                    tool_args = params.get("arguments", {})
                    
                    # Simple tool implementations
                    if tool_name == "hello_world":
                        result = "Hello, World! This is a test tool."
                    elif tool_name == "echo":
                        message = tool_args.get("message", "")
                        result = f"Echo: {message}"
                    else:
                        result = f"Unknown tool: {tool_name}"
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "value": result
                        }
                    }
                elif method == "shutdown":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": None
                    }
                    print("[*] Received shutdown request, will exit after response", file=sys.stderr)
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                
                # Send response
                response_json = json.dumps(response)
                print(f"[>] Sending: {response_json}", file=sys.stderr)
                print(response_json, flush=True)
                
                # Exit after shutdown
                if method == "shutdown":
                    break
                
            except json.JSONDecodeError:
                print(f"[!] Invalid JSON: {line}", file=sys.stderr)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response), flush=True)
            
            except Exception as e:
                print(f"[!] Error processing request: {e}", file=sys.stderr)
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_id if 'request_id' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": "Internal error"
                    }
                }
                print(json.dumps(error_response), flush=True)
    
    except KeyboardInterrupt:
        print("[*] Interrupted, exiting", file=sys.stderr)
    
    print("[*] Server stopped", file=sys.stderr)

if __name__ == "__main__":
    main()
