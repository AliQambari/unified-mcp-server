import asyncio
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from langchain_core.messages.utils import count_tokens_approximately, trim_messages
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.resources import load_mcp_resources
from langchain_mcp_adapters.prompts import load_mcp_prompt
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt.chat_agent_executor import AgentState
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from colorama import Fore, Style, init

init(autoreset=True)
load_dotenv()

SERVER_URL = "http://localhost:8000/mcp"
CONFIG = {"configurable": {"thread_id": "1"}}

# --------------------------
# Hooks
# --------------------------
def pre_model_hook(state: AgentState) -> dict[str, list[AnyMessage]]:
    """Trim messages before LLM invocation"""
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=30_000,
        start_on="human",
        end_on=("human", "tool"),
        include_system=True,
    )
    return {"llm_input_messages": trimmed_messages}

# --------------------------
# Resource Fetching Tool
# --------------------------
class FetchResourceInput(BaseModel):
    uri: str = Field(description="The MCP resource URI to fetch (e.g., 'schema://table/users')")

async def fetch_mcp_resource(uri: str, session: ClientSession) -> str:
    """Fetch a specific MCP resource by URI"""
    try:
        resources = await load_mcp_resources(session, uris=[uri])
        if not resources:
            return f"❌ No resource found for URI: {uri}"
        return str(resources[0].data)
    except Exception as e:
        return f"❌ Error fetching resource {uri}: {str(e)}"

async def create_fetch_tool(session: ClientSession) -> StructuredTool:
    """Create the fetch resource tool"""
    async def bound_fetch_resource(uri: str) -> str:
        return await fetch_mcp_resource(uri, session)

    return StructuredTool.from_function(
        func=bound_fetch_resource,
        name="fetch_mcp_resource",
        description=(
            "Fetch the content of a specific MCP resource by its URI. "
            "Available URIs are listed in the system prompt."
        ),
        args_schema=FetchResourceInput,
        return_direct=False,
        coroutine=bound_fetch_resource,
    )

# --------------------------
# Pre-load Resources
# --------------------------
async def get_available_resources(session: ClientSession) -> str:
    """Get a formatted list of all available resources"""
    try:
        result = await session.list_resources()
        if not result or not result.resources:
            return "No resources available."
        
        output = "📚 AVAILABLE RESOURCES:\n\n"
        for res in result.resources:
            output += f"  • URI: {res.uri}\n"
            output += f"    Name: {res.name}\n"
            if res.description:
                output += f"    Description: {res.description}\n"
            output += "\n"
        return output
    except Exception as e:
        return f"Error loading resources: {str(e)}"

# --------------------------
# Stream printer with tool tracking
# --------------------------
async def print_stream_with_tools(agent, initial_state, config):
    """Print agent stream and track tool calls"""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    tool_calls = []
    final_response = None
    
    async for chunk in agent.astream(initial_state, config=config, stream_mode="updates"):
        for node, update in chunk.items():
            messages = update.get("messages", [])
            
            for msg in messages:
                # Track tool calls
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        tool_name = tool_call.get("name", "unknown")
                        tool_args = tool_call.get("args", {})
                        tool_calls.append((tool_name, tool_args))
                        print(f"{Fore.YELLOW}🔧 Calling tool: {Fore.GREEN}{tool_name}{Style.RESET_ALL}")
                        print(f"{Fore.YELLOW}   Args: {Fore.WHITE}{tool_args}{Style.RESET_ALL}\n")
                
                # Track tool responses
                elif hasattr(msg, "content") and hasattr(msg, "name"):
                    # This is a tool message
                    content = str(msg.content)
                    if len(content) > 300:
                        content = content[:300] + "..."
                    print(f"{Fore.YELLOW}✅ Tool result: {Fore.WHITE}{content}{Style.RESET_ALL}\n")
                
                # Track final assistant message
                elif hasattr(msg, "content") and msg.__class__.__name__ == "AIMessage":
                    if not hasattr(msg, "tool_calls") or not msg.tool_calls:
                        final_response = msg.content
    
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Final Answer:{Style.RESET_ALL}\n")
    if final_response:
        print(f"{Fore.WHITE}{final_response}{Style.RESET_ALL}\n")
    
    if tool_calls:
        print(f"{Fore.MAGENTA}📊 Tools used: {', '.join([t[0] for t in tool_calls])}{Style.RESET_ALL}\n")

# --------------------------
# Main
# --------------------------
async def main():
    async with streamablehttp_client(SERVER_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print(f"{Fore.CYAN}Initializing MCP Agent...{Style.RESET_ALL}")

            # Load MCP tools
            mcp_tools = await load_mcp_tools(session)
            print(f"{Fore.GREEN}✅ Loaded {len(mcp_tools)} MCP tools{Style.RESET_ALL}")

            # PRE-LOAD all available resources
            print(f"{Fore.CYAN}📚 Loading available resources...{Style.RESET_ALL}")
            available_resources_text = await get_available_resources(session)
            print(f"{Fore.GREEN}✅ Resources loaded{Style.RESET_ALL}\n")

            # Load system prompt
            try:
                mcp_prompts = await load_mcp_prompt(session, "system_prompt")
                base_system_prompt = mcp_prompts[0].content if mcp_prompts else "You are a helpful assistant."
            except:
                base_system_prompt = "You are a helpful assistant."

            # Build system prompt WITH pre-loaded resources
            system_prompt = f"""{base_system_prompt}

{available_resources_text}

INSTRUCTIONS:
- The resources listed above are available for you to fetch
- To access a resource's content, use the 'fetch_mcp_resource' tool with the exact URI shown above
- You do NOT need to list resources first - they are already shown above
- Simply use fetch_mcp_resource when you need the content of any listed resource

Example:
User: "Show me the schema for users table"
You: Use fetch_mcp_resource with uri="schema://table/users"
"""

            # Prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder("messages")
            ])

            # Create fetch tool
            fetch_tool = await create_fetch_tool(session)
            all_tools = mcp_tools + [fetch_tool]

            print(f"{Fore.GREEN}✅ Total tools: {len(all_tools)} (MCP: {len(mcp_tools)}, Resource: 1){Style.RESET_ALL}")

            # LLM
            llm = ChatOpenAI(
                model="x-ai/grok-4-fast:free",
                temperature=0,
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            )

            # Create agent
            agent = create_react_agent(
                llm,
                all_tools,
                prompt=prompt_template,
                checkpointer=InMemorySaver(),
                pre_model_hook=pre_model_hook
            )

            # Chat loop
            print(f"\n{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}🤖 MCP Agent Ready{Style.RESET_ALL}")
            print(f"{Fore.MAGENTA}{'='*60}{Style.RESET_ALL}")
            print(f"\n{Fore.WHITE}💡 Try:{Style.RESET_ALL}")
            print(f"  - What resources are available?")
            print(f"  - Show me the schema for users table")
            print(f"  - What is Ali's age?\n")

            while True:
                user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
                
                if user_input.lower() in {"quit", "exit", "q"}:
                    print(f"\n{Fore.MAGENTA}Goodbye! 👋{Style.RESET_ALL}\n")
                    break

                if not user_input.strip():
                    continue

                # Run agent with streaming
                await print_stream_with_tools(
                    agent,
                    {"messages": [{"role": "user", "content": user_input}]},
                    CONFIG
                )

if __name__ == "__main__":
    asyncio.run(main())