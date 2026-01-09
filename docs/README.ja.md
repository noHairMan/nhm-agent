# NHM エージェント プラットフォーム

これは、FastAPI と LangGraph に基づいて最初から構築されたエージェント プラットフォーム インフラストラクチャです。

## 核心特性

-   **多 Agent 管理**： 合格`AgentRegistry`異なるエージェントを一元管理します。
-   **反応モード**: Reasoning and Action (ReAct) モードをサポートする組み込みエージェント。
-   **ツール拡張機能**: エージェントから呼び出せるシンプルなデコレータパターン定義ツール。
-   **APIアクセス**: 完全な RESTful API インターフェイス。

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

## クイックスタート

### 1. 依存関係をインストールする

インストールされていることを確認してください`uv`、次に実行します:

```bash
uv sync
```

### 2. 環境を構成する

改訂`src/mercedes/conf.py`または経由`.env`Ollama のファイル構成`BASE_URL`。

### 3. サービスを開始する

```bash
python src/main.py
```

### 4.通話インターフェース

使用できます`src/mercedes/tests/test_api.py`テストするか、curl を直接使用するには:

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "现在几点了？"}'
```
