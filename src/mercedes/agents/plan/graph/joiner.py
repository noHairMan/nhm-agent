"""决策器节点：根据任务执行结果决定直接回复用户或重新规划。"""

from typing import Dict, Literal

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.runtime import Runtime

from mercedes.agents.plan.context import Context
from mercedes.agents.plan.state import JoinerAction, JoinerDecision, PlanExecuteState
from mercedes.core.llm import get_llm
from mercedes.utils.aimessage import build_past_steps_section, get_latest_human_message


async def joiner(state: PlanExecuteState, runtime: Runtime[Context]) -> Dict:
    """决策器：根据任务执行结果决定直接回复用户或重新规划。"""
    llm = get_llm(runtime.context.model).with_structured_output(JoinerDecision)

    objective = get_latest_human_message(state.messages)

    tasks_summary = "\n".join(
        f"  任务 {t['idx']} [{t['tool']}({t['args']}), 依赖: {t['dependencies']}]"
        f"\n    结果: {state.results.get(t['idx'], '未执行')}"
        for t in state.tasks
    )

    past_steps_context = build_past_steps_section(state.past_steps)
    if past_steps_context:
        past_steps_context = past_steps_context.replace("已完成的历史步骤（请勿重复执行）：", "历史执行步骤：") + "\n\n"

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

    max_replans = runtime.context.max_replans

    if response.get("action") == JoinerAction.RESPOND and response.get("response"):
        return {
            "response": response["response"],
            "thought": response.get("thought", ""),
            "replan_count": 0,
        }

    if state.replan_count >= max_replans:
        all_results = "\n".join(f"{step}: {result}" for step, result in state.past_steps)
        forced_response = (
            response.get("response")
            or f"根据已收集到的信息：\n{all_results}\n\n如需更准确的结果，请尝试换一种方式提问。"
        )
        return {
            "response": forced_response,
            "thought": response.get("thought", ""),
            "replan_count": 0,
        }

    new_past_steps = [(f"{t['tool']}({t['args']})", state.results.get(t["idx"], "未执行")) for t in state.tasks]
    return {
        "tasks": [],
        "results": {},
        "past_steps": new_past_steps,
        "thought": response.get("thought", ""),
        "replan_count": state.replan_count + 1,
    }


def should_continue(state: PlanExecuteState) -> Literal["planner", "__end__"]:
    """根据 Joiner 的决策结果决定流程走向。"""
    if state.response:
        return "__end__"
    return "planner"
