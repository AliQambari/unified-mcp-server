"""
Resource template decorator for registering parameterized resources.
"""

from typing import Callable, Optional, List, Dict

from ..core.registry import registry
from ..utils.inspection import get_function_description


def resource_template(
    uri_template: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    mime_type: str = "text/plain",
    parameters: Optional[List[Dict[str, str]]] = None
) -> Callable:
    """
    Decorator to expose a function as a resource template with parameters.
    
    Resource templates allow dynamic URI generation with parameters.
    
    Args:
        uri_template: URI template with parameters (e.g., "file://user/{user_id}/profile")
        name: Resource template name (defaults to function name)
        description: Resource template description (defaults to function docstring)
        mime_type: MIME type of the resource content
        parameters: List of parameter definitions with name, description, required
    
    Returns:
        Decorated function
    
    Example:
        @resource_template(
            uri_template="file://user/{user_id}/profile",
            description="User profile data",
            parameters=[
                {"name": "user_id", "description": "User ID", "required": True}
            ]
        )
        def get_user_profile(user_id: str):
            return {"user_id": user_id, "name": f"User {user_id}"}
    """
    def decorator(func: Callable) -> Callable:
        template_name = name or func.__name__
        template_description = description or get_function_description(func)
        template_parameters = parameters or []
        
        # Register the resource template
        registry.register_resource_template(
            name=template_name,
            function=func,
            uri_template=uri_template,
            description=template_description,
            mime_type=mime_type,
            parameters=template_parameters
        )
        
        return func
    
    return decorator