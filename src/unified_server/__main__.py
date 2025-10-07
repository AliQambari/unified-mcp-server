"""
Command-line interface for running the unified server.
"""

import argparse
import sys

from .core.server import create_server
from .core.config import ServerConfig


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description="Unified API & MCP over HTTP Server"
    )
    parser.add_argument(
        "--name",
        default="unified-server",
        help="Server name (default: unified-server)"
    )
    parser.add_argument(
        "--version",
        default="1.0.0",
        help="Server version (default: 1.0.0)"
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Create configuration
    config = ServerConfig(
        name=args.name,
        version=args.version,
        host=args.host,
        port=args.port,
        log_level=args.log_level
    )
    
    # Create and run server
    server = create_server(
        name=args.name,
        version=args.version,
        config=config
    )
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Server failed to start: {str(e)[:100]}")
        sys.exit(1)


if __name__ == "__main__":
    main()