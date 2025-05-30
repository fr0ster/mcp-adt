#!/usr/bin/env python3
"""
Basic MCP Server using core MCP library instead of FastMCP
"""

import argparse
import asyncio
import os
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    TextContent,
    Tool,
)

from src.tools.program_source import get_program_source
from src.tools.class_source import get_class_source
from src.tools.search_objects import get_search_objects
from src.tools.btp_tools import get_btp_connection_status

from dotenv import load_dotenv

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description="Basic MCP ADT Server for SAP ABAP Development Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter
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

# Create the server
server = Server("basic-adt-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_program_source",
            description="Retrieve ABAP program source code",
            inputSchema={
                "type": "object",
                "properties": {
                    "program_name": {
                        "type": "string",
                        "description": "Name of the ABAP program"
                    }
                },
                "required": ["program_name"]
            }
        ),
        Tool(
            name="get_class_source",
            description="Retrieve ABAP class source code",
            inputSchema={
                "type": "object",
                "properties": {
                    "class_name": {
                        "type": "string",
                        "description": "Name of the ABAP class"
                    }
                },
                "required": ["class_name"]
            }
        ),
        Tool(
            name="get_search_objects",
            description="Search for ABAP objects",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_btp_connection_status",
            description="Check BTP connection status",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[TextContent]:
    """Handle tool calls."""
    if arguments is None:
        arguments = {}
    
    try:
        if name == "get_program_source":
            program_name = arguments.get("program_name")
            if not program_name:
                raise ValueError("program_name is required")
            result = get_program_source(program_name)
            return [TextContent(type="text", text=str(result))]
        
        elif name == "get_class_source":
            class_name = arguments.get("class_name")
            if not class_name:
                raise ValueError("class_name is required")
            result = get_class_source(class_name)
            return [TextContent(type="text", text=str(result))]
        
        elif name == "get_search_objects":
            query = arguments.get("query")
            if not query:
                raise ValueError("query is required")
            max_results = arguments.get("max_results", 10)
            result = get_search_objects(query, max_results=max_results)
            return [TextContent(type="text", text=str(result))]
        
        elif name == "get_btp_connection_status":
            result = get_btp_connection_status()
            return [TextContent(type="text", text=str(result))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def main():
    # Parse command line arguments
    args = parse_args()
    
    # Load environment variables from specified file
    load_environment(args.env)
    
    # Run the server
    print("[*] Starting Basic MCP ADT Server")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="Basic ADT Server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
