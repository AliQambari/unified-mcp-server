import httpx
import asyncio
import json

class MCPClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        
    async def call_tool(self, tool_name, arguments):
        async with httpx.AsyncClient() as client:
            # MCP tool call request
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            response = await client.post(
                f"{self.base_url}/mcp",
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            
            result = response.json()
            return result["result"]["content"][0]["text"]
    
    async def list_tools(self):
        async with httpx.AsyncClient() as client:
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
            
            response = await client.post(
                f"{self.base_url}/mcp",
                json=mcp_request
            )
            
            return response.json()["result"]["tools"]

async def main():
    client = MCPClient("http://localhost:8002")
    
    # List available tools
    tools = await client.list_tools()
    print("Available tools:", [tool["name"] for tool in tools])
    
    # Call tools
    result = await client.call_tool("add", {"a": 15, "b": 27})
    print("Addition:", result)
    
    result = await client.call_tool("list_tables", {
        "db_type": "postgres", 
        "db_name": "kmp"
    })
    print("Tables:", result)

asyncio.run(main())
