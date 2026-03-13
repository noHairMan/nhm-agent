"""任务调度单元节点：按依赖关系波次并行执行任务 DAG。"""

import asyncio
from typing import Any, Dict

from langgraph.runtime import Runtime

from mercedes.agents.plan.context import Context
from mercedes.agents.plan.state import PlanExecuteState, Task
from mercedes.tools import tools

# 构建工具名称到工具实例的映射
tool_map = {t.name: t for t in tools}


def substitute_vars(args: dict[str, Any], results: dict[int, str]) -> dict[str, Any]:
    """将任务参数中的 $<idx> 变量替换为对应任务的执行结果。"""
    substituted = {}
    for key, value in args.items():
        if isinstance(value, str) and value.startswith("$"):
            try:
                dep_idx = int(value[1:])
                substituted[key] = results.get(dep_idx, value)
            except ValueError:
                substituted[key] = value
        else:
            substituted[key] = value
    return substituted


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
    """任务调度单元：按依赖关系波次并行执行任务 DAG。

    算法：
    1. 找出所有依赖已满足的就绪任务
    2. 并行执行该批次所有就绪任务
    3. 将结果合并，重复直至所有任务完成
    """
    pending: dict[int, Task] = {t["idx"]: t for t in state.tasks}
    completed: set[int] = set()
    results: dict[int, str] = {}

    while pending:
        # 找出当前批次所有依赖已满足的就绪任务
        ready = [t for idx, t in pending.items() if all(dep in completed for dep in t["dependencies"])]

        if not ready:
            # 存在循环依赖或无法推进，退出避免死循环
            break

        # 并行执行本批次所有就绪任务
        batch_results = await asyncio.gather(*[_execute_task(t, results) for t in ready])

        for idx, result in batch_results:
            results[idx] = result
            completed.add(idx)
            pending.pop(idx, None)

    return {"results": results}
