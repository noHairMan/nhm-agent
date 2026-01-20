from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Agent 状态定义"""

    messages: List[Dict[str, Any]] = Field(default_factory=list)
    next_step: Optional[str] = None


class BaseAgent(ABC):
    """Agent 基类"""

    def __init__(self, name: str = "", model_name: str = ""):
        self.name = name
        self.model_name = model_name

    @abstractmethod
    async def ainvoke(self, input_text: str):
        raise NotImplementedError("Subclass must implement this method")

    @abstractmethod
    async def astream(self, input_text: str):
        raise NotImplementedError("Subclass must implement this method")
