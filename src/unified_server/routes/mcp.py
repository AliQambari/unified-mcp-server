"""
MCP endpoint with WebSocket and JSON-RPC support.

Transports:
- WebSocket: /mcp/ws (RECOMMENDED - bidirectional, low latency)
- HTTP POST: /mcp (JSON-RPC request/response)

Note: streamablehttp_client from MCP SDK has undocumented requirements that are
impractical to implement without SDK internals. Use WebSocket instead.
"""

import json
import asyncio
import re
from uuid import uuid4
from typing import Any, Dict, Optional

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from ..core.registry import registry
from ..core.config import ServerConfig, MCPCapabilities
from ..utils.logging import get_logger
from ..utils.inspection import is_async_function

logger = get_logger("routes.mcp")

# Validation models
class MCPMessage(BaseModel):
    jsonrpc: str = Field(default="2.0", pattern=r"^2\.0$")
    method: str = Field(..., min_length=1, max_length=100)
    params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    id: Optional[Any] = None
    
    @validator('method')
    def validate_method(cls, v):
        if not re.match(r'^[a-zA-Z0-9/_-]+$', v):
            raise ValueError('Invalid method name')
        return v

# Connection management
MAX_CONNECTIONS = 100
ws_connections: Dict[str, WebSocket] = {}


def create_mcp_router(config: ServerConfig) -> APIRouter:
    router = APIRouter(prefix=config.mcp_endpoint, tags=["mcp"])

    # =========================================================================
    # WEBSOCKET ENDPOINT (RECOMMENDED)
    # =========================================================================
    
    @router.websocket("/ws")
    async def mcp_websocket(websocket: WebSocket):
        """
        WebSocket transport for MCP protocol.
        
        Benefits over HTTP:
        - Bidirectional communication
        - Lower latency
        - True streaming support
        - Connection persistence
        
        Usage:
            ws = await websockets.connect("ws://localhost:8000/mcp/ws")
            await ws.send(json.dumps({"jsonrpc": "2.0", "method": "initialize", ...}))
            response = await ws.recv()
        """
        if len(ws_connections) >= MAX_CONNECTIONS:
            await websocket.close(code=1008)  # Policy violation
            return
        
        await websocket.accept()
        client_id = str(uuid4())
        ws_connections[client_id] = websocket
        
        logger.info(f"WebSocket client connected: {client_id[:8]}...")
        
        # Send welcome message
        await websocket.send_json({
            "type": "connection",
            "client_id": client_id,
            "protocol": "MCP over WebSocket"
        })
        
        try:
            while True:
                raw = await websocket.receive_text()
                
                # Validate message size
                if len(raw) > 1024 * 1024:  # 1MB
                    await websocket.send_json({
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32600, "message": "Message too large"}
                    })
                    continue
                
                # Parse and validate
                try:
                    raw_message = json.loads(raw)
                    validated = MCPMessage(**raw_message)
                    message = validated.dict()
                except json.JSONDecodeError:
                    await websocket.send_json({
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": "Parse error"}
                    })
                    continue
                except Exception as e:
                    await websocket.send_json({
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32600, "message": f"Invalid request: {str(e)}"}
                    })
                    continue
                
                # Process message
                response = await process_mcp_message(message, config)
                await websocket.send_json(response)
                
        except WebSocketDisconnect:
            logger.info(f"WebSocket client disconnected: {client_id[:8]}...")
        except Exception as e:
            logger.error(f"WebSocket error for {client_id[:8]}...: {e}")
        finally:
            ws_connections.pop(client_id, None)

    # =========================================================================
    # HTTP POST JSON-RPC ENDPOINT
    # =========================================================================
    
    @router.post("")
    async def mcp_jsonrpc(request: Request):
        """
        Synchronous JSON-RPC endpoint.
        
        Simple request/response pattern.
        Use WebSocket for better performance and streaming.
        
        Usage:
            response = requests.post(
                "http://localhost:8000/mcp",
                json={"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}
            )
        """
        try:
            # Validate size
            content_length = request.headers.get('content-length')
            if content_length and int(content_length) > 1024 * 1024:
                raise HTTPException(status_code=413, detail="Request too large")
            
            raw_message = await request.json()
            
            # Validate
            try:
                validated = MCPMessage(**raw_message)
                message = validated.dict()
            except Exception as e:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": raw_message.get("id") if isinstance(raw_message, dict) else None,
                    "error": {"code": -32600, "message": f"Invalid request: {str(e)}"}
                }, status_code=400)
            
            # Process
            response = await process_mcp_message(message, config)
            return JSONResponse(response)
            
        except Exception as e:
            logger.error(f"JSON-RPC error: {e}")
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": "Internal error"}
            }, status_code=500)

    return router


# =============================================================================
# MESSAGE PROCESSOR
# =============================================================================

