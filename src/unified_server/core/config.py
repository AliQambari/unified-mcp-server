"""
Configuration management for the unified server.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ServerConfig:
    """Server configuration"""
    name: str = "unified-server"
    version: str = "1.0.0"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    
    # CORS settings
    cors_enabled: bool = False
    cors_origins: list[str] | None = None
    
    # API settings
    api_prefix: str = ""
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    
    # MCP settings
    mcp_endpoint: str = "/mcp"
    mcp_protocol_version: str = "2024-11-05"
    
    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create config from environment variables"""
        import os
        
        try:
            port = int(os.getenv("SERVER_PORT", "8000"))
        except (ValueError, TypeError):
            port = 8000  # Fallback to default
            
        return cls(
            name=os.getenv("SERVER_NAME", "unified-server"),
            version=os.getenv("SERVER_VERSION", "1.0.0"),
            host=os.getenv("SERVER_HOST", "0.0.0.0"),
            port=port,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )


@dataclass
class MCPCapabilities:
    """MCP server capabilities"""
    tools: dict = None
    resources: dict = None
    prompts: dict = None
    
    def __post_init__(self):
        if self.tools is None:
            self.tools = {}
        if self.resources is None:
            self.resources = {}
        if self.prompts is None:
            self.prompts = {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MCP response"""
        return {
            "tools": self.tools,
            "resources": self.resources,
            "prompts": self.prompts
        }