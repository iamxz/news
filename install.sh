#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

PYTHON_CMD="${PYTHON_CMD:-python3}"
VENV_DIR="venv"
VENV_PATH="$(pwd)/$VENV_DIR"

# 若 venv 是在其它路径下创建的（项目被移动/复制过），
# activate 中的 VIRTUAL_ENV 以及 bin/ 下所有脚本的 shebang 都会失效，这里自动修复。
if [ -d "$VENV_DIR/bin" ]; then
    OLD_PATH="$(sed -n 's/^VIRTUAL_ENV=//p' "$VENV_DIR/bin/activate" 2>/dev/null | head -1)"
    if [ -n "$OLD_PATH" ] && [ "$OLD_PATH" != "$VENV_PATH" ]; then
        echo "检测到虚拟环境创建于 $OLD_PATH，与当前路径不一致，正在修复 ..."
        if [ -d "$OLD_PATH" ]; then
            echo "注意: 旧路径仍然存在，建议改用独立的虚拟环境以免混淆。"
        fi
        # 修正 activate 及 bin/ 下脚本 shebang 中的旧路径
        grep -rlF "$OLD_PATH" "$VENV_DIR/bin" 2>/dev/null | while IFS= read -r f; do
            [ -f "$f" ] || continue
            sed -i.bak "s|$OLD_PATH|$VENV_PATH|g" "$f" && rm -f "$f.bak"
        done
        echo "✓ 虚拟环境路径已修复"
    fi
    if ! "$VENV_DIR/bin/python" -c "import sys" >/dev/null 2>&1; then
        echo "虚拟环境解释器不可用，正在重建 ..."
        rm -rf "$VENV_DIR"
    fi
fi

[ -d "$VENV_DIR" ] || "$PYTHON_CMD" -m venv "$VENV_DIR"

"$VENV_DIR/bin/python" -m pip install -r requirements.txt
"$VENV_DIR/bin/python" -m pip install -r requirements-dev.txt
echo "安装完成。运行 'make run' 启动应用，或 'source venv/bin/activate' 激活虚拟环境。"
