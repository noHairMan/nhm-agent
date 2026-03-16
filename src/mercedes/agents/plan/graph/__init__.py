"""定义基于 LLMCompiler 模式的计划与执行代理图。

LLMCompiler 架构包含三个核心组件：
- Planner（规划器）：生成带依赖关系的任务 DAG，支持并行执行
- Task Fetching Unit（任务调度单元）：按依赖顺序并行调度执行任务
- Joiner（决策器）：根据执行结果决定直接回复用户或重新规划

相比传统顺序执行的 Plan-and-Execute，LLMCompiler 通过并行执行独立任务
显著缩短运行时间（论文报告可达 3.6x 加速）。
"""

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph

from mercedes.agents.plan.context import Context
from mercedes.agents.plan.graph.joiner import joiner, should_continue
from mercedes.agents.plan.graph.planner import planner
from mercedes.agents.plan.graph.task_fetching_unit import task_fetching_unit
from mercedes.agents.plan.state import InputState, PlanExecuteState

builder = StateGraph(PlanExecuteState, input_schema=InputState, context_schema=Context)

builder.add_node("planner", planner)
builder.add_node("task_fetching_unit", task_fetching_unit)
builder.add_node("joiner", joiner)

builder.add_edge("__start__", "planner")
builder.add_edge("planner", "task_fetching_unit")
builder.add_edge("task_fetching_unit", "joiner")

builder.add_conditional_edges(
    "joiner",
    should_continue,
)

checkpointer = InMemorySaver()
graph = builder.compile(name="LLMCompiler", checkpointer=checkpointer)
