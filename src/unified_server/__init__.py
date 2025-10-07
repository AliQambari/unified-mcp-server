"""
Unified API & MCP over HTTP Server

A unified server that exposes tools and resources as both REST API and MCP over HTTP.
"""

from .core.server import UnifiedServer, create_server
from .core.config import ServerConfig
from .core.registry import registry
from .decorators.tool import tool
from .decorators.resource import resource
from .decorators.resource_template import resource_template
from .decorators.prompt import prompt

__version__ = "1.0.0"
__all__ = [
    "UnifiedServer",
    "create_server",
    "ServerConfig",
    "registry",
    "tool",
    "resource",
    "resource_template",
    "prompt",
]