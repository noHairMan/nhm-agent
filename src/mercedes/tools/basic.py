import ujson
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import tool
from pydantic import BaseModel

from mercedes.tools.rag import rag_add_document, rag_search


@tool
def get_datetime() -> str:
    """获取当前日期和时间。"""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


duck_search = DuckDuckGoSearchResults(output_format="json")


class SearchJsonResult(BaseModel):
    snippet: str
    title: str
    link: str


@tool("web_search")
async def search(query: str) -> list[SearchJsonResult]:
    """Search the web for information."""
    content = await duck_search.ainvoke(query)
    results = ujson.loads(content)
    return results


def get_default_tools():
    return [
        get_datetime,
        search,
        rag_search,
        rag_add_document,
    ]


tools = get_default_tools()
