"""
Tool decorator for registering functions as tools.
"""

from typing import Any, Callable, Dict, Optional

from ..core.registry import registry
from ..utils.inspection import get_parameter_schema, get_function_description


def tool(
    name: Optional[str] = None,
    description: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None
) -> Callable:
    """
    Decorator to expose a function as both API endpoint and MCP tool
    
    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to function docstring)
        parameters: JSON schema for parameters (auto-generated if not provided)
    
    Returns:
        Decorated function
    
    Example:
        @tool(description="Add two numbers")
        def add(a: int, b: int) -> int:
            return a + b
    """
    def decorator(func: Callable) -> Callable:
        try:
            tool_name = name or func.__name__
            tool_description = description or get_function_description(func)
            
            # Generate parameter schema if not provided
            if parameters is None:
                param_schema = get_parameter_schema(func)
            else:
                param_schema = parameters
            
            # Register the tool
            registry.register_tool(
                name=tool_name,
                function=func,
                description=tool_description,
                parameters=param_schema
            )
        except Exception as e:
            # Log error but don't fail the decorator
            import logging
            logger = logging.getLogger("unified_server.decorators.tool")
            logger.error(f"Failed to register tool {func.__name__}: {str(e)[:100]}")
        
        return func
    
    return decorator