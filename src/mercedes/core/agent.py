from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentState(BaseModel):
    """Agent 状态定义"""

    messages: List[Dict[str, Any]] = Field(default_factory=list)
    next_step: Optional[str] = None


class BaseAgent:
    """Agent 基类"""

    def __init__(self, name: str, model_name: str):
        self.name = name
        self.model_name = model_name

    async def run(self, input_text: str) -> str:
        raise NotImplementedError("Subclasses must implement run method")
