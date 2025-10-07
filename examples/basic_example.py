"""
Basic example of using the unified server.
"""

from unified_server import UnifiedServer, tool, resource, prompt


# Create server
server = UnifiedServer(name="basic-example", version="1.0.0")


# Define a simple tool
@tool(description="Add two numbers together")
def add(a: int, b: int) -> int:
    """Add two numbers and return the result"""
    return a + b


@tool(description="Multiply two numbers together")
def multiply(x: int, y: int) -> int:
    """Multiply two numbers and return the result"""
    return x * y


@tool(description="Get a greeting message")
def greet(name: str) -> str:
    """Generate a personalized greeting"""
    return f"Hello, {name}! Welcome to the unified server."


# Define a simple resource
@resource(
    uri="config://settings",
    description="Application settings and configuration"
)
def get_settings():
    """Return application settings"""
    return {
        "app_name": "Basic Example",
        "version": "1.0.0",
        "theme": "dark",
        "language": "en",
        "features": {
            "notifications": True,
            "auto_save": True
        }
    }


@resource(
    uri="data://users",
    description="List of users",
    mime_type="application/json"
)
def get_users():
    """Return list of users"""
    return [
        {"id": 1, "name": "Alice", "role": "admin"},
        {"id": 2, "name": "Bob", "role": "user"},
        {"id": 3, "name": "Charlie", "role": "user"}
    ]


# Define a simple prompt
@prompt(
    description="Generate a code review prompt",
    arguments=[
        {
            "name": "language",
            "description": "Programming language",
            "required": True
        }
    ]
)
def code_review_prompt(language: str):
    """Generate a prompt for code review"""
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"Please review this {language} code for best practices, "
                        f"potential bugs, and suggest improvements."
            }
        }
    ]


# Run the server
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Basic Example Server")
    print("="*60)
    print("\nThis example demonstrates:")
    print("  • 3 tools: add, multiply, greet")
    print("  • 2 resources: settings, users")
    print("  • 1 prompt: code_review_prompt")
    print("\nTry the API:")
    print("  curl -X POST http://localhost:8000/tools/add \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"a": 5, "b": 3}\'')
    print("\n" + "="*60 + "\n")
    
    server.run(host="0.0.0.0", port=8000)