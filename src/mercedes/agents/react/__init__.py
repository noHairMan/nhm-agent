"""React Agent.

This module defines a custom reasoning and action agent graph.
It invokes tools in a simple loop.
"""

from mercedes.core.agent import BaseAgent

from .graph import graph


class ReactAgent(BaseAgent):
    async def ainvoke(self, input_text: str):
        inputs = {"messages": [("user", input_text)]}
        context = {"model": None}
        return await graph.ainvoke(inputs, context=context, stream_mode="values")

    async def astream(self, input_text: str):
        inputs = {"messages": [("user", input_text)]}
        context = {"model": None}
        async for output in graph.astream(inputs, context=context, stream_mode="values"):
            yield output
