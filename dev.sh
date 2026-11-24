#!/usr/bin/env bash
# 开发模式启动（默认端口 4000，debug 热重载）
set -euo pipefail

cd "$(dirname "$0")"

# 同 start.sh：不依赖可能已失效的 venv/bin/activate，直接定位解释器
PYTHON_BIN=""
for candidate in venv/bin/python3 venv/bin/python .venv/bin/python3 .venv/bin/python; do
    if [ -x "$candidate" ] && "$candidate" -c "import flask" >/dev/null 2>&1; then
        PYTHON_BIN="$candidate"
        break
    fi
done

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

if [ "$#" -gt 0 ]; then
    exec "$PYTHON_BIN" main.py "$@"
else
    exec "$PYTHON_BIN" main.py --port "${PORT:-4000}"
fi
