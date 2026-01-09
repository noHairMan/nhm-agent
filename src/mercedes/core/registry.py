from typing import Dict, Type

from mercedes.agents.react import ReActAgent
from mercedes.core.agent import BaseAgent


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        # 默认注册一个 ReAct Agent
        self.register("default", ReActAgent(name="DefaultAssistant"))

    def register(self, agent_id: str, agent: BaseAgent):
        self._agents[agent_id] = agent

    def get_agent(self, agent_id: str) -> BaseAgent:
        return self._agents.get(agent_id)


registry = AgentRegistry()
