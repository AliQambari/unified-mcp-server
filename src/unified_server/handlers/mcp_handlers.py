"""
MCP server handlers for STDIO mode (optional, for future use).
"""

from typing import Any, Dict, List

from mcp.server import Server
from mcp.types import Tool, TextContent, Resource

from ..core.registry import registry
from ..utils.inspection import is_async_function
from ..utils.logging import get_logger

logger = get_logger("handlers.mcp")


def setup_mcp_handlers(mcp_server: Server) -> None:
    """
    Setup MCP server handlers for STDIO mode
    
    Args:
        mcp_server: MCP Server instance
    """
    
    @mcp_server.list_tools()
    async def list_tools() -> List[Tool]:
        """List all available tools"""
        return [
            Tool(
                name=name,
                description=info.description,
                inputSchema=info.parameters
            )
            for name, info in registry.tools.items()
        ]
    
    @mcp_server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        """Call a tool with given arguments"""
        try:
            tool_info = registry.get_tool(name)
            if not tool_info:
                raise ValueError(f"Tool '{name}' not found")
            
            if is_async_function(tool_info.function):
                result = await tool_info.function(**arguments)
            else:
                result = tool_info.function(**arguments)
            
            return [TextContent(type="text", text=str(result))]
        except Exception as e:
            # Log error and re-raise with sanitized message
            error_msg = str(e)[:100].replace('\n', '').replace('\r', '')
            safe_name = name.replace('\n', '').replace('\r', '')[:50] if name else 'unknown'
            logger.error(f"Tool execution failed for {safe_name}: {error_msg}")
            raise ValueError(f"Tool execution failed: {error_msg}")
    
    @mcp_server.list_resources()
    async def list_resources() -> List[Resource]:
        """List all available resources"""
        return [
            Resource(
                uri=info.uri,
                name=name,
                description=info.description,
                mimeType=info.mime_type
            )
            for name, info in registry.resources.items()
        ]
    
    @mcp_server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read a resource by URI"""
        try:
            resource_info = registry.get_resource_by_uri(uri)
            if not resource_info:
                raise ValueError(f"Resource with URI '{uri}' not found")
            
            if is_async_function(resource_info.function):
                result = await resource_info.function()
            else:
                result = resource_info.function()
            
            return str(result)
        except Exception as e:
            # Log error and re-raise with sanitized message
            safe_uri = uri.replace('\n', '').replace('\r', '')[:100] if uri else 'None'
            logger.error(f"Resource read failed for {safe_uri}: {str(e)[:100]}")
            raise ValueError(f"Resource read failed: {str(e)[:100]}")