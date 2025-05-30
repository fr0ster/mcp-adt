#!/usr/bin/env python3
"""
Minimal MCP Server Test
This script creates a very simple MCP server with minimal components for testing.
"""

import os
import sys
import argparse
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

# Create a minimal MCP server
mcp = FastMCP("Minimal Test Server")

@mcp.tool()
def hello_world() -> str:
    """Tool: hello_world
       Description: Simple test tool that returns a hello world message.
       Parameters: None
       Required: []"""
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
