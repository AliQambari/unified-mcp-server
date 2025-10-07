"""
Resource decorator for registering functions as resources.
"""

from typing import Callable, Optional

from ..core.registry import registry
from ..utils.inspection import get_function_description


def resource(
    uri: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    mime_type: str = "text/plain"
) -> Callable:
    """
    Decorator to expose a function as both API endpoint and MCP resource
    
    Args:
        uri: Resource URI (e.g., "config://app")
        name: Resource name (defaults to function name)
        description: Resource description (defaults to function docstring)
        mime_type: MIME type of the resource content
    
    Returns:
        Decorated function
    
    Example:
        @resource(uri="config://app", description="App configuration")
        def get_config():
            return {"theme": "dark"}
    """
    def decorator(func: Callable) -> Callable:
        resource_name = name or func.__name__
        resource_description = description or get_function_description(func)
        
        # Register the resource
        registry.register_resource(
            name=resource_name,
            function=func,
            uri=uri,
            description=resource_description,
            mime_type=mime_type
        )
        
        return func
    
    return decorator