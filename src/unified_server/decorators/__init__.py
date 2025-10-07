"""Decorators for registering tools, resources, and prompts"""

from .tool import tool
from .resource import resource
from .resource_template import resource_template
from .prompt import prompt

__all__ = ["tool", "resource", "resource_template", "prompt"]