"""
Complete REST API for exposing MCP tools, resources, templates, and prompts.

All MCP functionality available via standard REST endpoints.
"""

from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import re

from ..core.registry import registry
from ..utils.logging import get_logger
from ..utils.inspection import is_async_function

logger = get_logger("routes.api")


# =============================================================================
# REQUEST/RESPONSE MODELS
# =============================================================================

class ToolExecuteRequest(BaseModel):
    """Request to execute a tool"""
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")

    model_config = {
        "json_schema_extra": {
            "examples": [{"arguments": {"a": 5, "b": 3}}]
        }
    }


class ToolInfo(BaseModel):
    """Tool information"""
    name: str
    description: str
    parameters: Dict[str, Any]


class ToolListResponse(BaseModel):
    """Response with list of tools"""
    tools: List[ToolInfo]
    count: int


class ToolExecuteResponse(BaseModel):
    """Response from tool execution"""
    success: bool
    result: Any
    tool_name: str


class ResourceInfo(BaseModel):
    """Resource information"""
    name: str
    uri: str
    description: str
    mime_type: str


class ResourceTemplateInfo(BaseModel):
    """Resource template information"""
    name: str
    uri_template: str
    description: str
    mime_type: str
    parameters: List[Dict[str, Any]]


class ResourceListResponse(BaseModel):
    """Response with list of resources"""
    resources: List[ResourceInfo]
    count: int


class ResourceTemplateListResponse(BaseModel):
    """Response with list of resource templates"""
    templates: List[ResourceTemplateInfo]
    count: int


class ResourceTemplateReadRequest(BaseModel):
    """Request to read a resource template with parameters"""
    parameters: Dict[str, str] = Field(default_factory=dict, description="Template parameters")

    model_config = {
        "json_schema_extra": {
            "examples": [{"parameters": {"user_id": "123", "file_name": "profile.json"}}]
        }
    }


class ResourceReadResponse(BaseModel):
    """Response from reading a resource"""
    success: bool
    uri: str
    content: Any
    mime_type: str


class PromptArgument(BaseModel):
    """Prompt argument definition"""
    name: str
    description: str
    required: bool


class PromptInfo(BaseModel):
    """Prompt information"""
    name: str
    description: str
    arguments: List[Dict[str, Any]]


class PromptListResponse(BaseModel):
    """Response with list of prompts"""
    prompts: List[PromptInfo]
    count: int


class PromptExecuteRequest(BaseModel):
    """Request to execute a prompt"""
    arguments: Dict[str, str] = Field(default_factory=dict, description="Prompt arguments")

    model_config = {
        "json_schema_extra": {
            "examples": [{"arguments": {"language": "python"}}]
        }
    }


class PromptExecuteResponse(BaseModel):
    """Response from prompt execution"""
    success: bool
    prompt_name: str
    description: str
    messages: List[Dict[str, Any]]


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    status_code: int


# =============================================================================
# ROUTER CREATION
# =============================================================================

