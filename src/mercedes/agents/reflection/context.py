"""定义 Reflection Agent 的可配置参数。"""

import os
from dataclasses import dataclass, field, fields
from typing import Annotated

from mercedes.agents.reflection import prompts


@dataclass(kw_only=True)
class Context:
    """Reflection Agent 的上下文。"""

    generator_prompt: str = field(
        default=prompts.GENERATOR_PROMPT,
        metadata={
            "description": "用于内容生成的提示词。",
        },
    )
    reflector_prompt: str = field(
        default=prompts.REFLECTOR_PROMPT,
        metadata={
            "description": "用于对生成内容进行反思和批评的提示词。",
        },
    )
    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default="qwen3.5:9b",
        metadata={
            "description": "用于代理交互的语言模型名称。格式应为：provider/model-name。",
        },
    )
    max_iterations: int = field(
        default=3,
        metadata={
            "description": "最大迭代次数，超过后强制结束流程。",
        },
    )

    def __post_init__(self) -> None:
        """为未作为参数传递的属性获取环境变量。"""
        for f in fields(self):
            if not f.init:
                continue
            if getattr(self, f.name) == f.default:
                setattr(self, f.name, os.environ.get(f.name.upper(), f.default))
