# AGENTS.md

所有回答、注释、文档使用中文。

## 启动与命令

```bash
# 安装依赖（若 venv 因目录迁移而失效会自动修复）
make install        # ./install.sh
# 开发模式
make dev            # ./dev.sh（默认端口 4000，可用 PORT=xxxx 覆盖）
# 启动应用
make run            # ./start.sh

# 应用子命令（CLI 入口 src/main.py，当前已实现 fetch / show）
make fetch|show|translate|validate|stats|pipeline|clean-news
venv/bin/python -m src.main fetch

# Web 服务器（端口 4000）
./start.sh                       # debug=True
venv/bin/python main.py --port 4000
# 或 venv/bin/python web_server.py

# 注意：脚本直接调用 venv/bin/python，不依赖 source venv/bin/activate
# （项目目录变更后 activate 内的 VIRTUAL_ENV 会失效，且 macOS 无 python 命令）

# 代码检查顺序（make check 包含全部）
make format         # black .
make lint           # ruff check .
make type           # mypy src/
make check          # format → lint-fix → type

# 测试
make test           # pytest -v
make test-cov       # pytest --cov=src --cov-report=html --cov-report=term
pytest tests/path/to/test_file.py -v    # 单文件测试
```

## 项目结构

- `src/fetchers/source/` — 26 个新闻源抓取器，继承 `BaseFetcher`，通过 `src/fetchers/__init__.py` 自动注册
- `src/translators/` — 10 个翻译后端（OpenAI, DeepL, Google, Baidu 等），继承 `BaseTranslator`
- `src/storage/` — SQLite 数据库 + Pydantic 数据模型
- `routes/` — Flask Blueprint（frontend, admin, api）
- `templates/` — Jinja2 模板
- `tests/` — pytest 测试，目录结构镜像 `src/`

## 关键约定

- **入口**: `main.py` 既是 CLI 入口（click），也是 Flask 应用入口（端口 4000）。`pyproject.toml` 注册了 `news` 命令指向 `src.main:main`
- **配置**: pydantic-settings 从 `.env` 加载，配置类在 `src/utils/config.py`
- **Fetcher 模式**: 所有抓取器放在 `source/` 目录，类名以 `Fetcher` 结尾（如 `BaiduFetcher`），`BaseFetcher.run()` 自动处理 async 调度和标准化
- **测试文件**: `tests/` 中既有 `pytest` 测试，也有少数直接运行的脚本（如 `test_baidu_fetcher.py`），后者会被 `pytest` 收集报错但无妨
- **已有指令文件**: `.traerules`（Trae IDE 规则）、`TRAE_SPEC.md`（Trae 项目规范），修改时同步更新

## 注意事项

- 添加新抓取器：在 `source/` 下新建文件，实现 `BaseFetcher`，无需手动注册
- 添加新翻译器：在 `translators/` 下新建文件，实现 `BaseTranslator`
- 添加新依赖：同步更新 `pyproject.toml`、`requirements.txt`、`requirements-dev.txt`
- 测试用 mock 数据，避免网络请求依赖
