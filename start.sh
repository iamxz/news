#!/usr/bin/env bash
# 启动新闻 Web 应用（日常运行）
set -euo pipefail

cd "$(dirname "$0")"

# 说明：项目目录可能被移动过，venv/bin/activate 中硬编码的 VIRTUAL_ENV 会失效，
# 因此这里不使用 source activate，而是直接定位可用的解释器
# （直接运行 venv 内的解释器即可获得虚拟环境上下文）。
PYTHON_BIN=""
for candidate in venv/bin/python3 venv/bin/python .venv/bin/python3 .venv/bin/python; do
    if [ -x "$candidate" ] && "$candidate" -c "import flask" >/dev/null 2>&1; then
        PYTHON_BIN="$candidate"
        break
    fi
done

# 兜底：系统 python3 且已安装依赖
if [ -z "$PYTHON_BIN" ]; then
    for candidate in python3 python; do
        if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c "import flask" >/dev/null 2>&1; then
            PYTHON_BIN="$candidate"
            break
        fi
    done
fi

if [ -z "$PYTHON_BIN" ]; then
    echo "错误: 未找到可用的 Python 环境（缺少 flask 依赖）。" >&2
    echo "请先运行 ./install.sh 安装依赖（会自动修复失效的 venv）。" >&2
    exit 1
fi

echo "使用 Python: $PYTHON_BIN"
exec "$PYTHON_BIN" main.py "$@"
