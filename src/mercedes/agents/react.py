from typing import Annotated, Sequence

from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from mercedes.core.agent import BaseAgent
from mercedes.core.llm import get_llm
from mercedes.tools.basic import get_default_tools


class AgentState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], add_messages]


class ReActAgent(BaseAgent):
    def __init__(self, name: str, model_name: str = None):
        super().__init__(name, model_name)
        self.llm = get_llm(model_name)
        self.tools = get_default_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        # 定义节点
        def call_model(state: AgentState):
            response = self.llm_with_tools.invoke(state.messages)
            return {"messages": [response]}

        tool_node = ToolNode(self.tools)

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
        inputs = {"messages": [("user", input_text)]}
        async for output in self.graph.astream(inputs):
            for key, value in output.items():
                print(f"Node '{key}' finished.")

        # final_state = await self.graph.aget_state(inputs)
        # 直接使用 ainvoke 获取最终状态
        state = await self.graph.ainvoke(inputs)
        return state["messages"][-1].content
