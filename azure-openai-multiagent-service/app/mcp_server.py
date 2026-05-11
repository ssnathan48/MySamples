from fastmcp import FastMCP

mcp = FastMCP("FoundryTools")

@mcp.tool()
async def write_to_file(filename: str, content: str) -> str:
    """Writes content to a local text file."""
    with open(filename, "w") as f:
        f.write(content)
    return f"Successfully saved to {filename}"

@mcp.tool()
async def read_from_file(filename: str) -> str:
    """Reads a local text file."""
    try:
        with open(filename, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Error: File not found."
