# 开发指南

## 构建与配置
- **依赖**: 该项目使用 [uv](https://github.com/astral-sh/uv) 进行依赖管理。要设置环境，请运行:
  ```bash
  uv sync
  ```
- **配置**: 项目需要为 LLM 服务（如 Ollama）进行配置。请在 `src/mercedes/conf.py` 中或通过 `.env` 文件配置 `BASE_URL`。
- **运行**: 可以通过以下入口点启动服务:
  ```bash
  python src/main.py
  ```

## 测试
- **结构**: 测试脚本位于 `tests/` 目录中。
- **执行**: 当前测试是独立的 Python 脚本。你可以直接运行它们:
  ```bash
  python tests/test_api.py
  ```
- **添加测试**: 你可以按照现有可执行 Python 脚本的模式在 `tests/` 中创建新的测试文件。或者，如果需要更健壮的测试运行器，可以安装 `pytest`，尽管当前工作流依赖于直接执行。

## 开发标准
- **格式化**: 项目使用 `black` 进行代码格式化。
- **导入**: `isort` 被配置为维护导入顺序。
- **配置**: 样式配置在 `pyproject.toml` 中管理。
