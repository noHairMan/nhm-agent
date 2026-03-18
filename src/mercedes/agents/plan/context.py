"""定义代理的可配置参数。"""

import os
from dataclasses import dataclass, field, fields
from typing import Annotated

from mercedes.agents.plan import prompts


@dataclass(kw_only=True)
class Context:
    """代理的上下文。"""

    planner_prompt: str = field(
        default=prompts.PLANNER_PROMPT,
        metadata={
            "description": "用于任务规划的提示词，支持 {tool_descriptions} 和 {past_steps_section} 占位符。",
        },
    )
    joiner_prompt: str = field(
        default=prompts.JOINER_PROMPT,
        metadata={
            "description": "用于 Joiner 决策的提示词。",
        },
    )
    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="qwen3.5:9b",
        metadata={
            "description": "用于代理主要交互的语言模型名称。格式应为：provider/model-name。",
        },
    )
    max_replans: int = field(
        default=3,
        metadata={
            "description": "Joiner 允许重新规划的最大次数，超过后强制根据已有信息回复用户，防止无限循环。",
        },
    )

    def __post_init__(self) -> None:
        """为未作为参数传递的属性获取环境变量。"""
        for f in fields(self):
            if not f.init:
                continue
            if getattr(self, f.name) == f.default:
                setattr(self, f.name, os.environ.get(f.name.upper(), f.default))
