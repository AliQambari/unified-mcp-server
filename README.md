# 🚀 Unified MCP Server - One tool server; multiple protocols 

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.118+-green.svg)](https://fastapi.tiangolo.com/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.16+-purple.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple server that seamlessly exposes AI tools and resources through **multiple protocols**: REST API, MCP (Model Context Protocol), and WebSocket connections.

## ✨ Features

### 🔌 **Triple Protocol Support**
- **REST API**: Standard HTTP endpoints for web integration
- **MCP over HTTP**: Model Context Protocol for AI assistants (Claude, etc.)
- **WebSocket**: Real-time bidirectional communication

### 🎯 **Developer Experience**
- **Simple Decorators**: `@tool`, `@resource`,'@resource_template', `@prompt` - that's it!
- **Auto Schema Generation**: Function signatures → JSON schemas automatically
- **Type Safety**: Full type hints with mypy support
- **Async/Await**: Native async support throughout

### 🏗️ **Production Ready**
- **Comprehensive Logging**: Structured logging with configurable levels
- **Error Handling**: Graceful error responses and recovery
- **CORS Support**: Cross-origin requests handled
- **Health Checks**: Built-in monitoring endpoints

## 📦 Installation

### Using uv (Recommended)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
uv add unified-mcp-server
```

### Using pip

```bash
pip install unified-mcp-server
```

### Development Installation

```bash
# Clone the repository
git clone <repository-url>
cd unified-mcp-server

# Using uv (recommended)
uv sync --dev

# Or using pip
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Basic Example

```python
from unified_server import create_server, tool, resource, prompt

# Define tools with simple decorators
@tool(description="Add two numbers together")
def add(a: int, b: int) -> int:
    """Add two integers and return the result"""
    return a + b

@tool(description="Analyze text sentiment")
def analyze_sentiment(text: str) -> dict:
    """Analyze the sentiment of given text"""
    # Your sentiment analysis logic here
    return {"sentiment": "positive", "confidence": 0.95}

# Define resources (data sources)
@resource(
    uri="config://app/settings",
    description="Application configuration",
    mime_type="application/json"
)
def get_config():
    return {
        "app_name": "My App",
        "version": "1.0.0",
        "features": {"ai_enabled": True}
    }

# Define prompts for AI interactions
@prompt(description="Code review prompt")
def code_review_prompt(language: str):
    return [{
        "role": "user",
        "content": {
            "type": "text",
            "text": f"Review this {language} code for best practices"
        }
    }]

# Create and run server
if __name__ == "__main__":
    server = create_server(name="my-server", version="1.0.0")
    server.run(host="0.0.0.0", port=8000)
```

### 📁 Complete Example

See [`src/tool_server.py`](src/tool_server.py) for a comprehensive example with:
- Multiple tools (math, search, sentiment analysis)
- Various resources (config, user data, documentation)
- Advanced prompts with parameters
- Real file loading
- Error handling

## 🔧 Usage Examples

### 🌐 REST API

```bash
# List all available tools
curl http://localhost:8000/tools

# Execute a tool
curl -X POST http://localhost:8000/tools/add \
  -H "Content-Type: application/json" \
  -d '{"a": 15, "b": 27}'

# Get all resources
curl http://localhost:8000/resources

# Read a specific resource
curl http://localhost:8000/resources/get_config

# List available prompts
curl http://localhost:8000/prompts

# Generate a prompt
curl -X POST http://localhost:8000/prompts/code_review_prompt \
  -H "Content-Type: application/json" \
  -d '{"language": "python"}'
```

### 🤖 MCP Integration

#### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "unified-server": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-everything", "http://localhost:8000/mcp"]
    }
  }
}
```

#### Direct MCP Client

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    # Connect to your unified server
    async with stdio_client(StdioServerParameters(
        command="python",
        args=["-m", "your_server_module"]
    )) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {[tool.name for tool in tools.tools]}")
            
            # Call a tool
            result = await session.call_tool("add", {"a": 10, "b": 20})
            print(f"Result: {result.content}")

asyncio.run(main())
```

### 🔌 WebSocket Connection

```javascript
// Connect via WebSocket for real-time communication
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = function() {
    // Send tool execution request
    ws.send(JSON.stringify({
        type: 'tool_call',
        tool: 'add',
        parameters: { a: 5, b: 3 }
    }));
};

ws.onmessage = function(event) {
    const response = JSON.parse(event.data);
    console.log('Tool result:', response.result);
};
```

## 📚 Examples

### Basic Usage
- [`examples/basic_example.py`](examples/basic_example.py) - Simple tools and resources
- [`examples/advanced_example.py`](examples/advanced_example.py) - Async functions, complex schemas

### Production Example
- [`src/tool_server.py`](src/tool_server.py) - Full-featured server with:
  - 🔧 **Tools**: Math operations, search, sentiment analysis
  - 📄 **Resources**: Configuration, user data, documentation
  - 💬 **Prompts**: System prompts, code review, debugging
  - 📁 **File Operations**: Loading real files from disk

## 🏗️ Architecture

```
src/unified_server/
├── 🏛️ core/              # Core server and registry
│   ├── server.py         # Main FastAPI server
│   ├── registry.py       # Tool/resource registry
│   └── config.py         # Configuration management
├── 🎨 decorators/         # Decorator implementations
│   ├── tool.py          # @tool decorator
│   ├── resource.py      # @resource decorator
│   └── prompt.py        # @prompt decorator
├── 🛣️ routes/            # HTTP route handlers
│   ├── tools.py         # Tool execution endpoints
│   ├── resources.py     # Resource access endpoints
│   ├── prompts.py       # Prompt generation endpoints
│   └── mcp.py           # MCP protocol endpoints
├── 🔧 handlers/          # Protocol handlers
│   └── mcp_handlers.py  # MCP message handling
└── 🛠️ utils/             # Utilities
    ├── inspection.py    # Function signature analysis
    └── logging.py       # Logging configuration
```

## 🔍 API Documentation

Once your server is running, visit:

- **📖 Interactive Docs**: `http://localhost:8000/docs` (Swagger UI)
- **📋 ReDoc**: `http://localhost:8000/redoc` (Alternative documentation)
- **🔧 OpenAPI Schema**: `http://localhost:8000/openapi.json`

## 🛠️ Development

### Setup Development Environment

```bash
# Using uv (recommended)
uv sync --dev
source .venv/bin/activate

# Using pip
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=unified_server

# Run specific test file
pytest tests/test_tools.py -v
```

### Code Quality

```bash
# Format code
black src tests examples

# Lint code
ruff check src tests examples

# Type checking
mypy src

# Run all quality checks
make lint  # if using the provided Makefile
```

### Project Commands

```bash
# Start development server with auto-reload
uv run python src/tool_server.py

# Run basic example
uv run python examples/basic_example.py

# Run advanced example
uv run python examples/advanced_example.py
```

## 🐳 Docker Support

```bash
# Build image
docker build -t unified-mcp-server .

# Run container
docker run -p 8000:8000 unified-mcp-server

# Using docker-compose
docker-compose up
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **MCP Protocol** for standardizing AI tool interfaces
- **Pydantic** for data validation and serialization
- **uvicorn** for ASGI server implementation

---

**Made with ❤️ for the AI development community**
