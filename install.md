# Installation Guide
- pip install -e .
## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)

## Installation Methods

### 1. Install from Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/aliqambari/unified-mcp-server.git
cd unified-mcp-server

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### 2. Install from PyPI (Coming Soon)

```bash
pip install unified-mcp-server
```

### 3. Using Make

```bash
# Install package
make install

# Install with dev dependencies
make dev
```

### 4. Docker Installation

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build Docker image manually
docker build -t unified-mcp-server .
docker run -p 8000:8000 unified-mcp-server
```

## Verify Installation

```bash
# Check if package is installed
python -c "import unified_server; print(unified_server.__version__)"

# Run the server
python -m unified_server --help
```

## Quick Start

Create a simple server file `my_server.py`:

```python
from unified_server import UnifiedServer, tool

server = UnifiedServer(name="my-server", version="1.0.0")

@tool(description="Add two numbers")
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    server.run()
```

Run the server:

```bash
python my_server.py
```

## Configuration

### Environment Variables

You can configure the server using environment variables:

```bash
export SERVER_NAME="my-server"
export SERVER_VERSION="1.0.0"
export SERVER_HOST="0.0.0.0"
export SERVER_PORT="8000"
export LOG_LEVEL="INFO"
```

### Configuration File

Create a `config.py`:

```python
from unified_server import ServerConfig

config = ServerConfig(
    name="my-server",
    version="1.0.0",
    host="0.0.0.0",
    port=8000,
    log_level="INFO",
    cors_enabled=True,
    cors_origins=["http://localhost:3000"]
)
```

## Development Setup

```bash
# Install dev dependencies
make dev

# Run tests
make test

# Run tests with coverage
make test-cov

# Format code
make format

# Lint code
make lint
```

## Troubleshooting

### Import Error

If you get an import error, make sure you're in the correct directory and the package is installed:

```bash
pip install -e .
```

### Port Already in Use

If port 8000 is already in use, specify a different port:

```bash
python -m unified_server --port 8001
```

### Permission Denied (Linux/Mac)

If you get permission errors on Linux/Mac:

```bash
sudo python -m unified_server
# Or use a port > 1024
python -m unified_server --port 8000
```

## Next Steps

- Check out the [examples/](examples/) directory for more examples
- Read the [README.md](README.md) for usage instructions
- See [API Documentation](http://localhost:8000/docs) when server is running