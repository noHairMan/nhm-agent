from .basic import get_datetime, search
from .mcp import get_mcp_tools_and_sessions
from .rag import rag_search


def get_default_tools():
    return [
        get_datetime,
        search,
        rag_search,
    ]


tools = get_default_tools()
