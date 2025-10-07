"""
Utilities for function inspection and schema generation.
"""

import inspect
from typing import Any, Callable, Dict, get_type_hints


def get_parameter_schema(func: Callable) -> Dict[str, Any]:
    """
    Generate JSON schema for function parameters
    
    Args:
        func: Function to inspect
    
    Returns:
        JSON schema dictionary
    """
    sig = inspect.signature(func)
    properties = {}
    required = []
    
    # Try to get type hints with proper error handling
    try:
        hints = get_type_hints(func)
    except (TypeError, AttributeError, NameError, ImportError):
        # Handle various exceptions that can occur during type hint extraction
        hints = {}
    
    for param_name, param in sig.parameters.items():
        # Skip self and cls parameters
        if param_name in ('self', 'cls'):
            continue
        
        # Determine parameter type
        param_type = "string"  # default
        
        # Check type hints first
        if param_name in hints:
            hint = hints[param_name]
            param_type = _python_type_to_json_type(hint)
        # Fall back to annotation
        elif param.annotation != inspect.Parameter.empty:
            param_type = _python_type_to_json_type(param.annotation)
        
        properties[param_name] = {
            "type": param_type
        }
        
        # Add description from docstring if available
        doc = inspect.getdoc(func)
        if doc:
            # Simple extraction - could be enhanced
            properties[param_name]["description"] = f"Parameter {param_name}"
        
        # Mark as required if no default value
        if param.default == inspect.Parameter.empty:
            required.append(param_name)
    
    schema = {
        "type": "object",
        "properties": properties
    }
    
    if required:
        schema["required"] = required
    
    return schema


def _python_type_to_json_type(python_type: Any) -> str:
    """
    Convert Python type to JSON schema type
    
    Args:
        python_type: Python type annotation
    
    Returns:
        JSON schema type string
    """
    try:
        # Handle basic types
        if python_type == int:
            return "integer"
        elif python_type == float:
            return "number"
        elif python_type == bool:
            return "boolean"
        elif python_type == str:
            return "string"
        elif python_type == list:
            return "array"
        elif python_type == dict:
            return "object"
        
        # Handle typing module types
        type_str = str(python_type)
        
        if "list" in type_str.lower() or "List" in type_str:
            return "array"
        elif "dict" in type_str.lower() or "Dict" in type_str:
            return "object"
        elif "int" in type_str.lower():
            return "integer"
        elif "float" in type_str.lower():
            return "number"
        elif "bool" in type_str.lower():
            return "boolean"
        
        # Default to string
        return "string"
    except Exception:
        # Fallback to string if type conversion fails
        return "string"


def is_async_function(func: Callable) -> bool:
    """
    Check if a function is async
    
    Args:
        func: Function to check
    
    Returns:
        True if function is async, False otherwise
    """
    return inspect.iscoroutinefunction(func)


def get_function_description(func: Callable) -> str:
    """
    Get function description from docstring
    
    Args:
        func: Function to inspect
    
    Returns:
        Function description (sanitized)
    """
    doc = inspect.getdoc(func)
    if doc:
        # Return first line of docstring, sanitized
        first_line = doc.split('\n')[0].strip()
        # Remove potentially dangerous characters to prevent XSS
        sanitized = first_line.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#x27;')
        return sanitized[:200]  # Limit length
    
    # Sanitize function name too
    safe_name = func.__name__.replace('<', '&lt;').replace('>', '&gt;')[:50]
    return f"Function {safe_name}"