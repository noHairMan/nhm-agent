from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


async def get_mcp_tools_and_sessions() -> list[BaseTool]:
    """
    Load tools from all configured MCP servers and return tools along with their session stack.
    """
    client = MultiServerMCPClient(
        {
            # Example:
            "nhm-django-infra": {
                "transport": "http",  # HTTP-based remote server
                # Ensure you start your weather server on port 8000
                "url": "http://localhost:3002/mcp",
                "headers": {"Authorization": "Basic bmhtOk1VdTdPalpmY01Jb0l0", "X-Custom-Header": "custom-value"},
            },
        },
    )
    return await client.get_tools()
