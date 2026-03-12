"""Define the state structures for the plan-and-execute agent."""

from __future__ import annotations

import operator
from dataclasses import dataclass, field
from typing import List, Sequence, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated


class Plan(TypedDict):
    """A list of steps to execute."""

    steps: list[str]


@dataclass
class InputState:
    """Defines the input state for the agent."""

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(default_factory=list)


@dataclass
class PlanExecuteState(InputState):
    """Represents the complete state of the plan-and-execute agent."""

    plan: list[str] = field(default_factory=list)
    """The list of steps remaining to be executed."""

    past_steps: Annotated[list[tuple[str, str]], operator.add] = field(default_factory=list)
    """The list of steps already executed and their results."""

    response: str = field(default="")
    """The final response to the user."""