async def process_mcp_message(message: Dict[str, Any], config: ServerConfig) -> Dict[str, Any]:
    """Process MCP JSON-RPC message and return response"""
    method = message.get("method")
    params = message.get("params", {})
    msg_id = message.get("id")
    
    # Sanitize for logging
    safe_method = method.replace('\n', '').replace('\r', '')[:50] if method else 'None'
    logger.info(f"MCP method: {safe_method}")
    
    try:
        # Route to handler
        if method == "initialize":
            result = await handle_initialize(config)
        elif method == "notifications/initialized":
            result = {}
        elif method == "ping":
            result = {}
        elif method == "tools/list":
            result = await handle_tools_list()
        elif method == "tools/call":
            result = await handle_tools_call(params)
        elif method == "resources/list":
            result = await handle_resources_list()
        elif method == "resources/read":
            result = await handle_resources_read(params)
        elif method == "resources/templates/list":
            result = {"resourceTemplates": []}
        elif method == "prompts/list":
            result = await handle_prompts_list()
        elif method == "prompts/get":
            result = await handle_prompts_get(params)
        else:
            return {
                "jsonrpc": "2.0",
                "id": msg_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }
        
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}
        
    except Exception as e:
        logger.error(f"Handler error: {str(e)[:200]}")
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {"code": -32603, "message": str(e)[:200]}
        }


# =============================================================================
# HANDLERS
# =============================================================================

async def handle_initialize(config: ServerConfig) -> Dict[str, Any]:
    logger.info("Initialize connection")
    return {
        "protocolVersion": config.mcp_protocol_version,
        "serverInfo": {"name": config.name, "version": config.version},
        "capabilities": MCPCapabilities().to_dict()
    }


async def handle_tools_list() -> Dict[str, Any]:
    logger.info(f"List tools: {len(registry.tools)}")
    return {
        "tools": [
            {
                "name": name,
                "description": info.description,
                "inputSchema": info.parameters
            }
            for name, info in registry.tools.items()
        ]
    }


async def handle_tools_call(params: Dict[str, Any]) -> Dict[str, Any]:
    tool_name = params.get("name")
    arguments = params.get("arguments", {})
    
    # Validate
    if not tool_name or len(tool_name) > 100:
        raise ValueError("Invalid tool name")
    if not re.match(r'^[a-zA-Z0-9_-]+$', tool_name):
        raise ValueError("Invalid tool name format")
    if len(str(arguments)) > 10000:
        raise ValueError("Arguments too large")
    
    logger.info(f"Call tool: {tool_name}")
    
    tool_info = registry.get_tool(tool_name)
    if not tool_info:
        raise ValueError(f"Tool not found: {tool_name}")
    
    try:
        if is_async_function(tool_info.function):
            result = await tool_info.function(**arguments)
        else:
            result = tool_info.function(**arguments)
    except Exception as e:
        raise ValueError(f"Tool execution failed: {str(e)[:200]}")
    
    return {"content": [{"type": "text", "text": str(result)}]}


async def handle_resources_list() -> Dict[str, Any]:
    logger.info(f"List resources: {len(registry.resources)}")
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


async def handle_resources_read(params: Dict[str, Any]) -> Dict[str, Any]:
    uri = params.get("uri")
    
    # Validate
    if not uri or len(uri) > 500:
        raise ValueError("Invalid URI")
    
    logger.info(f"Read resource: {uri[:100]}")
    
    resource_info = registry.get_resource_by_uri(uri)
    if not resource_info:
        raise ValueError(f"Resource not found: {uri}")
    
    try:
        if is_async_function(resource_info.function):
            content = await resource_info.function()
        else:
            content = resource_info.function()
    except Exception as e:
        raise ValueError(f"Resource read failed: {str(e)[:200]}")
    
    return {
        "contents": [{
            "uri": uri,
            "mimeType": resource_info.mime_type,
            "text": str(content)
        }]
    }


async def handle_prompts_list() -> Dict[str, Any]:
    logger.info(f"List prompts: {len(registry.prompts)}")
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


async def handle_prompts_get(params: Dict[str, Any]) -> Dict[str, Any]:
    prompt_name = params.get("name")
    arguments = params.get("arguments", {})
    
    # Validate
    if not prompt_name or len(prompt_name) > 100:
        raise ValueError("Invalid prompt name")
    if not re.match(r'^[a-zA-Z0-9_-]+$', prompt_name):
        raise ValueError("Invalid prompt name format")
    if len(str(arguments)) > 10000:
        raise ValueError("Arguments too large")
    
    logger.info(f"Get prompt: {prompt_name}")
    
    prompt_info = registry.get_prompt(prompt_name)
    if not prompt_info:
        raise ValueError(f"Prompt not found: {prompt_name}")
    
    try:
        if is_async_function(prompt_info.function):
            messages = await prompt_info.function(**arguments)
        else:
            messages = prompt_info.function(**arguments)
    except Exception as e:
        raise ValueError(f"Prompt execution failed: {str(e)[:200]}")
    
    return {"description": prompt_info.description, "messages": messages}