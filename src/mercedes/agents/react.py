from pprint import pformat
from typing import Annotated, Sequence

from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel

from mercedes.core.agent import BaseAgent
from mercedes.core.llm import get_llm
from mercedes.tools.basic import get_default_tools
from mercedes.tools.mcp import get_mcp_tools_and_sessions
from mercedes.utils.log import logger


class AgentState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], add_messages]


class ReActAgent(BaseAgent):
    def __init__(self, name: str, model_name: str = None):
        super().__init__(name, model_name)
        self.llm = get_llm(model_name)
        self.tools = get_default_tools()
        self.graph = None
        self.llm_with_tools = None

    async def initialize(self):
        """异步初始化，加载 MCP 工具并构建图"""
        mcp_tools = await get_mcp_tools_and_sessions()
        if mcp_tools:
            self.tools.extend(mcp_tools)

        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.graph = self._build_graph()

    async def close(self):
        pass

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # 定义节点
        def call_model(state: AgentState):
            response = self.llm_with_tools.invoke(state.messages)
            return {"messages": [response]}

        tool_node = ToolNode(self.tools, handle_tool_errors=True)  # 工具错误会返回错误以让大模型自动纠错

        workflow.add_node("agent", call_model)
        workflow.add_node("action", tool_node)

        workflow.set_entry_point("agent")

        # 定义边
        def should_continue(state: AgentState):
            messages = state.messages
            last_message = messages[-1]
            if last_message.tool_calls:
                return "action"
            return "end"

        workflow.add_conditional_edges(
            "agent",
            should_continue,
            {
                "action": "action",
                "end": END,
            },
        )
        workflow.add_edge("action", "agent")

        return workflow.compile()

    async def run(self, input_text: str) -> str:
        if self.graph is None:
            await self.initialize()

        inputs = {"messages": [("user", input_text)]}
        async for output in self.graph.astream(inputs):
            for key, value in output.items():
                logger.info(f"Node '{key}' finished. value: {pformat(value)}")

        state = await self.graph.ainvoke(inputs)
        return state["messages"][-1].content
