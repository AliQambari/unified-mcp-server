"""
Prompt decorator for registering functions as prompts.
"""

from typing import Callable, Dict, List, Optional

from ..core.registry import registry
from ..utils.inspection import get_function_description


def prompt(
    name: Optional[str] = None,
    description: Optional[str] = None,
    arguments: Optional[List[Dict[str, str]]] = None
) -> Callable:
    """
    Decorator to expose a function as both API endpoint and MCP prompt
    
    Args:
        name: Prompt name (defaults to function name)
        description: Prompt description (defaults to function docstring)
        arguments: List of argument definitions
    
    Returns:
        Decorated function
    
    Example:
        @prompt(description="Generate a greeting")
        def greeting_prompt(name: str):
            return [{
                "role": "user",
                "content": {"type": "text", "text": f"Hello {name}"}
            }]
    """
    def decorator(func: Callable) -> Callable:
        prompt_name = name or func.__name__
        prompt_description = description or get_function_description(func)
        prompt_arguments = arguments or []
        
        # Register the prompt
        registry.register_prompt(
            name=prompt_name,
            function=func,
            description=prompt_description,
            arguments=prompt_arguments
        )
        
        return func
    
    return decorator