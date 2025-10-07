"""
Tests for tool functionality.
"""

import pytest
from fastapi.testclient import TestClient

from unified_server import UnifiedServer, tool, registry


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


def test_tool_registration():
    """Test tool registration"""
    @tool(description="Test tool")
    def test_func(x: int) -> int:
        return x * 2
    
    assert "test_func" in registry.tools
    assert registry.tools["test_func"].description == "Test tool"


def test_tool_custom_name():
    """Test tool with custom name"""
    @tool(name="custom_name", description="Custom named tool")
    def some_function(x: int) -> int:
        return x * 2
    
    assert "custom_name" in registry.tools
    assert "some_function" not in registry.tools


def test_list_tools(client):
    """Test listing tools via API"""
    @tool(description="Tool 1")
    def tool1(x: int) -> int:
        return x
    
    @tool(description="Tool 2")
    def tool2(y: str) -> str:
        return y
    
    response = client.get("/tools")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tools"]) == 2
    assert any(t["name"] == "tool1" for t in data["tools"])
    assert any(t["name"] == "tool2" for t in data["tools"])


def test_execute_tool(client):
    """Test executing a tool"""
    @tool(description="Add numbers")
    def add(a: int, b: int) -> int:
        return a + b
    
    response = client.post("/tools/add", json={"a": 5, "b": 3})
    assert response.status_code == 200
    assert response.json()["result"] == 8


def test_execute_tool_not_found(client):
    """Test executing non-existent tool"""
    response = client.post("/tools/nonexistent", json={})
    assert response.status_code == 404


def test_execute_tool_invalid_params(client):
    """Test executing tool with invalid parameters"""
    @tool(description="Test tool")
    def test_tool(x: int) -> int:
        return x * 2
    
    response = client.post("/tools/test_tool", json={"y": 5})  # Wrong param name
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_async_tool(client):
    """Test async tool execution"""
    @tool(description="Async tool")
    async def async_tool(x: int) -> int:
        return x * 2
    
    response = client.post("/tools/async_tool", json={"x": 5})
    assert response.status_code == 200
    assert response.json()["result"] == 10


def test_tool_with_complex_schema(client):
    """Test tool with custom parameter schema"""
    @tool(
        description="Complex tool",
        parameters={
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "integer"}
                    }
                }
            },
            "required": ["data"]
        }
    )
    def complex_tool(data: dict) -> int:
        return data["value"] * 2
    
    response = client.post("/tools/complex_tool", json={"data": {"value": 5}})
    assert response.status_code == 200
    assert response.json()["result"] == 10


def test_get_tool_info(client):
    """Test getting tool information"""
    @tool(description="Test tool")
    def test_tool(x: int, y: int) -> int:
        return x + y
    
    response = client.get("/tools/test_tool")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_tool"
    assert data["description"] == "Test tool"
    assert "parameters" in data