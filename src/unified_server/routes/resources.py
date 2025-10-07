"""
Routes for resource management and reading.
"""

from fastapi import APIRouter, HTTPException

from ..core.registry import registry
from ..utils.logging import get_logger
from ..utils.inspection import is_async_function


logger = get_logger("routes.resources")


def create_resources_router() -> APIRouter:
    """
    Create router for resource endpoints
    
    Returns:
        APIRouter instance
    """
    router = APIRouter(prefix="/resources", tags=["resources"])
    
    @router.get("")
    async def list_resources():
        """List all available resources"""
        return {
            "resources": [
                {
                    "uri": info.uri,
                    "name": name,
                    "description": info.description,
                    "mimeType": info.mime_type
                }
                for name, info in registry.resources.items()
            ]
        }
    
    @router.get("/{resource_name}")
    async def read_resource(resource_name: str):
        """Read a resource by name"""
        # Validate and sanitize resource name
        if not resource_name or len(resource_name) > 100:
            raise HTTPException(status_code=400, detail="Invalid resource name")
        
        # Sanitize for XSS prevention
        safe_resource_name = resource_name.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')[:50]
        logger.info(f"REST API - Reading resource: {safe_resource_name}")
        
        resource_info = registry.get_resource(resource_name)
        if not resource_info:
            logger.warning(f"Resource not found: {safe_resource_name}")
            raise HTTPException(status_code=404, detail=f"Resource not found")
        
        try:
            if is_async_function(resource_info.function):
                result = await resource_info.function()
            else:
                result = resource_info.function()
            
            logger.info(f"Resource {safe_resource_name} read successfully")
            return {
                "content": result,
                "uri": resource_info.uri,
                "mimeType": resource_info.mime_type
            }
        except Exception as e:
            error_msg = str(e)[:100]
            logger.error(f"Resource {safe_resource_name} failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Resource read failed: {error_msg}")
    
    @router.get("/by-uri/{uri:path}")
    async def read_resource_by_uri(uri: str):
        """Read a resource by URI"""
        # Validate and sanitize URI
        if not uri or len(uri) > 500:
            raise HTTPException(status_code=400, detail="Invalid URI")
            
        # Sanitize for XSS prevention
        safe_uri = uri.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')[:100]
        logger.info(f"REST API - Reading resource by URI: {safe_uri}")
        
        resource_info = registry.get_resource_by_uri(uri)
        if not resource_info:
            logger.warning(f"Resource not found for URI: {safe_uri}")
            raise HTTPException(status_code=404, detail=f"Resource not found")
        
        try:
            if is_async_function(resource_info.function):
                result = await resource_info.function()
            else:
                result = resource_info.function()
            
            logger.info(f"Resource read successfully")
            return {
                "content": result,
                "uri": resource_info.uri,
                "mimeType": resource_info.mime_type
            }
        except Exception as e:
            error_msg = str(e)[:100]
            logger.error(f"Resource failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Resource read failed: {error_msg}")
    
    return router