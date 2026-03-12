# NHM代理平台

[簡體中文](/docs/README.zh.md)\|[英語](/docs/README.en.md)\|[日本人](/docs/README.ja.md)\|[繁體中文](/docs/README.zh-TW.md)

這是一個從 0 建立的 Agent 平台基礎架構，基於 FastAPI 和 LangGraph。

## 核心特性

-   **多 Agent 管理**: 透過`AgentRegistry`統一管理不同的 Agent。
-   **ReAct 模式**: 支持推理與行動 (ReAct) 模式的 Agent (`agent_id="react"`)。
-   **Plan-and-Execute 模式**: 支援先規劃後執行 (Plan-and-Execute) 模式的 Agent (`agent_id="plan"`)。
-   **工具擴充**: 簡單的裝飾器模式定義工具，可供 Agent 呼叫。
-   **API 存取**: 完善的 RESTful API 介面。

## 專案結構

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

## 快速開始

### 1. 安裝依賴

確保已安裝`uv`，然後運行：

```bash
uv sync
```

### 2. 配置環境

修改`src/mercedes/conf.py`或透過`.env`文件配置 Ollama 的`BASE_URL`。

### 3. 啟動服務

```bash
python src/main.py
```

### 4. 呼叫接口

你可以使用`src/mercedes/tests/test_api.py`進行測試，或直接使用 curl：

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
