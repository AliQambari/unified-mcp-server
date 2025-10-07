"""
Routes for tool management and execution.
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from ..core.registry import registry
from ..utils.logging import get_logger
from ..utils.inspection import is_async_function


logger = get_logger("routes.tools")


def create_tools_router() -> APIRouter:
    """
    Create router for tool endpoints
    
    Returns:
        APIRouter instance
    """
    router = APIRouter(prefix="/tools", tags=["tools"])
    
    @router.get("")
    async def list_tools():
        """List all available tools"""
        return {
            "tools": [
                {
                    "name": name,
                    "description": info.description,
                    "parameters": info.parameters
                }
                for name, info in registry.tools.items()
            ]
        }
    
    @router.post("/{tool_name}")
    async def execute_tool(tool_name: str, params: Dict[str, Any]):
        """Execute a tool with given parameters"""
        # Sanitize logging to prevent injection
        safe_tool_name = tool_name.replace('\n', '').replace('\r', '')[:50]
        safe_params = str(params)[:200].replace('\n', '').replace('\r', '')
        logger.info(f"REST API - Executing tool: {safe_tool_name} with params: {safe_params}")
        
        tool_info = registry.get_tool(tool_name)
        if not tool_info:
            logger.warning(f"Tool not found: {safe_tool_name}")
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        try:
            # Validate params size
            if len(str(params)) > 10000:  # 10KB limit
                raise HTTPException(status_code=413, detail="Parameters too large")
                
            if is_async_function(tool_info.function):
                result = await tool_info.function(**params)
            else:
                result = tool_info.function(**params)
            
            logger.info(f"Tool {safe_tool_name} completed successfully")
            return {"result": result}
        except TypeError as e:
            error_msg = str(e)[:100]
            logger.error(f"Invalid parameters for tool {safe_tool_name}: {error_msg}")
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid parameters: {error_msg}"
            )
        except Exception as e:
            error_msg = str(e)[:100]
            logger.error(f"Tool {safe_tool_name} failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Tool execution failed: {error_msg}")
    
    @router.get("/{tool_name}")
    async def get_tool_info(tool_name: str):
        """Get information about a specific tool"""
        tool_info = registry.get_tool(tool_name)
        if not tool_info:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        
        return {
            "name": tool_name,
            "description": tool_info.description,
            "parameters": tool_info.parameters
        }
    
    return router