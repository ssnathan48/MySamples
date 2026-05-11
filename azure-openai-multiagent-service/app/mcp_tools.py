from fastmcp import FastMCP

mcp = FastMCP("AzureAgentTools")

@mcp.tool()
def get_weather(location: str) -> str:
    """Useful for finding the current weather in a specific city."""
    # In a real demo, you'd call an actual API here
    return f"The weather in {location} is currently 72°F and sunny."

@mcp.tool()
def search_knowledge_base(query: str) -> str:
    """Searches the internal grounding data for specific info."""
    return f"Search result for '{query}': Information retrieved from grounding.json."
