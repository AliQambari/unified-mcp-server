"""
Tests for resource functionality.
"""

import pytest
from fastapi.testclient import TestClient

from unified_server import UnifiedServer, resource, registry


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


def test_resource_registration():
    """Test resource registration"""
    @resource(uri="test://resource", description="Test resource")
    def test_resource():
        return "test data"
    
    assert "test_resource" in registry.resources
    assert registry.resources["test_resource"].uri == "test://resource"


def test_resource_custom_name():
    """Test resource with custom name"""
    @resource(uri="test://custom", name="custom_name", description="Custom resource")
    def some_function():
        return "data"
    
    assert "custom_name" in registry.resources
    assert "some_function" not in registry.resources


def test_list_resources(client):
    """Test listing resources via API"""
    @resource(uri="config://app", description="App config")
    def config():
        return {"theme": "dark"}
    
    @resource(uri="data://users", description="Users data")
    def users():
        return ["alice", "bob"]
    
    response = client.get("/resources")
    assert response.status_code == 200
    data = response.json()
    assert len(data["resources"]) == 2


def test_read_resource(client):
    """Test reading a resource"""
    @resource(uri="config://settings", description="Settings")
    def settings():
        return {"key": "value"}
    
    response = client.get("/resources/settings")
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == {"key": "value"}
    assert data["uri"] == "config://settings"


def test_read_resource_by_uri(client):
    """Test reading resource by URI"""
    @resource(uri="config://app", description="App config")
    def app_config():
        return {"name": "MyApp"}
    
    response = client.get("/resources/by-uri/config://app")
    assert response.status_code == 200
    assert response.json()["content"] == {"name": "MyApp"}


def test_read_resource_not_found(client):
    """Test reading non-existent resource"""
    response = client.get("/resources/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_async_resource(client):
    """Test async resource"""
    @resource(uri="async://data", description="Async data")
    async def async_data():
        return {"async": True}
    
    response = client.get("/resources/async_data")
    assert response.status_code == 200
    assert response.json()["content"] == {"async": True}


def test_resource_with_mime_type(client):
    """Test resource with custom MIME type"""
    @resource(
        uri="data://json",
        description="JSON data",
        mime_type="application/json"
    )
    def json_data():
        return {"format": "json"}
    
    response = client.get("/resources/json_data")
    assert response.status_code == 200
    assert response.json()["mimeType"] == "application/json"