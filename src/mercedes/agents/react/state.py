"""定义代理的状态结构。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep
from typing_extensions import Annotated


@dataclass
class InputState:
    """定义代理的输入状态，代表与外界较窄的接口。

    该类用于定义初始状态和传入数据的结构。
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)
    """
    跟踪代理主要执行状态的消息。

    通常积累如下模式：
    1. HumanMessage - 用户输入
    2. 带有 .tool_calls 的 AIMessage - 代理选择要使用的工具来收集信息
    3. ToolMessage(s) - 执行工具后的响应（或错误）
    4. 不带 .tool_calls 的 AIMessage - 代理以非结构化格式回复用户
    5. HumanMessage - 用户进行下一轮对话回复

    步骤 2-5 可根据需要重复。

    `add_messages` 注解确保新消息与现有消息合并，通过 ID 更新以维持“仅追加”状态，除非提供了具有相同 ID 的消息。
    """


@dataclass
class State(InputState):
    """表示代理的完整状态，扩展了 InputState 并增加了额外的属性。

    该类可用于存储代理生命周期中需要的任何信息。
    """

    is_last_step: IsLastStep = field(default=False)
    """
    指示当前步骤是否是图抛出错误前的最后一步。

    这是一个“受管”变量，由状态机而非用户代码控制。
    当步骤数达到 recursion_limit - 1 时，它被设置为 'True'。
    """

    # 可根据需要在此处添加额外属性。
    # 常见示例包括：
    # retrieved_documents: List[Document] = field(default_factory=list)
    # extracted_entities: Dict[str, Any] = field(default_factory=dict)
    # api_connections: Dict[str, Any] = field(default_factory=dict)
