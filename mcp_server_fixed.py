import argparse
import os
from mcp.server.fastmcp import FastMCP

# Import tools from root directory (old structure)
import sys
sys.path.append('.')

try:
    from tools.program_source import get_program_source
    from tools.class_source import get_class_source
    from tools.search_objects import get_search_objects
    from tools.btp_tools import get_btp_connection_status
    print("[+] Using tools from root directory")
except ImportError:
    # Fallback to src.tools
    from src.tools.program_source import get_program_source
    from src.tools.class_source import get_class_source
    from src.tools.search_objects import get_search_objects
    from src.tools.btp_tools import get_btp_connection_status
    print("[+] Using tools from src.tools directory")

from dotenv import load_dotenv

# Parse command line arguments
def parse_args():
    parser = argparse.ArgumentParser(
        description="MCP ADT Server (Fixed Version) for SAP ABAP Development Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--env',
        default='.env',
        help='Path to environment file (default: .env)'
    )
    parser.add_argument(
        '--transport',
        default='stdio',
        choices=['stdio', 'http'],
        help='Transport protocol (default: stdio)'
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

mcp = FastMCP("ADT Server Fixed")

@mcp.tool()
def get_program_source_mcp(program_name: str) -> list[str]:
    """Retrieve ABAP program source code"""
    return get_program_source(program_name)

@mcp.tool()
def get_class_source_mcp(class_name: str) -> list[str]:
    """Retrieve ABAP class source code"""
    return get_class_source(class_name)

@mcp.tool()
def get_search_objects_mcp(query: str, max_results: int = 10) -> list[dict]:
    """Search for ABAP objects"""
    return get_search_objects(query, max_results=max_results)

@mcp.tool()
def get_btp_connection_status_mcp() -> str:
    """Check BTP connection status"""
    return get_btp_connection_status()

if __name__ == "__main__":
    # Parse command line arguments
    args = parse_args()
    
    # Load environment variables from specified file
    load_environment(args.env)
    
    # Run the MCP server
    print(f"[*] Starting Fixed MCP ADT Server with transport: {args.transport}")
    mcp.run(transport=args.transport)
