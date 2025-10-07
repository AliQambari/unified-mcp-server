# Complete Guide: Writing Tools, Resources & Prompts

**For Unified MCP Server**

This guide shows you exactly how to write perfect tools, resources, and prompts for your unified server.

---

## 📋 Table of Contents

1. [Tools](#-tools)
2. [Static Resources](#-static-resources)
3. [Dynamic Resources](#-dynamic-resources)
4. [Resource Templates](#-resource-templates)
5. [Prompts](#-prompts)
6. [Best Practices](#-best-practices)
7. [Common Patterns](#-common-patterns)

---

## 🔧 Tools

Tools are functions that perform actions or computations.

### Basic Tool

```python
from unified_server import tool

@tool(description="Add two numbers together")
def add(a: int, b: int) -> int:
    """Add two integers and return the sum"""
    return a + b
```

### Tool with Optional Parameters

```python
@tool(description="Search for information")
def search(query: str, max_results: int = 5) -> dict:
    """
    Search for information with optional result limit
    
    Args:
        query: Search query string
        max_results: Maximum number of results (default: 5)
    """
    return {
        "query": query,
        "results": [f"Result {i+1}" for i in range(max_results)]
    }
```

### Tool with Complex Return Types

```python
from typing import List, Dict, Any

@tool(description="Analyze text and return detailed metrics")
def analyze_text(text: str) -> Dict[str, Any]:
    """
    Analyze text and return comprehensive metrics
    
    Returns:
        Dict with word_count, char_count, sentences, etc.
    """
    words = text.split()
    sentences = text.split('.')
    
    return {
        "word_count": len(words),
        "char_count": len(text),
        "sentence_count": len(sentences),
        "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
        "unique_words": len(set(words))
    }
```

### Async Tool

```python
import asyncio

@tool(description="Fetch data from API asynchronously")
async def fetch_data(url: str, timeout: int = 30) -> dict:
    """
    Fetch data from URL asynchronously
    
    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
    """
    await asyncio.sleep(0.1)  # Simulate async operation
    return {
        "url": url,
        "status": "success",
        "data": {"message": f"Data from {url}"}
    }
```

### Tool with Custom Schema

```python
@tool(
    description="Advanced search with filters",
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
            "sort_by": {
                "type": "string",
                "enum": ["price", "rating", "date"],
                "description": "Sort field"
            }
        },
        "required": ["query"]
    }
)
def advanced_search(query: str, filters: dict = None, sort_by: str = "rating") -> list:
    """Advanced search with complex filtering"""
    # Your search logic here
    results = [
        {
            "id": 1,
            "title": f"Result for '{query}'",
            "category": filters.get("category", "general") if filters else "general",
            "price": 29.99,
            "rating": 4.5
        }
    ]
    return results
```

### Tool with Error Handling

```python
@tool(description="Divide two numbers safely")
def divide(numerator: float, denominator: float) -> float:
    """
    Divide two numbers with error handling
    
    Raises:
        ValueError: If denominator is zero
    """
    if denominator == 0:
        raise ValueError("Cannot divide by zero")
    
    return numerator / denominator
```

### Tool with List Input

```python
@tool(description="Calculate statistics for a list of numbers")
def calculate_stats(numbers: List[float]) -> Dict[str, float]:
    """
    Calculate statistical measures for a list of numbers
    
    Args:
        numbers: List of numbers to analyze
    
    Returns:
        Dictionary with mean, median, min, max, etc.
    """
    if not numbers:
        raise ValueError("Numbers list cannot be empty")
    
    sorted_nums = sorted(numbers)
    n = len(numbers)
    
    return {
        "count": n,
        "sum": sum(numbers),
        "mean": sum(numbers) / n,
        "median": sorted_nums[n // 2],
        "min": min(numbers),
        "max": max(numbers),
        "range": max(numbers) - min(numbers)
    }
```

---

## 📄 Static Resources

Static resources provide fixed content that doesn't change based on input.

### Basic Static Resource

```python
from unified_server import resource

@resource(
    uri="config://app",
    description="Application configuration",
    mime_type="application/json"
)
def get_config() -> dict:
    """Return application configuration"""
    return {
        "app_name": "My Application",
        "version": "1.0.0",
        "environment": "production",
        "features": {
            "auth": True,
            "notifications": True
        }
    }
```

### Text Documentation Resource

```python
@resource(
    uri="file://docs/readme",
    description="Project documentation and guidelines",
    mime_type="text/plain"
)
def get_readme() -> str:
    """Return project documentation as plain text"""
    return """# Project Documentation

## Overview
This project provides tools for data analysis and processing.

## Features
- Data cleaning and validation
- Statistical analysis
- Visualization support
- Export to multiple formats

## Usage
1. Load your data
2. Apply transformations
3. Analyze results
4. Export findings

## Support
Contact: support@example.com
"""
```

### Markdown Resource

```python
@resource(
    uri="file://knowledge/base.md",
    description="Knowledge base with structured information",
    mime_type="text/markdown"
)
def get_knowledge_base() -> str:
    """Return knowledge base in markdown format"""
    return """# Knowledge Base

## Quick Facts
- **Founded**: 2024
- **Team Size**: 50+ members
- **Location**: Global (Remote)

## Products
### Core Platform
- Real-time analytics
- Custom dashboards
- API access
- Mobile apps

### Enterprise Features
- SSO integration
- Advanced security
- Dedicated support
- Custom training

## FAQ

### How do I get started?
Sign up at our website and follow the onboarding guide.

### What's the pricing?
We offer flexible plans starting at $10/month.

### Is there a free trial?
Yes! 14-day free trial with full access.
"""
```

### JSON Data Resource

```python
@resource(
    uri="data://users/list",
    description="List of all users",
    mime_type="application/json"
)
def get_users() -> list:
    """Return list of users"""
    return [
        {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "role": "admin",
            "status": "active"
        },
        {
            "id": 2,
            "name": "Bob Smith",
            "email": "bob@example.com",
            "role": "user",
            "status": "active"
        },
        {
            "id": 3,
            "name": "Charlie Davis",
            "email": "charlie@example.com",
            "role": "user",
            "status": "inactive"
        }
    ]
```

### System Instructions Resource

```python
@resource(
    uri="file://instructions/system.txt",
    description="System instructions that AI should follow",
    mime_type="text/plain"
)
def get_system_instructions() -> str:
    """Return system-wide instructions for AI"""
    return """SYSTEM INSTRUCTIONS

1. RESPONSE GUIDELINES:
   - Be concise and direct
   - Use examples when helpful
   - Cite sources when available
   - Admit uncertainty when appropriate

2. TOOL USAGE:
   - Always prefer tools over guessing
   - Check tool availability before suggesting
   - Handle tool errors gracefully
   - Log all tool calls for debugging

3. DATA HANDLING:
   - Validate input data
   - Sanitize user inputs
   - Protect sensitive information
   - Follow data privacy guidelines

4. ERROR HANDLING:
   - Provide clear error messages
   - Suggest solutions when possible
   - Log errors for investigation
   - Never expose internal details

5. BEST PRACTICES:
   - Follow company guidelines
   - Maintain professional tone
   - Stay within scope of expertise
   - Escalate complex issues appropriately
"""
```

### Load from File

```python
from pathlib import Path

@resource(
    uri="file://data/content.txt",
    description="Content loaded from actual file",
    mime_type="text/plain"
)
def get_file_content() -> str:
    """Load and return content from a file on disk"""
    file_path = Path("data/content.txt")
    
    # Create sample file if it doesn't exist
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("Default content from file.\nEdit data/content.txt to change this.")
    
    return file_path.read_text()
```

---

## 🔄 Dynamic Resources

Dynamic resources generate content based on current state or external data.

### Time-Based Resource

```python
from datetime import datetime

@resource(
    uri="system://status",
    description="Current system status with timestamp",
    mime_type="application/json"
)
def get_system_status() -> dict:
    """Return current system status"""
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "operational",
        "uptime_hours": 72.5,
        "active_users": 1523,
        "requests_per_second": 450,
        "cpu_usage": 45.2,
        "memory_usage": 67.8
    }
```

### Database-Backed Resource

```python
@resource(
    uri="data://products/inventory",
    description="Current product inventory levels",
    mime_type="application/json"
)
def get_inventory() -> list:
    """Return current inventory from database"""
    # In real app, query from database
    # products = db.query("SELECT * FROM inventory")
    
    return [
        {
            "id": 101,
            "name": "Laptop",
            "stock": 45,
            "last_updated": datetime.now().isoformat()
        },
        {
            "id": 102,
            "name": "Mouse",
            "stock": 234,
            "last_updated": datetime.now().isoformat()
        }
    ]
```

### Async Dynamic Resource

```python
@resource(
    uri="data://live/feed",
    description="Live data feed from external source",
    mime_type="application/json"
)
async def get_live_feed() -> dict:
    """Fetch live data asynchronously"""
    # Simulate async API call
    await asyncio.sleep(0.2)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "items": [
            {"id": 1, "title": "Breaking News", "time": "2 min ago"},
            {"id": 2, "title": "Market Update", "time": "5 min ago"},
            {"id": 3, "title": "Weather Alert", "time": "10 min ago"}
        ]
    }
```

### System Metrics Resource

```python
import psutil

@resource(
    uri="system://metrics",
    description="Real-time system performance metrics",
    mime_type="application/json"
)
def get_system_metrics() -> dict:
    """Return current system metrics"""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu": {
            "percent": psutil.cpu_percent(interval=1),
            "count": psutil.cpu_count(),
            "freq": psutil.cpu_freq().current if psutil.cpu_freq() else None
        },
        "memory": {
            "total_gb": psutil.virtual_memory().total / (1024**3),
            "available_gb": psutil.virtual_memory().available / (1024**3),
            "percent": psutil.virtual_memory().percent
        },
        "disk": {
            "total_gb": psutil.disk_usage('/').total / (1024**3),
            "used_gb": psutil.disk_usage('/').used / (1024**3),
            "free_gb": psutil.disk_usage('/').free / (1024**3),
            "percent": psutil.disk_usage('/').percent
        }
    }
```

### User Context Resource

```python
@resource(
    uri="context://user/preferences",
    description="Current user context and preferences",
    mime_type="application/json"
)
def get_user_context() -> dict:
    """Return dynamic user context"""
    # In real app, get from session/database
    return {
        "user_id": "user_123",
        "session_start": datetime.now().isoformat(),
        "preferences": {
            "theme": "dark",
            "language": "en",
            "timezone": "UTC",
            "notifications": True
        },
        "recent_activity": [
            {"action": "search", "query": "python tutorials", "time": "5 min ago"},
            {"action": "view", "item": "documentation", "time": "10 min ago"}
        ],
        "permissions": ["read", "write", "execute"]
    }
```

---

## 🎯 Resource Templates

Resource templates are parameterized resources with dynamic URIs.

### Basic Resource Template

```python
from unified_server import resource_template

@resource_template(
    uri_template="file://user/{user_id}/profile",
    description="User profile data",
    parameters=[
        {"name": "user_id", "description": "User ID", "required": True}
    ]
)
def get_user_profile(user_id: str) -> dict:
    """Get user profile by ID"""
    return {
        "user_id": user_id,
        "name": f"User {user_id}",
        "email": f"user{user_id}@example.com"
    }
```

### Multiple Parameters

```python
@resource_template(
    uri_template="file://project/{project_id}/file/{file_name}",
    description="Project file content",
    mime_type="text/plain",
    parameters=[
        {"name": "project_id", "description": "Project ID", "required": True},
        {"name": "file_name", "description": "File name", "required": True}
    ]
)
def get_project_file(project_id: str, file_name: str) -> str:
    """Get file from project"""
    return f"Content of {file_name} in project {project_id}"
```

### Database-Backed Template

```python
@resource_template(
    uri_template="data://customer/{customer_id}/orders",
    description="Customer order history",
    mime_type="application/json",
    parameters=[
        {"name": "customer_id", "description": "Customer ID", "required": True}
    ]
)
def get_customer_orders(customer_id: str) -> list:
    """Get orders for a customer"""
    # Query database
    return [
        {"id": 1, "customer_id": customer_id, "total": 99.99},
        {"id": 2, "customer_id": customer_id, "total": 149.99}
    ]
```

### Optional Parameters

```python
@resource_template(
    uri_template="api://weather/{city}/{date}",
    description="Weather data for city and date",
    parameters=[
        {"name": "city", "description": "City name", "required": True},
        {"name": "date", "description": "Date (YYYY-MM-DD)", "required": False}
    ]
)
def get_weather(city: str, date: str = None) -> dict:
    """Get weather data"""
    from datetime import datetime
    target_date = date or datetime.now().strftime("%Y-%m-%d")
    return {
        "city": city,
        "date": target_date,
        "temperature": 72,
        "condition": "sunny"
    }
```

### Async Resource Template

```python
@resource_template(
    uri_template="api://user/{user_id}/avatar",
    description="User avatar image",
    mime_type="image/png",
    parameters=[
        {"name": "user_id", "description": "User ID", "required": True}
    ]
)
async def get_user_avatar(user_id: str) -> bytes:
    """Fetch user avatar asynchronously"""
    # Simulate async fetch
    await asyncio.sleep(0.1)
    return b"PNG_IMAGE_DATA_HERE"
```

---

## 💬 Prompts

Prompts provide templates for AI interactions.

### Basic Prompt

```python
from unified_server import prompt
from typing import List, Dict, Any

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
def code_review(language: str) -> List[Dict[str, Any]]:
    """Generate a code review prompt for specified language"""
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""You are an expert {language} developer. Please review code for:

1. **Best Practices**: Adherence to {language} conventions
2. **Bugs & Errors**: Potential runtime or logic errors
3. **Performance**: Optimization opportunities
4. **Security**: Vulnerability assessment
5. **Readability**: Code clarity and maintainability

Provide specific, actionable feedback with examples."""
            }
        }
    ]
```

### Prompt with Multiple Arguments

```python
@prompt(
    description="Generate documentation prompt",
    arguments=[
        {
            "name": "topic",
            "description": "Topic to document",
            "required": True
        },
        {
            "name": "audience",
            "description": "Target audience level (beginner/intermediate/advanced)",
            "required": False
        },
        {
            "name": "format",
            "description": "Documentation format (tutorial/reference/guide)",
            "required": False
        }
    ]
)
def documentation_prompt(
    topic: str,
    audience: str = "intermediate",
    format: str = "guide"
) -> List[Dict[str, Any]]:
    """Generate documentation prompt with customization"""
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""Create {format}-style documentation about: {topic}

**Target Audience**: {audience} level developers

**Requirements**:
1. Clear explanation suitable for {audience} developers
2. Practical code examples
3. Common use cases
4. Best practices and pitfalls
5. Additional resources

**Format**: {format.capitalize()} style with:
- Introduction and overview
- Step-by-step instructions (if tutorial)
- Code examples with explanations
- Summary and next steps"""
            }
        }
    ]
```

### Multi-Turn Prompt

```python
@prompt(
    description="System and user prompt for chat initialization",
    arguments=[
        {
            "name": "user_role",
            "description": "User's role (developer/analyst/manager)",
            "required": True
        }
    ]
)
def chat_initialization(user_role: str) -> List[Dict[str, Any]]:
    """Generate system and user prompts for chat"""
    
    role_context = {
        "developer": "You're helping a software developer with coding tasks",
        "analyst": "You're assisting a data analyst with data analysis",
        "manager": "You're supporting a manager with project management"
    }
    
    context = role_context.get(user_role, "You're helping a professional user")
    
    return [
        {
            "role": "assistant",
            "content": {
                "type": "text",
                "text": f"""Hello! {context}. 

I have access to various tools and resources to help you:
- Code analysis and review
- Data processing
- Documentation access
- Real-time information

How can I assist you today?"""
            }
        },
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": "I need help with my current task."
            }
        }
    ]
```

### Debugging Prompt

```python
@prompt(
    description="Generate debugging assistance prompt",
    arguments=[
        {
            "name": "error_message",
            "description": "The error message received",
            "required": True
        },
        {
            "name": "language",
            "description": "Programming language",
            "required": True
        },
        {
            "name": "context",
            "description": "Additional context about the error",
            "required": False
        }
    ]
)
def debug_help(
    error_message: str,
    language: str,
    context: str = ""
) -> List[Dict[str, Any]]:
    """Generate debugging assistance prompt"""
    
    context_text = f"\n\n**Additional Context:**\n{context}" if context else ""
    
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""I'm encountering this error in {language}:

```
{error_message}
```
{context_text}

Please help me:
1. **Understand** what's causing this error
2. **Fix** the issue with a corrected code example
3. **Prevent** similar errors in the future
4. **Explain** any related concepts I should know

Provide clear, actionable solutions."""
            }
        }
    ]
```

### Analysis Prompt

```python
@prompt(
    description="Generate data analysis prompt",
    arguments=[
        {
            "name": "data_description",
            "description": "Description of the data to analyze",
            "required": True
        },
        {
            "name": "goals",
            "description": "Analysis goals",
            "required": False
        }
    ]
)
def data_analysis(
    data_description: str,
    goals: str = "general insights"
) -> List[Dict[str, Any]]:
    """Generate comprehensive data analysis prompt"""
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""Analyze this data: {data_description}

**Analysis Goals**: {goals}

**Required Analysis**:
1. **Overview**: Summarize the data structure and content
2. **Quality Assessment**: Check for missing values, outliers, inconsistencies
3. **Patterns & Trends**: Identify significant patterns
4. **Insights**: Extract actionable insights
5. **Recommendations**: Suggest next steps

**Deliverables**:
- Statistical summary
- Key findings
- Visualization recommendations
- Action items

Use available tools to query and process the data."""
            }
        }
    ]
```

---

## ✅ Best Practices

### 1. Type Hints

Always use type hints for better IDE support and documentation:

```python
from typing import List, Dict, Any, Optional

@tool(description="Process data")
def process_data(
    data: List[Dict[str, Any]],
    filter_key: Optional[str] = None
) -> Dict[str, Any]:
    """Type hints improve code quality"""
    pass
```

### 2. Docstrings

Provide clear docstrings:

```python
@tool(description="Calculate average")
def calculate_average(numbers: List[float]) -> float:
    """
    Calculate the arithmetic mean of a list of numbers.
    
    Args:
        numbers: List of numbers to average
    
    Returns:
        The arithmetic mean
    
    Raises:
        ValueError: If the list is empty
    
    Example:
        >>> calculate_average([1, 2, 3, 4, 5])
        3.0
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    return sum(numbers) / len(numbers)
```

### 3. Error Handling

Always handle errors gracefully:

```python
@tool(description="Safe operation")
def safe_operation(value: str) -> dict:
    """Handle errors properly"""
    try:
        result = int(value)
        return {"success": True, "result": result}
    except ValueError:
        raise ValueError(f"Cannot convert '{value}' to integer")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {str(e)}")
```

### 4. Input Validation

Validate inputs early:

```python
@tool(description="Validate inputs")
def process_user(name: str, age: int, email: str) -> dict:
    """Validate all inputs"""
    if not name or not name.strip():
        raise ValueError("Name cannot be empty")
    
    if age < 0 or age > 150:
        raise ValueError("Age must be between 0 and 150")
    
    if "@" not in email:
        raise ValueError("Invalid email format")
    
    return {"name": name, "age": age, "email": email}
```

### 5. Resource URIs

Use consistent URI schemes:

```python
# Good URI schemes
"config://app/settings"      # Configuration
"data://users/list"          # Data resources
"file://docs/readme"         # File content
"system://status"            # System info
"context://user/preferences" # Contextual data

# Bad URI schemes
"get_config"                 # No scheme
"users"                      # No context
"readme.txt"                 # Looks like filename
```

### 6. Return Consistent Types

Be consistent with return types:

```python
# Good - always returns dict
@tool(description="Get user")
def get_user(user_id: int) -> dict:
    """Always returns dict, even if empty"""
    user = find_user(user_id)
    if not user:
        return {"error": "User not found"}
    return {"user": user}

# Bad - returns different types
@tool(description="Get user")
def get_user_bad(user_id: int):
    user = find_user(user_id)
    if not user:
        return None  # Sometimes None
    return {"user": user}  # Sometimes dict
```

---

## 🎯 Common Patterns

### Pattern 1: CRUD Operations

```python
@tool(description="Create new item")
def create_item(name: str, data: dict) -> dict:
    """Create operation"""
    return {"id": 123, "name": name, "data": data, "created": True}

@tool(description="Read item by ID")
def read_item(item_id: int) -> dict:
    """Read operation"""
    return {"id": item_id, "name": "Item", "data": {}}

@tool(description="Update existing item")
def update_item(item_id: int, data: dict) -> dict:
    """Update operation"""
    return {"id": item_id, "updated": True, "data": data}

@tool(description="Delete item")
def delete_item(item_id: int) -> dict:
    """Delete operation"""
    return {"id": item_id, "deleted": True}
```

### Pattern 2: Data Pipeline

```python
@tool(description="Load data from source")
def load_data(source: str) -> list:
    """Step 1: Load"""
    return [{"raw": "data"}]

@tool(description="Transform data")
def transform_data(data: list) -> list:
    """Step 2: Transform"""
    return [{"processed": item} for item in data]

@tool(description="Validate processed data")
def validate_data(data: list) -> dict:
    """Step 3: Validate"""
    return {"valid": True, "count": len(data)}

@tool(description="Save processed data")
def save_data(data: list, destination: str) -> dict:
    """Step 4: Save"""
    return {"saved": True, "destination": destination, "count": len(data)}
```

### Pattern 3: Configuration Layers

```python
@resource(uri="config://app/base", description="Base configuration")
def base_config() -> dict:
    """Layer 1: Base config"""
    return {"debug": False, "timeout": 30}

@resource(uri="config://app/environment", description="Environment config")
def env_config() -> dict:
    """Layer 2: Environment-specific"""
    return {"api_url": "https://api.prod.com", "cache_enabled": True}

@resource(uri="config://app/user", description="User preferences")
def user_config() -> dict:
    """Layer 3: User preferences"""
    return {"theme": "dark", "language": "en"}
```

### Pattern 4: Status Checking

```python
@tool(description="Check service health")
def health_check(service: str) -> dict:
    """Check if service is healthy"""
    return {
        "service": service,
        "status": "healthy",
        "response_time_ms": 45,
        "last_check": datetime.now().isoformat()
    }

@resource(uri="system://health", description="Overall system health")
def system_health() -> dict:
    """Get overall health status"""
    return {
        "status": "operational",
        "services": {
            "database": "healthy",
            "api": "healthy",
            "cache": "healthy"
        },
        "uptime": "99.9%"
    }
```

---

## 🚀 Complete Example Server

Here's a complete example putting it all together:

```python
from unified_server import create_server, tool, resource, prompt
from typing import List, Dict, Any
from datetime import datetime

# Create server
server = create_server(name="example-server", version="1.0.0")

# ============================================================================
# TOOLS
# ============================================================================

@tool(description="Add two numbers")
def add(a: int, b: int) -> int:
    return a + b

@tool(description="Search for information")
def search(query: str, max_results: int = 5) -> dict:
    return {
        "query": query,
        "results": [f"Result {i+1}" for i in range(max_results)]
    }

# ============================================================================
# STATIC RESOURCES
# ============================================================================

@resource(
    uri="config://app",
    description="Application configuration"
)
def app_config() -> dict:
    return {
        "name": "Example App",
        "version": "1.0.0"
    }

@resource(
    uri="file://docs/readme",
    description="Documentation"
)
def readme() -> str:
    return "# Example App\n\nThis is example documentation."

# ============================================================================
# DYNAMIC RESOURCES
# ============================================================================

@resource(
    uri="system://status",
    description="Current system status"
)
def system_status() -> dict:
    return {
        "timestamp": datetime.now().isoformat(),
        "status": "operational"
    }

# ============================================================================
# PROMPTS
# ============================================================================

@prompt(
    description="Code review prompt",
    arguments=[
        {"name": "language", "description": "Programming language", "required": True}
    ]
)
def code_review(language: str) -> List[Dict[str, Any]]:
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"Review this {language} code for best practices."
            }
        }
    ]

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8000)
```

---

## 📚 Summary

### Quick Reference Card

```python
# TOOL
@tool(description="...")
def my_tool(arg: type) -> return_type:
    return result

# STATIC RESOURCE
@resource(uri="scheme://path", description="...")
def my_resource() -> dict | str:
    return data

# DYNAMIC RESOURCE
@resource(uri="scheme://path", description="...")
def my_dynamic_resource() -> dict:
    return {"timestamp": datetime.now().isoformat(), "data": ...}

# PROMPT
@prompt(description="...", arguments=[...])
def my_prompt(arg: str) -> List[Dict[str, Any]]:
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": "prompt text"
            }
        }
    ]
```

---