def create_api_router() -> APIRouter:
    """Create REST API router"""
    router = APIRouter(prefix="/api", tags=["REST API"])

    # =========================================================================
    # TOOLS
    # =========================================================================

    @router.get(
        "/tools",
        response_model=ToolListResponse,
        summary="List all tools",
        description="Get a list of all registered tools with their descriptions and parameters"
    )
    async def list_tools():
        """List all available tools"""
        logger.info("API - List tools")
        tools = [
            ToolInfo(name=name, description=info.description, parameters=info.parameters)
            for name, info in registry.tools.items()
        ]
        return ToolListResponse(tools=tools, count=len(tools))

    @router.get(
        "/tools/{tool_name}",
        response_model=ToolInfo,
        summary="Get tool information",
        description="Get detailed information about a specific tool by name"
    )
    async def get_tool_info(tool_name: str):
        """Get tool information"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', tool_name):
            raise HTTPException(status_code=400, detail="Invalid tool name")

        logger.info(f"API - Get tool info: {tool_name}")
        tool_info = registry.get_tool(tool_name)
        if not tool_info:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

        return ToolInfo(
            name=tool_name,
            description=tool_info.description,
            parameters=tool_info.parameters
        )

    @router.post(
        "/tools/{tool_name}",
        response_model=ToolExecuteResponse,
        summary="Execute a tool",
        description="Execute the named tool with provided arguments and return the result"
    )
    async def execute_tool(tool_name: str, request: ToolExecuteRequest):
        """Execute a tool"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', tool_name):
            raise HTTPException(status_code=400, detail="Invalid tool name")

        if len(str(request.arguments)) > 10000:
            raise HTTPException(status_code=413, detail="Arguments too large")

        tool_info = registry.get_tool(tool_name)
        if not tool_info:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

        try:
            result = (
                await tool_info.function(**request.arguments)
                if is_async_function(tool_info.function)
                else tool_info.function(**request.arguments)
            )
            logger.info(f"API - Tool {tool_name} executed successfully")
            return ToolExecuteResponse(success=True, result=result, tool_name=tool_name)
        except TypeError as e:
            logger.error(f"API - Invalid arguments for {tool_name}: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid arguments: {str(e)}")
        except Exception as e:
            logger.error(f"API - Tool {tool_name} execution failed: {e}")
            raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)[:200]}")

    # =========================================================================
    # RESOURCES
    # =========================================================================

    @router.get(
        "/resources",
        response_model=ResourceListResponse,
        summary="List all resources",
        description="Get a list of all registered resources with their metadata"
    )
    async def list_resources():
        """List all resources"""
        logger.info("API - List resources")
        resources = [
            ResourceInfo(
                name=name,
                uri=info.uri,
                description=info.description,
                mime_type=info.mime_type
            )
            for name, info in registry.resources.items()
        ]
        return ResourceListResponse(resources=resources, count=len(resources))

    @router.get(
        "/resources/{resource_name}",
        response_model=ResourceReadResponse,
        summary="Read a resource by name",
        description="Read the content of a resource by its registered name"
    )
    async def read_resource_by_name(resource_name: str):
        """Read a resource by name"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', resource_name):
            raise HTTPException(status_code=400, detail="Invalid resource name")

        resource_info = registry.get_resource(resource_name)
        if not resource_info:
            raise HTTPException(status_code=404, detail=f"Resource '{resource_name}' not found")

        try:
            content = (
                await resource_info.function()
                if is_async_function(resource_info.function)
                else resource_info.function()
            )
            logger.info(f"API - Resource {resource_name} read successfully")
            return ResourceReadResponse(
                success=True,
                uri=resource_info.uri,
                content=content,
                mime_type=resource_info.mime_type
            )
        except Exception as e:
            logger.error(f"API - Resource {resource_name} read failed: {e}")
            raise HTTPException(status_code=500, detail=f"Resource read failed: {str(e)[:200]}")

    @router.get(
        "/resources/by-uri",
        response_model=ResourceReadResponse,
        summary="Read a resource by URI",
        description="Read the content of a resource using its exact URI"
    )
    async def read_resource_by_uri(uri: str):
        """Read resource by URI"""
        if not uri or len(uri) > 500:
            raise HTTPException(status_code=400, detail="Invalid URI")

        resource_info = registry.get_resource_by_uri(uri)
        if not resource_info:
            raise HTTPException(status_code=404, detail=f"Resource with URI '{uri}' not found")

        try:
            content = (
                await resource_info.function()
                if is_async_function(resource_info.function)
                else resource_info.function()
            )
            logger.info(f"API - Resource read by URI succeeded")
            return ResourceReadResponse(
                success=True,
                uri=uri,
                content=content,
                mime_type=resource_info.mime_type
            )
        except Exception as e:
            logger.error(f"API - Resource read by URI failed: {e}")
            raise HTTPException(status_code=500, detail=f"Resource read failed: {str(e)[:200]}")

    # =========================================================================
    # RESOURCE TEMPLATES
    # =========================================================================

    @router.get(
        "/resource-templates",
        response_model=ResourceTemplateListResponse,
        summary="List all resource templates",
        description="Get a list of registered resource templates and their parameters"
    )
    async def list_resource_templates():
        """List all resource templates"""
        logger.info("API - List resource templates")
        templates = [
            ResourceTemplateInfo(
                name=name,
                uri_template=info.uri_template,
                description=info.description,
                mime_type=info.mime_type,
                parameters=info.parameters
            )
            for name, info in registry.resource_templates.items()
        ]
        return ResourceTemplateListResponse(templates=templates, count=len(templates))

    @router.get(
        "/resource-templates/{template_name}",
        response_model=ResourceTemplateInfo,
        summary="Get resource template information",
        description="Get detailed info for a specific resource template (URI template, parameters, mime type)"
    )
    async def get_resource_template_info(template_name: str):
        """Get resource template information"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', template_name):
            raise HTTPException(status_code=400, detail="Invalid template name")

        template_info = registry.get_resource_template(template_name)
        if not template_info:
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

        return ResourceTemplateInfo(
            name=template_name,
            uri_template=template_info.uri_template,
            description=template_info.description,
            mime_type=template_info.mime_type,
            parameters=template_info.parameters
        )

    @router.post(
        "/resource-templates/{template_name}",
        response_model=ResourceReadResponse,
        summary="Read a resource template with parameters",
        description="Resolve a resource template with provided parameters, execute its function, and return content"
    )
    async def read_resource_template(template_name: str, request: ResourceTemplateReadRequest):
        """Read resource template with parameters"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', template_name):
            raise HTTPException(status_code=400, detail="Invalid template name")

        if len(str(request.parameters)) > 5000:
            raise HTTPException(status_code=413, detail="Parameters too large")

        template_info = registry.get_resource_template(template_name)
        if not template_info:
            raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

        try:
            # Resolve uri_template using provided parameters (may raise KeyError if missing)
            resolved_uri = template_info.uri_template.format(**request.parameters)

            content = (
                await template_info.function(**request.parameters)
                if is_async_function(template_info.function)
                else template_info.function(**request.parameters)
            )
            logger.info(f"API - Resource template {template_name} read successfully")
            return ResourceReadResponse(
                success=True,
                uri=resolved_uri,
                content=content,
                mime_type=template_info.mime_type
            )
        except KeyError as e:
            logger.error(f"API - Missing parameter for template {template_name}: {e}")
            raise HTTPException(status_code=400, detail=f"Missing template parameter: {e}")
        except Exception as e:
            logger.error(f"API - Template read failed for {template_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Template read failed: {str(e)[:200]}")

    # =========================================================================
    # PROMPTS
    # =========================================================================

    @router.get(
        "/prompts",
        response_model=PromptListResponse,
        summary="List all prompts",
        description="Get a list of all registered prompts with their metadata"
    )
    async def list_prompts():
        """List all prompts"""
        logger.info("API - List prompts")
        prompts = [
            PromptInfo(
                name=name,
                description=info.description,
                arguments=info.arguments
            )
            for name, info in registry.prompts.items()
        ]
        return PromptListResponse(prompts=prompts, count=len(prompts))

    @router.get(
        "/prompts/{prompt_name}",
        response_model=PromptInfo,
        summary="Get prompt information",
        description="Get detailed information about a specific prompt"
    )
    async def get_prompt_info(prompt_name: str):
        """Get prompt information"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', prompt_name):
            raise HTTPException(status_code=400, detail="Invalid prompt name")

        prompt_info = registry.get_prompt(prompt_name)
        if not prompt_info:
            raise HTTPException(status_code=404, detail=f"Prompt '{prompt_name}' not found")

        return PromptInfo(
            name=prompt_name,
            description=prompt_info.description,
            arguments=prompt_info.arguments
        )

    @router.post(
        "/prompts/{prompt_name}",
        response_model=PromptExecuteResponse,
        summary="Execute a prompt",
        description="Execute the named prompt with provided arguments and return generated messages"
    )
    async def execute_prompt(prompt_name: str, request: PromptExecuteRequest):
        """Execute a prompt"""
        if not re.match(r'^[a-zA-Z0-9_-]+$', prompt_name):
            raise HTTPException(status_code=400, detail="Invalid prompt name")

        if len(str(request.arguments)) > 10000:
            raise HTTPException(status_code=413, detail="Arguments too large")

        prompt_info = registry.get_prompt(prompt_name)
        if not prompt_info:
            raise HTTPException(status_code=404, detail=f"Prompt '{prompt_name}' not found")

        try:
            messages = (
                await prompt_info.function(**request.arguments)
                if is_async_function(prompt_info.function)
                else prompt_info.function(**request.arguments)
            )
            logger.info(f"API - Prompt {prompt_name} executed successfully")
            return PromptExecuteResponse(
                success=True,
                prompt_name=prompt_name,
                description=prompt_info.description,
                messages=messages
            )
        except TypeError as e:
            logger.error(f"API - Invalid arguments for prompt {prompt_name}: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid arguments: {str(e)}")
        except Exception as e:
            logger.error(f"API - Prompt {prompt_name} execution failed: {e}")
            raise HTTPException(status_code=500, detail=f"Prompt execution failed: {str(e)[:200]}")

    # =========================================================================
    # STATUS
    # =========================================================================

    @router.get(
        "/status",
        summary="Get API status",
        description="Get the status of the REST API and registry statistics"
    )
    async def get_status():
        """Get API status"""
        return {
            "status": "operational",
            "statistics": {
                "tools": len(registry.tools),
                "resources": len(registry.resources),
                "templates": len(registry.resource_templates),
                "prompts": len(registry.prompts)
            },
            "endpoints": {
                "tools": "/api/tools",
                "resources": "/api/resources",
                "templates": "/api/resource-templates",
                "prompts": "/api/prompts",
                "docs": "/docs"
            }
        }

    return router
