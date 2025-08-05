#!/bin/bash
# 一键安装脚本 - 使用UV/UVX

set -e

echo "🚀 安装 Artifacts MCP Server (简化版)"

# 检查是否安装了uv
if ! command -v uv &> /dev/null; then
    echo "📦 安装 UV 包管理器..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

# 使用uvx安装和运行
echo "📦 使用UV安装依赖..."
uv sync

# 创建配置文件
echo "⚙️  创建配置文件..."
cat > config.json << 'EOF'
{
  "agentsphere_api_key": "",
  "auto_open_browser": true,
  "raycast_config_path": "~/.config/raycast/ai/mcp_servers.json"
}
EOF

# 提示用户设置API key
echo ""
echo "📋 下一步："
echo "1. 访问 https://www.agentsphere.run/apikey 获取API key"
echo "2. 设置API key:"
echo "   export AGENTSPHERE_API_KEY=your_api_key"
echo "   或编辑 config.json 文件"
echo ""
echo "3. 配置Raycast:"
echo "   uv run artifacts-mcp --setup-raycast"
echo ""
echo "4. 启动服务器:"
echo "   uv run artifacts-mcp"

echo ""
echo "✅ 安装完成！"