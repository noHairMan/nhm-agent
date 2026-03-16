"""定义自定义的推理与动作 (Reasoning and Action, ReAct) 代理图。

配合支持工具调用的聊天模型工作。
"""

from datetime import UTC, datetime
from string import Template
from typing import Dict, List, Literal, cast

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime

from mercedes.agents.react.context import Context
from mercedes.agents.react.state import InputState, State
from mercedes.core.llm import get_llm
from mercedes.tools import tools


async def call_model(state: State, runtime: Runtime[Context]) -> Dict[str, List[AIMessage]]:
    """调用驱动我们"代理"的 LLM。

    该函数准备提示词，初始化模型，并处理响应。

    参数:
        state (State): 对话的当前状态。
        runtime (Runtime[Context]): 运行时的上下文信息。

    返回:
        dict: 包含模型响应消息的字典。
    """
    # 使用工具绑定初始化模型。在此更改模型或添加更多工具。
    model = get_llm(runtime.context.model).bind_tools(tools)

    # 格式化系统提示词。自定义此处以更改代理的行为。
    system_message = Template(runtime.context.system_prompt).safe_substitute(
        system_time=datetime.now(tz=UTC).isoformat(),
    )

    # 获取模型响应
    response = cast(  # type: ignore[redundant-cast]
        AIMessage,
        await model.ainvoke([{"role": "system", "content": system_message}, *state.messages]),
    )

    # 处理最后一步且模型仍想使用工具的情况
    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="抱歉，我无法在指定的步数内找到您问题的答案。",
                ),
            ],
        }

    # 将模型的响应作为列表返回，以便添加到现有消息中
    return {"messages": [response]}


def route_model_output(state: State) -> Literal["__end__", "tools"]:
    """根据模型的输出确定下一个节点。

    该函数检查模型的最后一条消息是否包含工具调用。

    参数:
        state (State): 对话的当前状态。

    返回:
        str: 下一个要调用的节点名称（"__end__" 或 "tools"）。
    """
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(f"预期输出边中为 AIMessage，但得到的是 {type(last_message).__name__}")
    # 如果没有工具调用，则结束
    if not last_message.tool_calls:
        return "__end__"
    # 否则执行请求的操作
    return "tools"


# 定义一个新图
builder = StateGraph(State, input_schema=InputState, context_schema=Context)

# 定义我们将在其间循环的两个节点
builder.add_node(call_model)
builder.add_node("tools", ToolNode(tools))

# 设置入口点为 `call_model`
builder.add_edge("__start__", "call_model")

# 添加条件边以确定 `call_model` 之后的下一步
builder.add_conditional_edges(
    "call_model",
    # call_model 运行结束后，根据 route_model_output 的输出安排下一个节点
    route_model_output,
)

# 添加从 `tools` 到 `call_model` 的普通边
# 这创建了一个循环：使用工具后，我们总是返回到模型
builder.add_edge("tools", "call_model")

checkpointer = InMemorySaver()
# 将构建器编译为可执行的图
graph = builder.compile(name="ReAct", checkpointer=checkpointer)
