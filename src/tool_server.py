"""
- REST API: curl http://localhost:8000/tools
- MCP: Connect to http://localhost:8000/mcp
- API Docs: http://localhost:8000/docs
"""

from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
from unified_server import create_server, tool, resource, prompt


# ============================================================================
# TOOLS
# ============================================================================

@tool(description="Add two numbers together")
def add(a: int, b: int) -> int:
    """Add two integers"""
    return a + b


@tool(description="Multiply two numbers")
def multiply(x: float, y: float) -> float:
    """Multiply two numbers"""
    return x * y


@tool(description="Search for information")
def search(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Search for information (mock)"""
    return {
        "query": query,
        "results": [f"Result {i+1} for '{query}'" for i in range(max_results)],
        "timestamp": datetime.now().isoformat()
    }


@tool(description="Analyze text sentiment")
def analyze_sentiment(text: str) -> Dict[str, Any]:
    """Analyze text sentiment"""
    positive_words = ["good", "great", "excellent", "happy", "love"]
    negative_words = ["bad", "terrible", "sad", "hate", "awful"]
    
    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)
    
    if pos_count > neg_count:
        sentiment = "positive"
    elif neg_count > pos_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"
    
    return {
        "text": text,
        "sentiment": sentiment,
        "confidence": 0.75
    }

import os
import json
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@tool(description="Returns a list of tables in a database")
async def list_tables(db_type: str, db_name: str) -> str:
    """
    List all tables in a MySQL or PostgreSQL database.
    
    Args:
        db_type: Database type - "mysql" or "postgres"
        db_name: Name of the database
    
    Returns:
        JSON string with list of tables
    """
    db_type = db_type.lower()
    
    if db_type not in ["mysql", "postgres"]:
        return json.dumps({"error": "db_type must be 'mysql' or 'postgres'"})
    
    # Get credentials from environment based on db_type
    if db_type == "postgres":
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = int(os.getenv("POSTGRES_PORT", "5432"))
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "")
    else:  # mysql
        host = os.getenv("MYSQL_HOST", "localhost")
        port = int(os.getenv("MYSQL_PORT", "3306"))
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", "")
    
    try:
        if db_type == "mysql":
            import aiomysql
            
            conn = await aiomysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                db=db_name
            )
            
            async with conn.cursor() as cursor:
                await cursor.execute("SHOW TABLES")
                tables = await cursor.fetchall()
                table_list = [table[0] for table in tables]
            
            conn.close()
            
        else:  # postgres
            import asyncpg
            
            conn = await asyncpg.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db_name
            )
            
            query = """
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """
            
            rows = await conn.fetch(query)
            table_list = [row['tablename'] for row in rows]
            
            await conn.close()
        
        result = {
            "database_type": db_type,
            "database_name": db_name,
            "tables": table_list,
            "table_count": len(table_list)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"Failed to connect to {db_type} database: {str(e)}",
            "database_type": db_type,
            "database_name": db_name
        })

# ============================================================================
#  RESOURCES
# ============================================================================

@resource(
    uri="config://app/settings",
    description="Application configuration",
    mime_type="application/json"
)
def get_config() -> Dict[str, Any]:
    """Return app config"""
    return {
        "app_name": "Multi-Agent System",
        "version": "1.0.0",
        "max_agents": 10
    }


@resource(
    uri="data://agents/list",
    description="List of agents",
    mime_type="application/json"
)
def get_agents() -> List[Dict[str, str]]:
    """Return list of agents"""
    return [
        {"id": "agent-1", "name": "Researcher", "status": "active"},
        {"id": "agent-2", "name": "Writer", "status": "active"},
        {"id": "agent-3", "name": "Reviewer", "status": "idle"}
    ]


@resource(
    uri="file://docs/readme",
    description="Project documentation and guidelines for LLM to read",
    mime_type="text/plain"
)
def get_readme() -> str:
    """Return project documentation as plain text for LLM"""
    return """# Multi-Agent System Documentation

## Overview
This is a multi-agent system that provides various tools and resources
for processing data, analyzing text, and managing agent workflows.

## Available Tools
- **add**: Adds two numbers together
- **multiply**: Multiplies two numbers
- **search**: Searches for information (returns mock results)
- **analyze_sentiment**: Analyzes sentiment of text

## Agent Guidelines
1. Always use the search tool before providing information
2. Use sentiment analysis to gauge user satisfaction
3. Coordinate between agents for complex tasks
4. Check agent status before delegating work

## Best Practices
- Keep responses concise and accurate
- Use appropriate tools for each task
- Monitor agent performance regularly
- Maintain clear communication between agents

## Example Workflow
1. User asks a question
2. Researcher agent searches for information
3. Writer agent formats the response
4. Reviewer agent checks quality
5. Response is delivered to user
"""


@resource(
    uri="file://data/instructions.txt",
    description="System instructions and commands that LLM should follow",
    mime_type="text/plain"
)
def get_instructions() -> str:
    """Return system instructions for LLM"""
    return """SYSTEM INSTRUCTIONS

1. PRIORITY RULES:
   - Always verify information before responding
   - Use tools when available instead of guessing
   - Be concise but comprehensive

2. TOOL USAGE:
   - Use 'search' for any factual queries
   - Use 'analyze_sentiment' for user feedback
   - Use 'add' or 'multiply' for calculations

3. AGENT COORDINATION:
   - Check agent list before task delegation
   - Only delegate to 'active' status agents
   - Report to Reviewer agent for quality checks

4. ERROR HANDLING:
   - If a tool fails, inform the user clearly
   - Suggest alternatives when primary method fails
   - Log all errors for system improvement

5. RESPONSE FORMAT:
   - Start with direct answer
   - Provide context if needed
   - Include sources when using search results
"""


@resource(
    uri="file://knowledge/base.md",
    description="Knowledge base with facts and information for LLM reference",
    mime_type="text/markdown"
)
def get_knowledge_base() -> str:
    """Return knowledge base in markdown format"""
    return """# Knowledge Base

## Company Information
- **Name**: Multi-Agent Systems Inc.
- **Founded**: 2024
- **Mission**: Automate complex workflows using AI agents
- **Location**: Global (Remote-first)

## Product Features
### Core Capabilities
- Real-time text analysis
- Multi-agent coordination
- Intelligent search
- Sentiment tracking
- Resource management

### Technical Stack
- Python 3.11+
- FastAPI for REST API
- MCP protocol support
- Async/await architecture

## Common Questions

### Q: How many agents can run simultaneously?
A: Maximum of 10 agents (configurable in settings)

### Q: What formats are supported for data input?
A: Text, JSON, and structured data formats

### Q: How is sentiment analyzed?
A: Using keyword-based analysis with positive/negative word matching

## Troubleshooting
- **Agent not responding**: Check agent status in agent list
- **Tool errors**: Verify parameters are correct type
- **Slow performance**: Reduce max_agents in configuration
"""


@resource(
    uri="file://context/user_data.txt",
    description="User context and preferences for personalized responses",
    mime_type="text/plain"
)
def get_user_context() -> str:
    """Return user context information"""
    return """USER CONTEXT

Current User Profile:
- Role: Developer
- Experience Level: Intermediate
- Preferred Language: Python
- Timezone: UTC
- Communication Style: Technical and concise

User Preferences:
- Prefers code examples over long explanations
- Likes structured responses with headers
- Wants actionable information
- Appreciates error messages with solutions

Recent Activity:
- Working on multi-agent orchestration
- Interested in MCP protocol implementation
- Building HTTP-based tool integrations
- Exploring FastAPI patterns

Context Notes:
- User is familiar with async/await
- Has experience with REST APIs
- Currently debugging MCP connections
- Needs examples for decorator patterns
"""


# You can also load from actual files:
@resource(
    uri="file://local/data.txt",
    description="Load content from actual file on disk",
    mime_type="text/plain"
)
def get_file_content() -> str:
    """Load and return content from a real file"""
    file_path = Path("data.txt")
    
    # Create sample file if it doesn't exist
    if not file_path.exists():
        file_path.write_text("This is sample data from a real file.\nYou can edit data.txt to change this content.")
    
    return file_path.read_text()


# ============================================================================
#  PROMPTS
# ============================================================================

@prompt(
    description="System prompt for AI assistant",
    arguments=[]
)
def system_prompt() -> List[Dict[str, Any]]:
    """Generate system prompt for AI assistant"""
    return [
        {
            "role": "system",
            "content": {
                "type": "text",
                "text": "You are a helpful AI assistant with access to tools and resources. Use the available tools to help users with their requests. Always be accurate and helpful."
            }
        }
    ]


@prompt(
    description="Code review prompt",
    arguments=[
        {"name": "language", "description": "Programming language", "required": True}
    ]
)
def code_review(language: str) -> List[Dict[str, Any]]:
    """Generate code review prompt"""
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"You are a {language} code expert. Please review the following {language} code for best practices, potential bugs, and suggest improvements."
            }
        }
    ]
# ============================================================================
# RUN THE SERVER
# ============================================================================

if __name__ == "__main__":
    server = create_server(name="my-agent-server", version="1.0.0")
    server.run(host="0.0.0.0", port=8002)