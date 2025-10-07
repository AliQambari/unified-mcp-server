"""
Tests for MCP protocol functionality.
"""

import pytest
from fastapi.testclient import TestClient

from unified_server import UnifiedServer, tool, resource, prompt, registry


@pytest.fixture(autouse=True)
def clear_registry():
    """Clear registry before each test"""
    registry.clear()
    yield
    registry.clear()


@pytest.fixture
def server():
    """Create test server"""
    return UnifiedServer(name="test-server", version="1.0.0")


@pytest.fixture
def client(server):
    """Create test client"""
    return TestClient(server.app)


def test_mcp_initialize(client):
    """Test MCP initialize"""
    response = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert "result" in data
    assert data["result"]["protocolVersion"] == "2024-11-05"
    assert "serverInfo" in data["result"]
    assert data["result"]["serverInfo"]["name"] == "test-server"


def test_mcp_tools_list(client):
    """Test MCP tools/list"""
    @tool(description="Test tool")
    def test_tool(x: int) -> int:
        return x * 2
    
    response = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["result"]["tools"]) == 1
    assert data["result"]["tools"][0]["name"] == "test_tool"


def test_mcp_tools_call(client):
    """Test MCP tools/call"""
    @tool(description="Add numbers")
    def add(a: int, b: int) -> int:
        return a + b
    
    response = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "add",
            "arguments": {"a": 5, "b": 3}
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["content"][0]["text"] == "8"


def test_mcp_tools_call_not_found(client):
    """Test MCP tools/call with non-existent tool"""
    response = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "nonexistent",
            "arguments": {}
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32602


def test_mcp_resources_list(client):
    """Test MCP resources/list"""
    @resource(uri="test://resource", description="Test resource")
    def test_resource():
        return "test data"
    
    response = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 5,
        "method": "resources/list",
        "params": {}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["result"]["resources"]) == 1
    assert data["result"]["resources"][0]["uri"] == "test://resource"


def test_mcp_resources_read(client):
    """Test MCP resources/read"""
    @resource(uri="config://app", description="App config")
    def app_config():
        return {"name": "TestApp"}
    
    response = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 6,
        "method": "resources/read",
        "params": {
            "uri": "config://app"
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "{'name': 'TestApp'}" in data["result"]["contents"][0]["text"]


def test_mcp_resources_read_not_found(client):
    """Test MCP resources/read with non-existent URI"""
    response = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 7,
        "method": "resources/read",
        "params": {
            "uri": "nonexistent://uri"
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


def test_mcp_prompts_list(client):
    """Test MCP prompts/list"""
    @prompt(description="Test prompt")
    def test_prompt(name: str):
        return [{"role": "user", "content": {"type": "text", "text": f"Hello {name}"}}]
    
    response = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 8,
        "method": "prompts/list",
        "params": {}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["result"]["prompts"]) == 1
    assert data["result"]["prompts"][0]["name"] == "test_prompt"


def test_mcp_prompts_get(client):
    """Test MCP prompts/get"""
    @prompt(description="Greeting prompt")
    def greeting(name: str):
        return [{"role": "user", "content": {"type": "text", "text": f"Hello {name}"}}]
    
    response = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 9,
        "method": "prompts/get",
        "params": {
            "name": "greeting",
            "arguments": {"name": "Alice"}
        }
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["result"]["messages"][0]["content"]["text"] == "Hello Alice"


def test_mcp_unknown_method(client):
    """Test MCP with unknown method"""
    response = client.post("/mcp", json={
        "jsonrpc": "2.0",
        "id": 10,
        "method": "unknown/method",
        "params": {}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == -32601