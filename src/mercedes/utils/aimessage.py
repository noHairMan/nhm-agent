from typing import Sequence

from langchain_core.messages import AnyMessage, HumanMessage


def get_latest_human_message(messages: Sequence[AnyMessage]) -> str:
    """从消息列表中获取最近一条用户消息内容。"""
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return str(message.content)
    return ""


def build_past_steps_section(past_steps: list[tuple[str, str]]) -> str:
    """构建历史步骤的提示词片段。"""
    if not past_steps:
        return ""
    past_lines = "\n".join(f"  - {step}: {result}" for step, result in past_steps)
    return f"已完成的历史步骤（请勿重复执行）：\n{past_lines}"
