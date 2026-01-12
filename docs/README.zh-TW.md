# NHM代理平台

[簡體中文](/docs/README.zh.md)\|[英語](/docs/README.en.md)\|[日本人](/docs/README.ja.md)\|[繁體中文](/docs/README.zh-TW.md)

這是一個從 0 搭建的 Agent 平台基礎架構，基於 FastAPI 和 LangGraph。

## 核心特性

-   **多 Agent 管理**: 通過`AgentRegistry`統一管理不同的 Agent。
-   **ReAct 模式**: 內置支持推理與行動 (ReAct) 模式的 Agent。
-   **工具擴展**: 简单的装饰器模式定义工具，可供 Agent 调用。
-   **API 訪問**: 完善的 RESTful API 接口。

## 項目結構

```text
src/
├── mercedes/
│   ├── api/          # FastAPI 路由与接口
│   ├── agents/       # 具体 Agent 实现 (如 ReActAgent)
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

修改`src/mercedes/conf.py`或通過`.env`文件配置 Ollama 的`BASE_URL`。

### 3. 啟動服務

```bash
python src/main.py
```

### 4. 調用接口

你可以使用`src/mercedes/tests/test_api.py`進行測試，或者直接使用 curl：

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "现在几点了？"}'
```
