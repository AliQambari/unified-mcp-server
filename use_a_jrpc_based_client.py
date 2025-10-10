from fastmcp import Client
import asyncio

async def main():
    client = Client("http://localhost:8002/mcp")  
    async with client:
        
        # Call your list_tables tool
        result = await client.call_tool("list_tables", {
            "db_type": "postgres", 
            "db_name": "kmp"
        })
        print("Database tables:", result.content[0].text)
        
        # Call your add tool
        result = await client.call_tool("add", {
            "a": 15, 
            "b": 27
        })
        print("Addition result:", result.content[0].text)
        
        # Call your analyze_sentiment tool
        result = await client.call_tool("analyze_sentiment", {
            "text": "This is a great tool!"
        })
        print("Sentiment analysis:", result.content[0].text)
        
        # Call your search tool
        result = await client.call_tool("search", {
            "query": "python programming",
            "max_results": 3
        })
        print("Search results:", result.content[0].text)

asyncio.run(main())
