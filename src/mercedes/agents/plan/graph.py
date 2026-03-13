"""定义计划与执行 (Plan-and-Execute) 代理。

该代理使用两步过程：首先，根据用户的请求创建一个计划；
然后，执行计划的每一步，并根据需要重新评估和更新计划。
"""

from typing import Dict, List, Literal, Optional, TypedDict, Union, cast

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, StateGraph
from langgraph.runtime import Runtime

from mercedes.agents.plan.context import Context
from mercedes.agents.plan.state import (
    InputState,
    Plan,
    PlanExecuteState,
)
from mercedes.core.llm import get_llm
from mercedes.tools.basic import tools


async def planner(state: PlanExecuteState, runtime: Runtime[Context]) -> Dict:
    """规划解决用户请求的步骤。"""
    llm = get_llm(runtime.context.model).with_structured_output(Plan)

    # 从第一条人类消息中获取用户的目标
    objective = ""
    for message in state.messages:
        if isinstance(message, HumanMessage):
            objective = cast(str, message.content)
            break

    system_prompt = runtime.context.planner_prompt
    response = await llm.ainvoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=objective),
        ],
    )
    return {"plan": response["steps"]}


async def executor(state: PlanExecuteState, runtime: Runtime[Context]) -> Dict:
    """执行计划中的下一步。"""
    if not state.plan:
        return {"response": "抱歉，我找不到可执行的计划。"}

    task = state.plan[0]
    llm = get_llm(runtime.context.model)

    agent_executor = create_agent(llm, tools)

    past_steps_context = "\n".join([f"Step: {s}\nResult: {r}" for s, r in state.past_steps])
    task_input = f"""当前任务: {task}

以往步骤上下文:
{past_steps_context}

请解决当前任务。"""

    result = await agent_executor.ainvoke({"messages": [HumanMessage(content=task_input)]})

    return {
        "past_steps": [(task, result["messages"][-1].content)],
        "plan": state.plan[1:],
    }


# --- 修复：扁平化结构，让 LLM 更容易判断何时给出最终答案 ---
class Act(TypedDict):
    """要执行的操作：提供最终回复或新计划。"""

    action: Literal["respond", "replan"]
    """'respond' 表示已达成目标；'replan' 表示需要更多步骤。"""

    response: Optional[str]
    """给用户的最终回复。当 action='respond' 时需要。"""

    steps: Optional[List[str]]
    """修改后的计划步骤。当 action='replan' 时需要。"""


async def replanner(state: PlanExecuteState, runtime: Runtime[Context]) -> Dict:
    """根据执行结果重新评估计划。"""
    llm = get_llm(runtime.context.model).with_structured_output(Act)

    objective = ""
    for message in state.messages:
        if isinstance(message, HumanMessage):
            objective = cast(str, message.content)
            break

    past_steps = "\n".join([f"Step: {s}\nResult: {r}" for s, r in state.past_steps])

    system_prompt = runtime.context.replanner_prompt.format(
        objective=objective,
        plan="\n".join(state.plan),
        past_steps=past_steps,
    )

    response = await llm.ainvoke(
        [
            SystemMessage(content=system_prompt),
        ],
    )

    if response.get("action") == "respond" and response.get("response"):
        return {"response": response["response"], "plan": []}
    else:
        new_steps = response.get("steps") or []
        return {"plan": new_steps}


def should_continue(state: PlanExecuteState) -> Literal["executor", "__end__"]:
    """确定是继续执行还是结束。"""
    if state.response or not state.plan:
        return "__end__"
    return "executor"


# 构建图
builder = StateGraph(PlanExecuteState, input_schema=InputState, context_schema=Context)

builder.add_node("planner", planner)
builder.add_node("executor", executor)
builder.add_node("replanner", replanner)

builder.add_edge("__start__", "planner")
builder.add_edge("planner", "executor")
builder.add_edge("executor", "replanner")

builder.add_conditional_edges(
    "replanner",
    should_continue,
)

checkpointer = InMemorySaver()
graph = builder.compile(name="计划与执行代理", checkpointer=checkpointer)
