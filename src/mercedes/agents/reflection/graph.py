from string import Template
from typing import Any, Dict, Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime

from mercedes.agents.reflection.context import Context
from mercedes.agents.reflection.state import GenerationOutput, InputState, ReflectionOutput, ReflectionState
from mercedes.core.llm import get_llm
from mercedes.tools import tools
from mercedes.utils.aimessage import get_latest_human_message


async def call_tools(state: ReflectionState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """在生成前，先调用工具收集所需信息。"""
    llm = get_llm(runtime.context.model).bind_tools(tools)

    reflection_info = ""
    if state.reflection:
        reflection_info = (
            f"\n\n之前的生成内容：\n{state.generation}"
            f"\n\n之前的反思建议：\n{state.reflection}"
            "\n\n请根据以上反思建议，判断是否需要调用工具收集更多信息来改进生成内容。"
        )

    response = await llm.ainvoke(
        [
            SystemMessage(
                content=(
                    "你是一个助手，负责调用合适的工具来收集信息，以便后续生成高质量内容。"
                    "请注意：参考历史消息中的工具调用结果，避免重复调用已经执行过且获得结果的工具。"
                    f"{reflection_info}"
                ),
            ),
            *state.messages,
        ],
    )
    return {"messages": [response]}


async def generator(state: ReflectionState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """负责生成内容的节点。"""
    llm = get_llm(runtime.context.model).with_structured_output(GenerationOutput)
    reflection_context = ""
    if state.reflection:
        reflection_context = (
            f"之前的生成内容：\n{state.generation}\n\n"
            f"针对该内容的反思建议：\n{state.reflection}\n\n"
            "请根据以上建议进行改进并重新生成完整的内容。"
        )

    system_prompt = Template(runtime.context.generator_prompt).safe_substitute(reflection_context=reflection_context)

    response = await llm.ainvoke(
        [
            SystemMessage(content=system_prompt),
            *state.messages,
        ],
    )
    return response | {"iterations": state.iterations + 1}


def route_after_tools(state: ReflectionState) -> Literal["tools", "generator"]:
    """判断是否需要执行工具调用。"""
    last_message = state.messages[-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "generator"


async def reflector(state: ReflectionState, runtime: Runtime[Context]) -> Dict[str, Any]:
    """负责对生成内容进行反思和批评的节点。"""
    llm = get_llm(runtime.context.model).with_structured_output(ReflectionOutput)
    user_request = get_latest_human_message(state.messages) or "请根据我的要求生成内容。"

    user_content = (
        f"用户的原始请求是：\n{user_request}\n\n"
        f"当前的生成内容是：\n{state.generation}\n\n"
        f"请基于以上信息进行评估。"
    )

    response = await llm.ainvoke(
        [
            SystemMessage(content=runtime.context.reflector_prompt),
            HumanMessage(content=user_content),
        ],
    )
    return response


def should_continue(state: ReflectionState, runtime: Runtime[Context]) -> Literal["call_tools", "generator", "__end__"]:
    """判断是否需要继续进行反思循环。"""
    if state.satisfied or state.iterations >= runtime.context.max_iterations:
        return END
    if state.needs_more_info:
        return "call_tools"
    return "generator"


builder = StateGraph(ReflectionState, input_schema=InputState, context_schema=Context)
builder.add_node("call_tools", call_tools)
builder.add_node("tools", ToolNode(tools))
builder.add_node("generator", generator)
builder.add_node("reflector", reflector)

builder.set_entry_point("call_tools")
builder.add_conditional_edges("call_tools", route_after_tools)
builder.add_edge("tools", "generator")
builder.add_edge("generator", "reflector")
builder.add_conditional_edges("reflector", should_continue)

graph = builder.compile(name="Reflection")
