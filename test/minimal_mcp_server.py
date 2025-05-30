#!/usr/bin/env python3
"""
Minimal MCP Server Test
This script creates a very simple MCP server with minimal components for testing.
"""

import os
import sys
import argparse
import inspect
from mcp.server.fastmcp import FastMCP

from dotenv import load_dotenv

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description="Minimal MCP Test Server",
    )
    parser.add_argument(
        '--env',
        default='.env',
        help='Path to environment file (default: .env)'
    )
    return parser.parse_args()

# Load environment variables from specified file
def load_environment(env_file_path):
    """Load environment variables from the specified file."""
    if os.path.exists(env_file_path):
        load_dotenv(env_file_path)
        print(f"[+] Loaded environment from: {env_file_path}")
    else:
        print(f"[!] Environment file not found: {env_file_path}")
        print("    Using system environment variables only")

# Function to intercept and log MCP requests
def log_mcp_protocol(func):
    def wrapper(*args, **kwargs):
        print(f"[DEBUG] MCP Function Called: {func.__name__}")
        print(f"[DEBUG] Args: {args}")
        print(f"[DEBUG] Kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"[DEBUG] Result: {result}")
        return result
    return wrapper

# Create a minimal MCP server
mcp = FastMCP("Minimal Test Server")

# Enable debug logging for FastMCP
import types
for name, method in inspect.getmembers(mcp, predicate=inspect.ismethod):
    if name.startswith('_handle_'):
        setattr(mcp, name, log_mcp_protocol(method))

@mcp.tool()
def hello_world() -> str:
    """Tool: hello_world
       Description: Simple test tool that returns a hello world message.
       Parameters: None
       Required: []"""
    print("[TOOL] hello_world called")
    return "Hello, World! This is a test tool."

@mcp.tool()
def echo(message: str) -> str:
    """Tool: echo
       Description: Echoes back the input message.
       Parameters (object):
         message (string): Message to echo back
       Required: ["message"]"""
    return f"Echo: {message}"

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Load environment variables from specified file
    load_environment(args.env)
    
    # Run the MCP server
    print(f"[*] Starting Minimal MCP Test Server")
    mcp.run(transport="stdio")
