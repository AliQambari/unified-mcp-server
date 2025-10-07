from dotenv import load_dotenv
from langchain_core.messages import AnyMessage
from langchain_core.messages.utils import count_tokens_approximately, trim_messages
from langchain_core.tools import StructuredTool
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_mcp_adapters.resources import load_mcp_resources
from langchain_mcp_adapters.prompts import load_mcp_prompt
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from pydantic import BaseModel, Field
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import asyncio
from dotenv import load_dotenv

load_dotenv()

# -------------------
# Server Parameters
# -------------------
server_url = "http://localhost:8000/mcp"  #"http://localhost:8000/mcp"

# -------------------
# Resource Listing Tool (NEW!)
# -------------------
class ListResourcesInput(BaseModel):
    """Input schema for listing available resources"""
    pass  # No input needed

async def list_available_resources(session: ClientSession) -> str:
    """
    List all available MCP resources from the server.
    Returns a formatted string of available resource URIs.
    """
    try:
        # Call the server's list_resources
        result = await session.list_resources()
        
        if not result or not result.resources:
            return "No resources available on the server."
        
        # Format the resources
        output = "Available MCP Resources:\n\n"
        for resource in result.resources:
            output += f"📦 URI: {resource.uri}\n"
            output += f"   Name: {resource.name}\n"
            if resource.description:
                output += f"   Description: {resource.description}\n"
            output += "\n"
        
        return output
    except Exception as e:
        return f"Error listing resources: {str(e)}"

# -------------------
# Resource Fetching Tool
# -------------------
class FetchResourceInput(BaseModel):
    uri: str = Field(description="The MCP resource URI to fetch (e.g., 'schema://table/users')")

async def fetch_mcp_resource(uri: str, session: ClientSession) -> str:
    """
    Fetch an MCP resource by URI and return its data as a string.
    """
    try:
        resources = await load_mcp_resources(session, uris=[uri])
        if not resources:
            return f"No resource found for URI: {uri}"
        return str(resources[0].data)
    except Exception as e:
        return f"Error fetching resource {uri}: {str(e)}"

# -------------------
# Dynamic Tool Creation
# -------------------
async def create_resource_tools(session: ClientSession) -> list[StructuredTool]:
    """Create both list and fetch resource tools"""
    
    # List resources tool
    async def bound_list_resources() -> str:
        return await list_available_resources(session)
    
    list_tool = StructuredTool.from_function(
        func=bound_list_resources,
        name="list_mcp_resources",
        description=(
            "List all available MCP resources from the server. "
            "Use this FIRST to discover what resources are available before fetching them."
        ),
        args_schema=ListResourcesInput,
        return_direct=False,
        coroutine=bound_list_resources,
    )
    
    # Fetch resource tool
    async def bound_fetch_resource(uri: str) -> str:
        return await fetch_mcp_resource(uri, session)
    
    fetch_tool = StructuredTool.from_function(
        func=bound_fetch_resource,
        name="fetch_mcp_resource",
        description=(
            "Fetch an MCP resource by its URI and return its content. "
            "Use list_mcp_resources first to find available URIs. "
            "Example URIs: 'config://app/settings', 'file://docs/readme'"
        ),
        args_schema=FetchResourceInput,
        return_direct=False,
        coroutine=bound_fetch_resource,
    )
    
    return [list_tool, fetch_tool]

# -------------------
# Config + Hooks
# -------------------
CONFIG = {"configurable": {"thread_id": "1"}}

def pre_model_hook(state: AgentState) -> dict[str, list[AnyMessage]]:
    """
    Trim messages before LLM invocation to manage token limits.
    """
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

async def print_astream(async_stream, output_messages_key: str = "llm_input_messages") -> None:
    """
    Print the stream of messages from the agent.
    """
    async for chunk in async_stream:
        for node, update in chunk.items():
            print(f"Update from node: {node}")
            messages_key = output_messages_key if node == "pre_model_hook" else "messages"
            for message in update[messages_key]:
                if isinstance(message, tuple):
                    print(message)
                else:
                    message.pretty_print()
        print("\n\n")

# -------------------
# Main entry
# -------------------
async def main():
    async with streamablehttp_client(server_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Load MCP tools
            mcp_tools = await load_mcp_tools(session)
            
            print(f"✅ Loaded {len(mcp_tools)} MCP tools")

            # Load system prompt (optional)
            try:
                mcp_prompts = await load_mcp_prompt(session, "system_prompt")
                base_system_prompt = mcp_prompts[0].content if mcp_prompts else \
                    "You are a helpful assistant with access to MCP tools and resources."
            except:
                base_system_prompt = "You are a helpful assistant with access to MCP tools and resources."
            
            system_prompt = base_system_prompt + (
                "\n\n**Important Instructions for Resources:**"
                "\n1. When asked about available data or resources, FIRST use 'list_mcp_resources' to discover what's available"
                "\n2. After finding the URI you need, use 'fetch_mcp_resource' with that specific URI"
                "\n3. Resource URIs available: 'config://app/settings', 'file://docs/readme', etc."
                "\n\nAlways list resources before trying to fetch them!"
            )

            # Prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder("messages"),
            ])

            # Create resource tools (list + fetch)
            resource_tools = await create_resource_tools(session)
            allowed_tools = mcp_tools + resource_tools
            
            print(f"✅ Total tools available: {len(allowed_tools)}")
            print(f"   - MCP tools: {len(mcp_tools)}")
            print(f"   - Resource tools: {len(resource_tools)}")
            print(f"\n📋 Resource tools: {[t.name for t in resource_tools]}")

            # LLM
            """
            import os
            llm = ChatOpenAI(
                model="deepseek/deepseek-chat-v3.1:free",
                temperature=0,
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1"
            )
            """
            import google.generativeai as genai
            from langchain_google_genai import ChatGoogleGenerativeAI
            import os
            #pip install google-generativeai langchain-google-genai python-dotenv
            # Replace with your actual API key
            GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

            # Configure the generative AI with your API key
            genai.configure(api_key=GOOGLE_API_KEY)

            # Initialize the ChatGoogleGenerativeAI model
            # You can choose a different model name if needed, e.g., "gemini-pro"
            llm_google = ChatGoogleGenerativeAI(model="gemini-2.5-flash-preview-05-20", google_api_key=GOOGLE_API_KEY)


            llm = llm_google

            # Agent
            agent = create_react_agent(
                llm,
                allowed_tools,
                prompt=prompt_template,
                checkpointer=InMemorySaver(),
                pre_model_hook=pre_model_hook,
            )

            # Chat loop
            print("\n================== Chat =================")
            print("💡 Tip: Try asking 'What resources are available?' or 'List all schemas'\n")
            
            while True:
                user_input = input("> ")
                if user_input.lower() in {"exit", "quit", "q"}:
                    break

                await print_astream(
                    agent.astream({"messages": [{"role": "user", "content": user_input}]},
                                 config=CONFIG, stream_mode="updates")
                )

if __name__ == "__main__":
    asyncio.run(main())