"""规划器节点：生成带依赖关系的任务 DAG。"""

from typing import Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from mercedes.agents.plan.context import Context
from mercedes.agents.plan.state import LLMCompilerPlan, PlanExecuteState
from mercedes.core.llm import get_llm
from mercedes.tools import tools
from mercedes.utils.aimessage import build_past_steps_section, get_latest_human_message

tool_descriptions = "\n".join(f"- {t.name}: {t.description}" for t in tools)


async def planner(state: PlanExecuteState, runtime: Runtime[Context]) -> Dict:
    """规划器：生成带依赖关系的任务 DAG。

    独立任务将在 Task Fetching Unit 中并行执行；
    依赖其他任务结果的任务将在依赖完成后再调度。
    """
    llm = get_llm(runtime.context.model).with_structured_output(LLMCompilerPlan)

    objective = get_latest_human_message(state.messages)

    system_prompt = runtime.context.planner_prompt.format(
        tool_descriptions=tool_descriptions,
        past_steps_section=build_past_steps_section(state.past_steps),
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
