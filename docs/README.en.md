# NHM Agent Platform

[Simplified Chinese](/docs/README.zh.md)\|[English](/docs/README.en.md)\|[Japanese](/docs/README.ja.md)\|[Traditional Chinese](/docs/README.zh-TW.md)

This is an Agent platform infrastructure built from scratch, based on FastAPI and LangGraph.

## Core features

-   **Multi-Agent management**: pass`AgentRegistry`Unified management of different Agents.
-   **ReAct mode**: Agent that supports Reasoning and Action (ReAct) mode (`agent_id="react"`)。
-   **Plan-and-Execute pattern**: Agent that supports Plan-and-Execute mode (`agent_id="plan"`)。
-   **Tool extensions**: A simple decorator pattern definition tool that can be called by Agent.
-   **API access**: Complete RESTful API interface.

## Project structure

```text
src/
├── mercedes/
│   ├── api/          # FastAPI 路由与接口
│   ├── agents/       # 具体 Agent 实现 (包含 react 和 plan 模式)
│   ├── core/         # 核心抽象 (BaseAgent, Registry, LLM 配置)
│   ├── tools/        # 外部工具定义 (天气、时间等)
│   └── utils/        # 通用工具函数与配置
└── main.py           # 服务启动入口
```

## quick start

### 1. Install dependencies

Make sure it is installed`uv`, then run:

```bash
uv sync
```

### 2. Configure the environment

Revise`src/mercedes/conf.py`or via`.env`File configuration for Ollama`BASE_URL`。

### 3. Start the service

```bash
python src/main.py
```

### 4. Call interface

you can use`src/mercedes/tests/test_api.py`To test, or use curl directly:

```bash
# 默认使用 react 模式
curl -X POST http://127.0.0.1:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "现在几点了？"}'

# 使用 plan 模式
curl -X POST http://127.0.0.1:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "现在几点了？", "agent_id": "plan"}'
```
