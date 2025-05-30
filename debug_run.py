#!/usr/bin/env python3
"""
Quick debug runner for MCP Server
"""

import argparse
import logging
import os
import sys
from mcp.server.fastmcp import FastMCP

def setup_logging(level=logging.DEBUG):
    """Setup detailed logging"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('debug_server.log')
        ]
    )
    
    # Enable FastMCP debug logging
    logging.getLogger('mcp').setLevel(logging.DEBUG)
    logging.getLogger('fastmcp').setLevel(logging.DEBUG)
    
    return logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(
        description="Quick Debug Runner for MCP ADT Server",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--server',
        default='main',
        choices=['main', 'minimal', 'fixed', 'basic'],
        help='Which server to debug (default: main)'
    )
    parser.add_argument(
        '--transport',
        default='http',
        choices=['stdio', 'http'],
        help='Transport protocol (default: http)'
    )
    parser.add_argument(
        '--env',
        default='.env',
        help='Environment file (default: .env)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='HTTP port (default: 8000)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Extra verbose logging'
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logging(log_level)
    
    logger.info("=" * 60)
    logger.info("🐛 MCP Server Debug Runner")
    logger.info("=" * 60)
    logger.info(f"Server: {args.server}")
    logger.info(f"Transport: {args.transport}")
    logger.info(f"Environment: {args.env}")
    if args.transport == 'http':
        logger.info(f"Port: {args.port}")
    logger.info("=" * 60)
    
    # Determine server file
    server_files = {
        'main': 'mcp_server.py',
        'minimal': 'mcp_server_minimal.py',
        'fixed': 'mcp_server_fixed.py',
        'basic': 'mcp_server_basic.py'
    }
    
    server_file = server_files[args.server]
    
    if not os.path.exists(server_file):
        logger.error(f"❌ Server file not found: {server_file}")
        sys.exit(1)
    
    # Build command
    cmd_args = [
        sys.executable, server_file,
        '--transport', args.transport,
        '--env', args.env
    ]
    
    if args.transport == 'http':
        cmd_args.extend(['--port', str(args.port)])
    
    logger.info(f"🚀 Starting server: {' '.join(cmd_args)}")
    
    # Import and run the server
    try:
        if args.server == 'main':
            import mcp_server
            logger.info("✅ Imported main server")
        elif args.server == 'minimal':
            import mcp_server_minimal
            logger.info("✅ Imported minimal server")
        elif args.server == 'fixed':
            import mcp_server_fixed
            logger.info("✅ Imported fixed server")
        elif args.server == 'basic':
            import mcp_server_basic
            logger.info("✅ Imported basic server")
        
        logger.info("🎯 Server should be starting now...")
        logger.info("📝 Check debug_server.log for detailed logs")
        
        if args.transport == 'http':
            logger.info(f"🌐 HTTP server should be available at: http://localhost:{args.port}")
            logger.info("📋 Test with: curl -X POST http://localhost:8000/tools/list")
        
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
