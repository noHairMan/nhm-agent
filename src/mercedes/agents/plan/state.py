"""定义 LLMCompiler 代理的状态结构。"""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated, TypedDict


class Task(TypedDict):
    """DAG 中的单个可执行任务。"""

    idx: int
    """任务索引（从 1 开始）。"""
    tool: str
    """要调用的工具名称。"""
    args: dict[str, Any]
    """工具参数，可使用 $<idx> 语法引用其他任务的结果。"""
    dependencies: list[int]
    """此任务所依赖的任务索引列表。"""


class LLMCompilerPlan(TypedDict):
    """规划器输出的任务 DAG。"""

    thought: str
    """规划器的推理过程。"""
    tasks: list[Task]
    """任务列表，包含工具调用及依赖关系。"""


class JoinerDecision(TypedDict):
    """Joiner 的决策结果。"""

    thought: str
    """推理过程。"""
    action: str
    """'respond' 表示已完成目标；'replan' 表示需要重新规划。"""
    response: str | None
    """最终回复内容（action='respond' 时填写）。"""


@dataclass
class InputState:
    """代理的输入状态。"""

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)


@dataclass
class PlanExecuteState(InputState):
    """LLMCompiler 代理的完整状态。"""

    tasks: list[Task] = field(default_factory=list)
    """当前执行轮次的任务 DAG。"""

    results: dict[int, str] = field(default_factory=dict)
    """当前轮次各任务的执行结果，key 为任务索引。"""

    past_steps: Annotated[list[tuple[str, str]], operator.add] = field(default_factory=list)
    """历史执行记录列表，格式为 (任务描述, 结果)。"""

    response: str = field(default="")
    """给用户的最终回复。"""

    thought: str = field(default="")
    """最近一次规划或决策的推理过程。"""
