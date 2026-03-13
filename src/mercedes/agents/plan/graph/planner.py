"""规划器节点：生成带依赖关系的任务 DAG。"""

from typing import Dict, cast

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from mercedes.agents.plan.context import Context
from mercedes.agents.plan.state import LLMCompilerPlan, PlanExecuteState
from mercedes.core.llm import get_llm
from mercedes.tools import tools

# 生成工具描述字符串（供 Planner 提示词使用）
tool_descriptions = "\n".join(f"- {t.name}: {t.description}" for t in tools)


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
        tool_descriptions=tool_descriptions,
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
