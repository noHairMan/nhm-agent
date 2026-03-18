from typing import Dict

from mercedes.agents.plan import PlanExecuteAgent
from mercedes.agents.react import ReactAgent
from mercedes.agents.reflection import ReflectionAgent
from mercedes.core.agent import BaseAgent


class AgentRegistry:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self.register("react", ReactAgent(name="DefaultAssistant"))
        self.register("plan", PlanExecuteAgent(name="PlanExecuteAssistant"))
        self.register("reflection", ReflectionAgent(name="ReflectionAssistant"))

    def register(self, agent_id: str, agent: BaseAgent):
        self._agents[agent_id] = agent

    def get_agent(self, agent_id: str) -> BaseAgent:
        return self._agents.get(agent_id)


registry = AgentRegistry()
