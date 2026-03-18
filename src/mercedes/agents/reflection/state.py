from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated


@dataclass
class InputState:
    """代理的输入状态。"""

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)
    """消息列表，记录对话历史。"""


@dataclass
class ReflectionState(InputState):
    """定义 Reflection Agent 的状态。"""

    generation: str = field(default="")
    """当前生成的文本。"""

    reflection: str = field(default="")
    """针对生成的反思和批评。"""

    satisfied: bool = field(default=False)
    """是否对当前生成的内容感到满意。"""

    needs_more_info: bool = field(default=False)
    """是否需要通过工具收集更多信息。"""

    iterations: int = field(default=0)
    """已经进行的迭代次数。"""


class GenerationOutput(TypedDict):
    """负责生成内容的节点输出。"""

    generation: str


class ReflectionOutput(TypedDict):
    """负责对生成内容进行反思和批评的节点输出。"""

    reflection: str
    satisfied: bool
    needs_more_info: bool
