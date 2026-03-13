"""定义计划与执行代理的状态结构。"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import List, Sequence, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated


class Plan(TypedDict):
    """要执行的步骤列表。"""

    steps: list[str]


@dataclass
class InputState:
    """定义代理的输入状态。"""

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)


@dataclass
class PlanExecuteState(InputState):
    """表示计划与执行代理的完整状态。"""

    plan: list[str] = field(default_factory=list)
    """待执行的剩余步骤列表。"""

    past_steps: Annotated[list[tuple[str, str]], operator.add] = field(default_factory=list)
    """已执行的步骤及其结果的列表。"""

    response: str = field(default="")
    """给用户的最终回复。"""
