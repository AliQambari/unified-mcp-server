"""API route handlers"""

from .base import create_base_router
from .tools import create_tools_router
from .resources import create_resources_router
from .prompts import create_prompts_router
from .mcp import create_mcp_router

__all__ = [
    "create_base_router",
    "create_tools_router",
    "create_resources_router",
    "create_prompts_router",
    "create_mcp_router",
]