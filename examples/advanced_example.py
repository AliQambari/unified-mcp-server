"""
Advanced example with async functions, complex schemas, and more features.
"""

import asyncio
import json
from datetime import datetime
from typing import List, Dict, Optional

from unified_server import UnifiedServer, tool, resource, prompt, ServerConfig


# Create server with custom configuration
config = ServerConfig(
    name="advanced-example",
    version="2.0.0",
    host="0.0.0.0",
    port=8000,
    log_level="DEBUG",
    cors_enabled=True,
    cors_origins=["http://localhost:3000"]
)

server = UnifiedServer(name="advanced-example", version="2.0.0", config=config)


# Async tool example
@tool(description="Fetch data from a simulated API (async)")
async def fetch_data(endpoint: str, timeout: int = 5) -> Dict:
    """Simulate an async API call"""
    await asyncio.sleep(0.5)  # Simulate network delay
    return {
        "endpoint": endpoint,
        "timestamp": datetime.now().isoformat(),
        "status": "success",
        "data": {"message": f"Data from {endpoint}"}
    }


# Tool with complex parameters
@tool(
    description="Search database with filters",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query"
            },
            "filters": {
                "type": "object",
                "properties": {
                    "category": {"type": "string"},
                    "min_price": {"type": "number"},
                    "max_price": {"type": "number"},
                    "in_stock": {"type": "boolean"}
                },
                "description": "Filter criteria"
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results",
                "default": 10
            }
        },
        "required": ["query"]
    }
)
def search_database(query: str, filters: Optional[Dict] = None, limit: int = 10) -> List[Dict]:
    """Search database with complex filtering"""
    # Simulate database search
    results = [
        {
            "id": i,
            "title": f"Item matching '{query}' #{i}",
            "category": filters.get("category", "general") if filters else "general",
            "price": 10.0 + i,
            "in_stock": True
        }
        for i in range(1, min(limit + 1, 6))
    ]
    return results


# Tool with error handling
@tool(description="Divide two numbers (with error handling)")
def divide(numerator: float, denominator: float) -> float:
    """Divide two numbers with proper error handling"""
    if denominator == 0:
        raise ValueError("Cannot divide by zero")
    return numerator / denominator


# Analytics tool
@tool(description="Calculate statistics for a list of numbers")
def calculate_stats(numbers: List[float]) -> Dict:
    """Calculate mean, median, min, max for a list of numbers"""
    if not numbers:
        raise ValueError("Numbers list cannot be empty")
    
    sorted_numbers = sorted(numbers)
    n = len(numbers)
    
    return {
        "count": n,
        "sum": sum(numbers),
        "mean": sum(numbers) / n,
        "median": sorted_numbers[n // 2] if n % 2 else (sorted_numbers[n // 2 - 1] + sorted_numbers[n // 2]) / 2,
        "min": min(numbers),
        "max": max(numbers),
        "range": max(numbers) - min(numbers)
    }


# Dynamic resource
@resource(
    uri="system://status",
    description="Real-time system status",
    mime_type="application/json"
)
def get_system_status():
    """Get current system status"""
    import psutil
    
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "used": psutil.disk_usage('/').used,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        }
    }


# Async resource
@resource(
    uri="data://async-feed",
    description="Async data feed"
)
async def get_async_feed():
    """Get data from async source"""
    await asyncio.sleep(0.3)
    return {
        "items": [
            {"id": i, "title": f"Item {i}", "timestamp": datetime.now().isoformat()}
            for i in range(5)
        ]
    }


# Complex prompt with multiple arguments
@prompt(
    description="Generate a technical documentation prompt",
    arguments=[
        {
            "name": "topic",
            "description": "The topic to document",
            "required": True
        },
        {
            "name": "audience",
            "description": "Target audience (beginner/intermediate/advanced)",
            "required": False
        },
        {
            "name": "format",
            "description": "Documentation format (tutorial/reference/guide)",
            "required": False
        }
    ]
)
def documentation_prompt(topic: str, audience: str = "intermediate", format: str = "guide"):
    """Generate a comprehensive documentation prompt"""
    return [
        {
            "role": "system",
            "content": {
                "type": "text",
                "text": f"You are a technical writer creating {format} documentation "
                        f"for {audience} level users."
            }
        },
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"Create comprehensive {format}-style documentation about {topic}. "
                        f"Target audience: {audience}. Include examples and best practices."
            }
        }
    ]


@prompt(description="Generate a debugging prompt with context")
def debugging_prompt(error_message: str, language: str, context: str = ""):
    """Generate a debugging assistance prompt"""
    context_text = f"\n\nAdditional context:\n{context}" if context else ""
    
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"I'm getting this error in {language}:\n\n{error_message}{context_text}\n\n"
                        f"Please help me understand what's causing this error and how to fix it."
            }
        }
    ]


# Run the server
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Advanced Example Server")
    print("="*60)
    print("\nFeatures demonstrated:")
    print("  • Async tools and resources")
    print("  • Complex parameter schemas")
    print("  • Error handling")
    print("  • System monitoring")
    print("  • Advanced prompts")
    print("\nExample requests:")
    print("\n1. Async data fetch:")
    print("  curl -X POST http://localhost:8000/tools/fetch_data \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"endpoint": "/api/users"}\'')
    print("\n2. Complex search:")
    print("  curl -X POST http://localhost:8000/tools/search_database \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"query": "laptop", "filters": {"category": "electronics"}, "limit": 5}\'')
    print("\n3. Statistics:")
    print("  curl -X POST http://localhost:8000/tools/calculate_stats \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"numbers": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]}\'')
    print("\n" + "="*60 + "\n")
    
    server.run()