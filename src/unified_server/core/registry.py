"""
Central registry for tools, resources, and prompts.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict


@dataclass
class ToolInfo:
    """Information about a registered tool"""
    function: Callable
    description: str
    parameters: Dict[str, Any]


@dataclass
class ResourceInfo:
    """Information about a registered resource"""
    function: Callable
    uri: str
    description: str
    mime_type: str


@dataclass
class ResourceTemplateInfo:
    """Information about a registered resource template"""
    function: Callable
    uri_template: str  # e.g., "file://user/{user_id}/profile"
    description: str
    mime_type: str
    parameters: list[Dict[str, str]]  # Parameter definitions
    
    def resolve_uri(self, params: Dict[str, str]) -> str:
        """Resolve template URI with parameters"""
        uri = self.uri_template
        for key, value in params.items():
            uri = uri.replace(f"{{{key}}}", value)
        return uri


@dataclass
class PromptInfo:
    """Information about a registered prompt"""
    function: Callable
    description: str
    arguments: list[Dict[str, str]]


@dataclass
class UnifiedRegistry:
    """Central registry for tools, resources, and prompts"""
    tools: Dict[str, ToolInfo] = field(default_factory=dict)
    resources: Dict[str, ResourceInfo] = field(default_factory=dict)
    resource_templates: Dict[str, ResourceTemplateInfo] = field(default_factory=dict)
    prompts: Dict[str, PromptInfo] = field(default_factory=dict)
    
    def register_tool(
        self,
        name: str,
        function: Callable,
        description: str,
        parameters: Dict[str, Any]
    ) -> None:
        """Register a new tool"""
        self.tools[name] = ToolInfo(
            function=function,
            description=description,
            parameters=parameters
        )
    
    def register_resource(
        self,
        name: str,
        function: Callable,
        uri: str,
        description: str,
        mime_type: str
    ) -> None:
        """Register a new resource"""
        self.resources[name] = ResourceInfo(
            function=function,
            uri=uri,
            description=description,
            mime_type=mime_type
        )
    
    def register_resource_template(
        self,
        name: str,
        function: Callable,
        uri_template: str,
        description: str,
        mime_type: str,
        parameters: list[Dict[str, str]]
    ) -> None:
        """Register a new resource template"""
        self.resource_templates[name] = ResourceTemplateInfo(
            function=function,
            uri_template=uri_template,
            description=description,
            mime_type=mime_type,
            parameters=parameters
        )
    
    def get_resource_template(self, name: str) -> ResourceTemplateInfo | None:
        """Get a resource template by name"""
        return self.resource_templates.get(name)
    
    def list_resource_template_names(self) -> list[str]:
        """List all resource template names"""
        return list(self.resource_templates.keys())
    
    def register_prompt(
        self,
        name: str,
        function: Callable,
        description: str,
        arguments: list[Dict[str, str]]
    ) -> None:
        """Register a new prompt"""
        self.prompts[name] = PromptInfo(
            function=function,
            description=description,
            arguments=arguments
        )
    
    def get_tool(self, name: str) -> ToolInfo | None:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def get_resource(self, name: str) -> ResourceInfo | None:
        """Get a resource by name"""
        return self.resources.get(name)
    
    def get_resource_by_uri(self, uri: str) -> ResourceInfo | None:
        """Get a resource by URI"""
        for resource in self.resources.values():
            if resource.uri == uri:
                return resource
        return None
    
    def get_prompt(self, name: str) -> PromptInfo | None:
        """Get a prompt by name"""
        return self.prompts.get(name)
    
    def list_tool_names(self) -> list[str]:
        """List all tool names"""
        return list(self.tools.keys())
    
    def list_resource_names(self) -> list[str]:
        """List all resource names"""
        return list(self.resources.keys())
    
    def list_prompt_names(self) -> list[str]:
        """List all prompt names"""
        return list(self.prompts.keys())
    
    def clear(self) -> None:
        """Clear all registrations"""
        self.tools.clear()
        self.resources.clear()
        self.resource_templates.clear()
        self.prompts.clear()


# Global registry instance
registry = UnifiedRegistry()