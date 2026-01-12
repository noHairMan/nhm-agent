# NHM Agent Platform

[简体中文](/docs/README.zh.md) | [English](/docs/README.en.md) | [日本語](/docs/README.ja.md) | [繁体中文](/docs/README.zh-TW.md)

这是一个从 0 搭建的 Agent 平台基础架构，基于 FastAPI 和 LangGraph。

## 核心特性
- **多 Agent 管理**: 通过 `AgentRegistry` 统一管理不同的 Agent。
- **ReAct 模式**: 内置支持推理与行动 (ReAct) 模式的 Agent。
- **工具扩展**: 简单的装饰器模式定义工具，可供 Agent 调用。
- **API 访问**: 完善的 RESTful API 接口。

## 项目结构
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

## 快速开始

### 1. 安装依赖
确保已安装 `uv`，然后运行：
```bash
uv sync
```

### 2. 配置环境
修改 `src/mercedes/conf.py` 或通过 `.env` 文件配置 Ollama 的 `BASE_URL`。

### 3. 启动服务
```bash
python src/main.py
```

### 4. 调用接口
你可以使用 `src/mercedes/tests/test_api.py` 进行测试，或者直接使用 curl：
```bash
curl -X POST http://127.0.0.1:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "现在几点了？"}'
```
