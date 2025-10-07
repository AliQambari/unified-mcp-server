"""
Routes for prompt management and generation.
"""

from typing import Dict, Optional

from fastapi import APIRouter, HTTPException

from ..core.registry import registry
from ..utils.logging import get_logger
from ..utils.inspection import is_async_function


logger = get_logger("routes.prompts")


def create_prompts_router() -> APIRouter:
    """
    Create router for prompt endpoints
    
    Returns:
        APIRouter instance
    """
    router = APIRouter(prefix="/prompts", tags=["prompts"])
    
    @router.get("")
    async def list_prompts():
        """List all available prompts"""
        return {
            "prompts": [
                {
                    "name": name,
                    "description": info.description,
                    "arguments": info.arguments
                }
                for name, info in registry.prompts.items()
            ]
        }
    
    @router.post("/{prompt_name}")
    async def get_prompt(prompt_name: str, arguments: Optional[Dict[str, str]] = None):
        """Get a prompt with given arguments"""
        # Validate prompt name
        if not prompt_name or len(prompt_name) > 100:
            raise HTTPException(status_code=400, detail="Invalid prompt name")
        
        # Validate arguments to prevent mass assignment
        if arguments:
            if len(arguments) > 20:  # Limit number of arguments
                raise HTTPException(status_code=400, detail="Too many arguments")
            for key, value in arguments.items():
                if len(str(key)) > 50 or len(str(value)) > 1000:
                    raise HTTPException(status_code=400, detail="Argument too large")
        
        # Sanitize logging to prevent injection
        safe_prompt_name = prompt_name.replace('\n', '').replace('\r', '')[:50]
        logger.info(f"REST API - Getting prompt: {safe_prompt_name}")
        if arguments:
            safe_args = str(arguments)[:200].replace('\n', '').replace('\r', '')
            logger.info(f"   Arguments: {safe_args}")
        
        prompt_info = registry.get_prompt(prompt_name)
        if not prompt_info:
            logger.warning(f"Prompt not found: {safe_prompt_name}")
            raise HTTPException(status_code=404, detail=f"Prompt not found")
        
        try:
            # Validate arguments size
            if arguments and len(str(arguments)) > 10000:  # 10KB limit
                raise HTTPException(status_code=413, detail="Arguments too large")
                
            if is_async_function(prompt_info.function):
                result = await prompt_info.function(**(arguments or {}))
            else:
                result = prompt_info.function(**(arguments or {}))
            
            logger.info(f"Prompt {safe_prompt_name} generated successfully")
            return {
                "messages": result,
                "description": prompt_info.description
            }
        except TypeError as e:
            error_msg = str(e)[:100]
            logger.error(f"Invalid arguments for prompt {safe_prompt_name}: {error_msg}")
            raise HTTPException(
                status_code=400,
                detail=f"Invalid arguments: {error_msg}"
            )
        except Exception as e:
            error_msg = str(e)[:100]
            logger.error(f"Prompt {safe_prompt_name} failed: {error_msg}")
            raise HTTPException(status_code=500, detail=f"Prompt execution failed: {error_msg}")
    
    @router.get("/{prompt_name}")
    async def get_prompt_info(prompt_name: str):
        """Get information about a specific prompt"""
        prompt_info = registry.get_prompt(prompt_name)
        if not prompt_info:
            raise HTTPException(status_code=404, detail=f"Prompt '{prompt_name}' not found")
        
        return {
            "name": prompt_name,
            "description": prompt_info.description,
            "arguments": prompt_info.arguments
        }
    
    return router