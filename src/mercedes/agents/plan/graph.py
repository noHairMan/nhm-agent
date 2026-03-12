"""Define the Plan-and-Execute agent.

This agent uses a two-step process: first, it creates a plan to solve the user's request,
and then it executes each step of the plan, re-evaluating and updating the plan as needed.
"""

from typing import Dict, List, Literal, TypedDict, Union, cast

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent
from langgraph.runtime import Runtime

from mercedes.agents.plan.context import Context
from mercedes.agents.plan.state import (
    InputState,
    Plan,
    PlanExecuteState,
)
from mercedes.core.llm import get_llm
from mercedes.tools.basic import tools


async def planner(state: PlanExecuteState, runtime: Runtime[Context]) -> Dict:
    """Plan the steps to solve the user's request."""
    llm = get_llm(runtime.context.model).with_structured_output(Plan)

    # Get the user's objective from the first human message
    objective = ""
    for message in state.messages:
        if isinstance(message, HumanMessage):
            objective = cast(str, message.content)
            break

    system_prompt = runtime.context.planner_prompt
    response = await llm.ainvoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=objective),
        ],
    )
    return {"plan": response["steps"]}


async def executor(state: PlanExecuteState, runtime: Runtime[Context]) -> Dict:
    """Execute the next step in the plan."""
    task = state.plan[0]
    llm = get_llm(runtime.context.model)

    # We use a simple ReAct agent to execute each task
    # This can be more complex if needed
    agent_executor = create_react_agent(llm, tools)

    # Prepare task input
    # Include context from past steps
    past_steps_context = "\n".join([f"Step: {s}\nResult: {r}" for s, r in state.past_steps])
    task_input = f"""Current task: {task}

Past steps context:
{past_steps_context}

Please solve the current task."""

    result = await agent_executor.ainvoke({"messages": [HumanMessage(content=task_input)]})

    return {
        "past_steps": [(task, result["messages"][-1].content)],
        "plan": state.plan[1:],
    }


async def replanner(state: PlanExecuteState, runtime: Runtime[Context]) -> Union[Dict, List]:
    """Re-evaluate the plan based on the results of the execution."""
    llm = get_llm(runtime.context.model).with_structured_output(Plan)

    objective = ""
    for message in state.messages:
        if isinstance(message, HumanMessage):
            objective = cast(str, message.content)
            break

    past_steps = "\n".join([f"Step: {s}\nResult: {r}" for s, r in state.past_steps])

    system_prompt = runtime.context.replanner_prompt.format(
        objective=objective,
        plan="\n".join(state.plan),
        past_steps=past_steps,
    )

    # Since we want to allow the LLM to provide a final response or a new plan,
    # and we are using with_structured_output(Plan), we need to handle the case
    # where it might not want to provide a plan but a response.
    # However, create_react_agent might be better for executor.
    # For replanner, we'll try to get Plan. If it's a final answer, we should have a way to detect it.
    # A common pattern is to have a Response model as well.

    # Let's simplify: the replanner prompt says "respond with the final answer instead of a plan".
    # with_structured_output might force a Plan.
    # Let's use a Union type for structured output if possible, or just a more flexible schema.

    class Response(TypedDict):
        """Response to the user."""

        response: str

    class Act(TypedDict):
        """Action to take."""

        action: Union[Plan, Response]

    llm_act = get_llm(runtime.context.model).with_structured_output(Act)

    response = await llm_act.ainvoke(
        [
            SystemMessage(content=system_prompt),
        ],
    )

    action = response["action"]
    if "response" in action:
        return {"response": action["response"]}
    else:
        return {"plan": action["steps"]}


def should_continue(state: PlanExecuteState) -> Literal["executor", "__end__"]:
    """Determine whether to continue execution or finish."""
    if state.response:
        return "__end__"
    return "executor"


# Build the graph
builder = StateGraph(PlanExecuteState, input_schema=InputState, context_schema=Context)

builder.add_node("planner", planner)
builder.add_node("executor", executor)
builder.add_node("replanner", replanner)

builder.add_edge("__start__", "planner")
builder.add_edge("planner", "executor")
builder.add_edge("executor", "replanner")

builder.add_conditional_edges(
    "replanner",
    should_continue,
)

checkpointer = InMemorySaver()
graph = builder.compile(name="Plan-and-Execute Agent", checkpointer=checkpointer)
