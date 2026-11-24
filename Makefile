# Makefile - 提供便捷的命令快捷方式

# 统一使用项目内虚拟环境的解释器（macOS 无 python 命令，且避免激活失效的 activate）
PY := venv/bin/python

.PHONY: help install test clean run dev format lint type check deploy

# 默认目标
.DEFAULT_GOAL := help

help:  ## 显示帮助信息
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "🌍 全球新闻聚合工具 - Makefile 命令"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install:  ## 安装项目依赖
	./install.sh

run:  ## 启动应用
	./start.sh

test:  ## 运行测试
	$(PY) -m pytest -v

test-cov:  ## 运行测试并生成覆盖率报告
	$(PY) -m pytest --cov=src --cov-report=html --cov-report=term
	@echo ""
	@echo "✓ HTML 报告: htmlcov/index.html"

format:  ## 格式化代码
	$(PY) -m black .
	@echo "✓ 代码已格式化"

lint:  ## 运行 lint 检查
	$(PY) -m ruff check .

lint-fix:  ## 运行 lint 并自动修复
	$(PY) -m ruff check --fix .

type:  ## 类型检查
	$(PY) -m mypy src/

check: format lint-fix type  ## 运行所有代码检查

clean:  ## 清理缓存和临时文件
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage dist/ build/ 2>/dev/null || true
	@echo "✓ 缓存已清理"

dev:  ## 开发模式
	./dev.sh

deploy:  ## 部署提示（无 deploy.sh 时给出说明）
	@echo "警告: 未找到 deploy.sh，请使用 ./start.sh 启动，或自行配置部署流程。"

# 应用命令快捷方式（CLI 入口为 src/main.py）
fetch:  ## 抓取新闻
	$(PY) -m src.main fetch

translate:  ## 翻译新闻
	$(PY) -m src.main translate

validate:  ## 验证新闻
	$(PY) -m src.main validate

show:  ## 显示新闻列表
	$(PY) -m src.main show

stats:  ## 显示统计信息
	$(PY) -m src.main stats

pipeline:  ## 运行完整流程
	$(PY) -m src.main pipeline

clean-news:  ## 清理旧新闻
	$(PY) -m src.main clean
