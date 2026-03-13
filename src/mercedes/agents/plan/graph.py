"""定义基于 LLMCompiler 模式的计划与执行代理。

LLMCompiler 架构包含三个核心组件：
- Planner（规划器）：生成带依赖关系的任务 DAG，支持并行执行
- Task Fetching Unit（任务调度单元）：按依赖顺序并行调度执行任务
- Joiner（决策器）：根据执行结果决定直接回复用户或重新规划

相比传统顺序执行的 Plan-and-Execute，LLMCompiler 通过并行执行独立任务
显著缩短运行时间（论文报告可达 3.6x 加速）。
"""

import asyncio
from typing import Any, Dict, Literal, cast

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime

from mercedes.agents.plan.context import Context
from mercedes.agents.plan.state import (
    InputState,
    JoinerDecision,
    LLMCompilerPlan,
    PlanExecuteState,
    Task,
)
from mercedes.core.llm import get_llm
from mercedes.tools import tools

# 构建工具名称到工具实例的映射
_tool_map = {t.name: t for t in tools}

# 生成工具描述字符串（供 Planner 提示词使用）
_tool_descriptions = "\n".join(f"- {t.name}: {t.description}" for t in tools)


def _substitute_vars(args: dict[str, Any], results: dict[int, str]) -> dict[str, Any]:
    """将任务参数中的 $<idx> 变量替换为对应任务的执行结果。"""
    substituted = {}
    for key, value in args.items():
        if isinstance(value, str) and value.startswith("$"):
            try:
                dep_idx = int(value[1:])
                substituted[key] = results.get(dep_idx, value)
            except ValueError:
                substituted[key] = value
        else:
            substituted[key] = value
    return substituted


async def planner(state: PlanExecuteState, runtime: Runtime[Context]) -> Dict:
    """规划器：生成带依赖关系的任务 DAG。

    独立任务将在 Task Fetching Unit 中并行执行；
    依赖其他任务结果的任务将在依赖完成后再调度。
    """
    llm = get_llm(runtime.context.model).with_structured_output(LLMCompilerPlan)

    # 获取用户目标
    objective = ""
    for message in state.messages:
        if isinstance(message, HumanMessage):
            objective = cast(str, message.content)
            break

    # 构建历史步骤上下文（重新规划时使用）
    if state.past_steps:
        past_lines = "\n".join(f"  - {step}: {result}" for step, result in state.past_steps)
        past_steps_section = f"已完成的历史步骤（请勿重复执行）：\n{past_lines}"
    else:
        past_steps_section = ""

    system_prompt = runtime.context.planner_prompt.format(
        tool_descriptions=_tool_descriptions,
        past_steps_section=past_steps_section,
    )

    response = await llm.ainvoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=objective),
        ],
    )

    return {
        "tasks": response.get("tasks", []),
        "results": {},
        "thought": response.get("thought", ""),
    }


async def _execute_task(task: Task, results: dict[int, str]) -> tuple[int, str]:
    """执行单个任务，支持变量替换。"""
    tool_fn = _tool_map.get(task["tool"])
    if tool_fn is None:
        return task["idx"], f"错误：工具 '{task['tool']}' 不存在"

    args = _substitute_vars(task["args"], results)
    try:
        result = await tool_fn.ainvoke(args)
        return task["idx"], str(result)
    except Exception as e:
        return task["idx"], f"执行错误：{e}"


async def task_fetching_unit(state: PlanExecuteState, runtime: Runtime[Context]) -> Dict:
    """任务调度单元：按依赖关系波次并行执行任务 DAG。

    算法：
    1. 找出所有依赖已满足的就绪任务
    2. 并行执行该批次所有就绪任务
    3. 将结果合并，重复直至所有任务完成
    """
    pending: dict[int, Task] = {t["idx"]: t for t in state.tasks}
    completed: set[int] = set()
    results: dict[int, str] = {}

    while pending:
        # 找出当前批次所有依赖已满足的就绪任务
        ready = [t for idx, t in pending.items() if all(dep in completed for dep in t["dependencies"])]

        if not ready:
            # 存在循环依赖或无法推进，退出避免死循环
            break

        # 并行执行本批次所有就绪任务
        batch_results = await asyncio.gather(*[_execute_task(t, results) for t in ready])

        for idx, result in batch_results:
            results[idx] = result
            completed.add(idx)
            pending.pop(idx, None)

    return {"results": results}


async def joiner(state: PlanExecuteState, runtime: Runtime[Context]) -> Dict:
    """决策器：根据任务执行结果决定直接回复用户或重新规划。"""
    llm = get_llm(runtime.context.model).with_structured_output(JoinerDecision)

    # 获取用户目标
    objective = ""
    for message in state.messages:
        if isinstance(message, HumanMessage):
            objective = cast(str, message.content)
            break

    # 构建本轮任务执行摘要
    tasks_summary = "\n".join(
        f"  任务 {t['idx']} [{t['tool']}({t['args']}), 依赖: {t['dependencies']}]"
        f"\n    结果: {state.results.get(t['idx'], '未执行')}"
        for t in state.tasks
    )

    # 构建历史步骤上下文
    if state.past_steps:
        past_lines = "\n".join(f"  - {step}: {result}" for step, result in state.past_steps)
        past_steps_context = f"历史执行步骤：\n{past_lines}\n\n"
    else:
        past_steps_context = ""

    user_content = (
        f"用户目标：{objective}\n\n"
        f"{past_steps_context}"
        f"本轮任务执行结果：\n{tasks_summary}\n\n"
        f"请根据以上信息决定：是直接回复用户（respond），还是需要重新规划（replan）？"
    )

    response = await llm.ainvoke(
        [
            SystemMessage(content=runtime.context.joiner_prompt),
            HumanMessage(content=user_content),
        ],
    )

    if response.get("action") == "respond" and response.get("response"):
        return {
            "response": response["response"],
            "thought": response.get("thought", ""),
        }

    # 重新规划：将本轮任务结果归入历史，清空当前轮次状态
    new_past_steps = [
        (
            f"{t['tool']}({t['args']})",
            state.results.get(t["idx"], "未执行"),
        )
        for t in state.tasks
    ]
    return {
        "tasks": [],
        "results": {},
        "past_steps": new_past_steps,
        "thought": response.get("thought", ""),
    }


def should_continue(state: PlanExecuteState) -> Literal["planner", "__end__"]:
    """根据 Joiner 的决策结果决定流程走向。"""
    if state.response:
        return "__end__"
    return "planner"


# 构建图
builder = StateGraph(PlanExecuteState, input_schema=InputState, context_schema=Context)

builder.add_node("planner", planner)
builder.add_node("task_fetching_unit", task_fetching_unit)
builder.add_node("joiner", joiner)

builder.add_edge("__start__", "planner")
builder.add_edge("planner", "task_fetching_unit")
builder.add_edge("task_fetching_unit", "joiner")

builder.add_conditional_edges(
    "joiner",
    should_continue,
)

checkpointer = InMemorySaver()
graph = builder.compile(name="LLMCompiler", checkpointer=checkpointer)
