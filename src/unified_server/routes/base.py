"""
Base routes for the unified server.
"""

from fastapi import APIRouter

from ..core.registry import registry
from ..core.config import ServerConfig


def create_base_router(config: ServerConfig) -> APIRouter:
    """
    Create base router with root endpoint
    
    Args:
        config: Server configuration
    
    Returns:
        APIRouter instance
    """
    router = APIRouter()
    
    @router.get("/")
    async def root():
        """Root endpoint with server information"""
        return {
            "name": config.name,
            "version": config.version,
            "tools": list(registry.tools.keys()),
            "resources": list(registry.resources.keys()),
            "prompts": list(registry.prompts.keys()),
            "endpoints": {
                "rest_api": {
                    "tools": "/tools",
                    "resources": "/resources",
                    "prompts": "/prompts",
                    "docs": config.docs_url
                },
                "mcp": {
                    "endpoint": f"{config.mcp_endpoint} (POST for JSON-RPC)"
                }
            }
        }
    
    @router.get("/health")
    async def health():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "tools": len(registry.tools),
            "resources": len(registry.resources),
            "prompts": len(registry.prompts)
        }
    
    return router