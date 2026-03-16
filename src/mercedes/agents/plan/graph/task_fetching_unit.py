"""任务调度单元节点：按依赖关系波次并行执行任务 DAG。"""

import asyncio
import re
from typing import Any, Dict

from langgraph.runtime import Runtime

from mercedes.agents.plan.context import Context
from mercedes.agents.plan.state import PlanExecuteState, Task
from mercedes.tools import tools

tool_map = {t.name: t for t in tools}

VAR_PATTERN = re.compile(r"\$\{(\d+)\}|\$(\d+)")


def substitute_value(value: Any, results: dict[int, str]) -> Any:
    """递归地将值中的 $idx 或 ${idx} 变量替换为对应任务的执行结果。"""
    if isinstance(value, str):
        matches = list(VAR_PATTERN.finditer(value))
        if not matches:
            return value

        new_value = value
        for match in reversed(matches):
            idx_str = match.group(1) or match.group(2)
            idx = int(idx_str)
            if idx in results:
                replacement = str(results[idx])
                new_value = new_value[: match.start()] + replacement + new_value[match.end() :]
        return new_value
    elif isinstance(value, dict):
        return {k: substitute_value(v, results) for k, v in value.items()}
    elif isinstance(value, list):
        return [substitute_value(item, results) for item in value]
    else:
        return value


def substitute_vars(args: dict[str, Any], results: dict[int, str]) -> dict[str, Any]:
    """将任务参数中的 $idx 或 ${idx} 变量替换为对应任务的执行结果。"""
    return substitute_value(args, results)


async def _execute_task(task: Task, results: dict[int, str]) -> tuple[int, str]:
    """执行单个任务，支持变量替换。"""
    tool_fn = tool_map.get(task["tool"])
    if tool_fn is None:
        return task["idx"], f"错误：工具 '{task['tool']}' 不存在"

    args = substitute_vars(task["args"], results)
    try:
        result = await tool_fn.ainvoke(args)
        return task["idx"], str(result)
    except Exception as e:
        return task["idx"], f"执行错误：{e}"


async def task_fetching_unit(state: PlanExecuteState, runtime: Runtime[Context]) -> Dict:
    """ASAP 任务调度单元：只要依赖满足即刻并行执行任务。

    算法：
    1. 为每个任务创建一个独立的协程。
    2. 任务协程等待其依赖项（如果有）完成。
    3. 依赖满足后，立即调用工具执行。
    4. 执行完成后通知下游任务，实现最大化并行。
    """
    tasks = state.tasks
    if not tasks:
        return {"results": {}}

    results: dict[int, str] = {}
    events: dict[int, asyncio.Event] = {t["idx"]: asyncio.Event() for t in tasks}
    completed: set[int] = set()
    lock = asyncio.Lock()

    async def run_task(task: Task):
        idx = task["idx"]
        deps = task.get("dependencies", [])

        if deps:
            valid_deps = [d for d in deps if d in events]
            if valid_deps:
                await asyncio.gather(*[events[d].wait() for d in valid_deps])

        res_idx, res_val = await _execute_task(task, results)

        async with lock:
            results[res_idx] = res_val
            completed.add(res_idx)

        events[idx].set()

    try:
        await asyncio.wait_for(asyncio.gather(*[run_task(t) for t in tasks]), timeout=300)
    except asyncio.TimeoutError:
        for idx, event in events.items():
            if not event.is_set():
                results[idx] = "错误：任务执行超时或存在循环依赖"

    return {"results": results}
