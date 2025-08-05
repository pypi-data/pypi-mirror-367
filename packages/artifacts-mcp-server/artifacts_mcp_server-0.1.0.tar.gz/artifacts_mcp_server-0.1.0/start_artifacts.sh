#!/bin/bash
# Artifacts MCP Server启动脚本
# 自动处理Python路径问题

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 尝试不同的Python命令
if command -v python3 &> /dev/null; then
    exec python3 artifacts_fastmcp.py
elif command -v python &> /dev/null; then
    exec python artifacts_fastmcp.py
elif [ -x "/opt/homebrew/bin/python3" ]; then
    exec /opt/homebrew/bin/python3 artifacts_fastmcp.py
elif [ -x "/usr/local/bin/python3" ]; then
    exec /usr/local/bin/python3 artifacts_fastmcp.py
else
    echo "Error: Python not found!"
    exit 1
fi