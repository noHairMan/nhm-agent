"""Default prompts used by the plan-and-execute agent."""

PLANNER_PROMPT = """For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps."""

RE_PLANNER_PROMPT = """For the given objective, come up with a revised plan. \
The plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. \
The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps.

Your objective was this:
{objective}

Your original plan was this:
{plan}

You have currently done the following steps:
{past_steps}

Update the plan accordingly. If no more steps are needed and you can provide the final answer, please respond with the final answer instead of a plan."""
