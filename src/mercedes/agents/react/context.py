"""定义代理的可配置参数。"""

import os
from dataclasses import dataclass, field, fields
from typing import Annotated

from mercedes.agents.react import prompts


@dataclass(kw_only=True)
class Context:
    """代理的上下文。"""

    system_prompt: str = field(
        default=prompts.SYSTEM_PROMPT,
        metadata={
            "description": "用于代理交互的系统提示词。此提示词为代理设定背景和行为。",
        },
    )

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="qwen3.5:9b",
        metadata={
            "description": "用于代理主要交互的语言模型名称。格式应为：provider/model-name。",
        },
    )

    max_search_results: int = field(
        default=10,
        metadata={"description": "每个搜索查询返回的最大搜索结果数。"},
    )

    def __post_init__(self) -> None:
        """为未作为参数传递的属性获取环境变量。"""
        for f in fields(self):
            if not f.init:
                continue

            if getattr(self, f.name) == f.default:
                setattr(self, f.name, os.environ.get(f.name.upper(), f.default))
