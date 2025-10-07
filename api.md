# API Documentation

## REST API Endpoints

### Base Endpoints

#### GET `/`
Get server information and available endpoints.

**Response:**
```json
{
  "name": "unified-server",
  "version": "1.0.0",
  "tools": ["tool1", "tool2"],
  "resources": ["resource1", "resource2"],
  "prompts": ["prompt1"],
  "endpoints": {
    "rest_api": {
      "tools": "/tools",
      "resources": "/resources",
      "prompts": "/prompts",
      "docs": "/docs"
    },
    "mcp": {
      "endpoint": "/mcp (POST for JSON-RPC)"
    }
  }
}
```

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "tools": 5,
  "resources": 3,
  "prompts": 2
}
```

### Tool Endpoints

#### GET `/tools`
List all available tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "add",
      "description": "Add two numbers",
      "parameters": {
        "type": "object",
        "properties": {
          "a": {"type": "integer"},
          "b": {"type": "integer"}
        },
        "required": ["a", "b"]
      }
    }
  ]
}
```

#### GET `/tools/{tool_name}`
Get information about a specific tool.

**Parameters:**
- `tool_name` (path): Name of the tool

**Response:**
```json
{
  "name": "add",
  "description": "Add two numbers",
  "parameters": { ... }
}
```

#### POST `/tools/{tool_name}`
Execute a tool with given parameters.

**Parameters:**
- `tool_name` (path): Name of the tool
- Request body: JSON object with tool parameters

**Request:**
```json
{
  "a": 5,
  "b": 3
}
```

**Response:**
```json
{
  "result": 8
}
```

**Error Response (404):**
```json
{
  "detail": "Tool 'nonexistent' not found"
}
```

**Error Response (400):**
```json
{
  "detail": "Invalid parameters: ..."
}
```

### Resource Endpoints

#### GET `/resources`
List all available resources.

**Response:**
```json
{
  "resources": [
    {
      "uri": "config://app",
      "name": "app_config",
      "description": "Application configuration",
      "mimeType": "application/json"
    }
  ]
}
```

#### GET `/resources/{resource_name}`
Read a resource by name.

**Parameters:**
- `resource_name` (path): Name of the resource

**Response:**
```json
{
  "content": {"theme": "dark", "language": "en"},
  "uri": "config://app",
  "mimeType": "application/json"
}
```

#### GET `/resources/by-uri/{uri:path}`
Read a resource by URI.

**Parameters:**
- `uri` (path): URI of the resource

**Response:**
```json
{
  "content": { ... },
  "uri": "config://app",
  "mimeType": "application/json"
}
```

### Prompt Endpoints

#### GET `/prompts`
List all available prompts.

**Response:**
```json
{
  "prompts": [
    {
      "name": "greeting",
      "description": "Generate a greeting",
      "arguments": [
        {
          "name": "name",
          "description": "Person's name",
          "required": true
        }
      ]
    }
  ]
}
```

#### GET `/prompts/{prompt_name}`
Get information about a specific prompt.

**Response:**
```json
{
  "name": "greeting",
  "description": "Generate a greeting",
  "arguments": [ ... ]
}
```

#### POST `/prompts/{prompt_name}`
Get a prompt with arguments.

**Request:**
```json
{
  "name": "Alice"
}
```

**Response:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": {
        "type": "text",
        "text": "Hello Alice!"
      }
    }
  ],
  "description": "Generate a greeting"
}
```

## MCP JSON-RPC Endpoint

### POST `/mcp`
Main MCP JSON-RPC endpoint for all MCP operations.

#### initialize

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {
      "name": "unified-server",
      "version": "1.0.0"
    },
    "capabilities": {
      "tools": {},
      "resources": {},
      "prompts": {}
    }
  }
}
```

#### tools/list

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "add",
        "description": "Add two numbers",
        "inputSchema": { ... }
      }
    ]
  }
}
```

#### tools/call

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "add",
    "arguments": {
      "a": 5,
      "b": 3
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "8"
      }
    ]
  }
}
```

#### resources/list

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "resources/list",
  "params": {}
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "resources": [
      {
        "uri": "config://app",
        "name": "app_config",
        "description": "Application configuration",
        "mimeType": "application/json"
      }
    ]
  }
}
```

#### resources/read

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "resources/read",
  "params": {
    "uri": "config://app"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "contents": [
      {
        "uri": "config://app",
        "mimeType": "application/json",
        "text": "{\"theme\": \"dark\"}"
      }
    ]
  }
}
```

#### prompts/list

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "prompts/list",
  "params": {}
}
```

#### prompts/get

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "prompts/get",
  "params": {
    "name": "greeting",
    "arguments": {
      "name": "Alice"
    }
  }
}
```

## Error Responses

### MCP Error Response

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32602,
    "message": "Tool 'nonexistent' not found"
  }
}
```

### Error Codes

- `-32700`: Parse error
- `-32600`: Invalid request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error

## Using with MCP Clients

### Claude Desktop Configuration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8000/mcp"]
    }
  }
}
```

### Amazon Q Configuration

Similar configuration for Amazon Q:

```json
{
  "servers": {
    "my-server": {
      "command": "npx",
      "args": ["mcp-remote", "http://localhost:8000/mcp"]
    }
  }
}
```