"""
Main unified server implementation.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mcp.server import Server

from .config import ServerConfig
from .registry import registry
from ..routes.base import create_base_router
from ..routes.tools import create_tools_router
from ..routes.resources import create_resources_router
from ..routes.prompts import create_prompts_router
from ..routes.mcp import create_mcp_router
from ..routes.api import create_api_router
from ..handlers.mcp_handlers import setup_mcp_handlers
from ..utils.logging import setup_logging, get_logger


class UnifiedServer:
    """Unified server that handles both FastAPI and MCP over HTTP"""
    
    def __init__(
        self,
        name: str = "unified-server",
        version: str = "1.0.0",
        config: ServerConfig = None
    ):
        """
        Initialize the unified server
        
        Args:
            name: Server name
            version: Server version
            config: Server configuration (optional)
        """
        if config is None:
            config = ServerConfig(name=name, version=version)
        else:
            config.name = name
            config.version = version
        
        self.config = config
        self.logger = setup_logging(config.log_level)
        self.app = self._create_fastapi_app()
        self.mcp_server = Server(name)
        
        # Setup routes
        self._setup_routes()
        
        # Setup MCP handlers (for future STDIO support)
        setup_mcp_handlers(self.mcp_server)
    
    def _create_fastapi_app(self) -> FastAPI:
        """Create and configure FastAPI application"""
        app = FastAPI(
            title=self.config.name,
            version=self.config.version,
            docs_url=self.config.docs_url,
            redoc_url=self.config.redoc_url,
            openapi_url=self.config.openapi_url
        )
        
        # Add CORS middleware if enabled
        if self.config.cors_enabled:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=self.config.cors_origins or ["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )
        
        return app
    
    def _setup_routes(self) -> None:
        """Setup all routes"""
        # Base routes
        base_router = create_base_router(self.config)
        self.app.include_router(base_router)
        
        # REST API (new unified API)
        api_router = create_api_router()
        self.app.include_router(api_router)
        
        # Individual routes (legacy, can be removed if not needed)
        self.app.include_router(create_tools_router())
        self.app.include_router(create_resources_router())
        self.app.include_router(create_prompts_router())
        
        # MCP route
        mcp_router = create_mcp_router(self.config)
        self.app.include_router(mcp_router)
    
    def run(
        self,
        host: str = None,
        port: int = None,
        log_level: str = None,
        **kwargs
    ) -> None:
        """
        Run the HTTP server with both REST API and MCP endpoints
        
        Args:
            host: Host to bind to (defaults to config.host)
            port: Port to bind to (defaults to config.port)
            log_level: Logging level (defaults to config.log_level)
            **kwargs: Additional arguments passed to uvicorn.run
        """
        host = host or self.config.host
        port = port or self.config.port
        log_level = (log_level or self.config.log_level).lower()
        
        # Print startup information
        self._print_startup_info(host, port)
        
        # Run server
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level=log_level,
            **kwargs
        )
    
    def _print_startup_info(self, host: str, port: int) -> None:
        """Print server startup information"""
        print(f"\n🚀 Starting Unified Server on http://{host}:{port}")
        print(f"📦 Server: {self.config.name} v{self.config.version}\n")
        print(f"🔧 Registered {len(registry.tools)} tools")
        print(f"📚 Registered {len(registry.resources)} resources")
        print(f"💬 Registered {len(registry.prompts)} prompts\n")
        print("🌐 Endpoints:")
        print(f"   REST API:        http://{host}:{port}/")
        print(f"   API Docs:        http://{host}:{port}{self.config.docs_url}")
        print(f"   Health Check:    http://{host}:{port}/health")
        print(f"   MCP (JSON-RPC):  http://{host}:{port}{self.config.mcp_endpoint}")
        print(f"\n🔗 For Claude/Amazon Q with mcp-remote:")
        print(f'   "command": "npx"')
        print(f'   "args": ["mcp-remote", "http://{host}:{port}{self.config.mcp_endpoint}"]\n')


def create_server(
    name: str = "unified-server",
    version: str = "1.0.0",
    config: ServerConfig = None
) -> UnifiedServer:
    """
    Create and return a unified server instance
    
    Args:
        name: Server name
        version: Server version
        config: Server configuration (optional)
    
    Returns:
        UnifiedServer instance
    """
    return UnifiedServer(name=name, version=version, config=config)