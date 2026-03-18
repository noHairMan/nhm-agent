"""Reflection Agent.

This module defines a reflection agent graph.
"""

from typing import Any, AsyncGenerator, Dict

from langchain_core.messages import AIMessage

from mercedes.core.agent import BaseAgent

from .graph import graph


class ReflectionAgent(BaseAgent):
    """
    通过生成、反思、修正的循环过程来提高回答质量的 Agent。
    """

    async def ainvoke(self, input_text: str, config: Dict[str, Any]) -> AIMessage:
        """
        调用 Reflection Agent 并返回最终生成的 AIMessage。
        """
        inputs = {"messages": [("user", input_text)]}
        context = {"model": None}
        result = await graph.ainvoke(inputs, context=context, config=config)
        return AIMessage(content=result["generation"])

    async def astream(self, input_text: str, config: Dict[str, Any]) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式返回图执行过程中的更新。
        """
        inputs = {"messages": [("user", input_text)]}
        context = {"model": None}
        async for output in graph.astream(inputs, context=context, config=config, stream_mode="updates"):
            yield output
