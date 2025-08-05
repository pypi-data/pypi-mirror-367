#!/bin/bash
# 本地测试脚本

echo "🧪 测试artifacts-mcp-server本地运行"

# 方法1: 直接用Python运行
echo ""
echo "方法1: 直接Python运行"
echo "python artifacts_mcp_server.py"
echo ""

# 方法2: 使用UV本地安装
echo "方法2: UV本地安装测试"
echo "uv pip install -e ."
echo "uv run artifacts-mcp-server"
echo ""

# 方法3: 模拟uvx运行（从本地）
echo "方法3: 模拟uvx（本地）"
echo "uvx --from . artifacts-mcp-server"
echo ""

# 创建测试用的Raycast配置
echo "📝 创建测试配置文件..."

# 本地Python文件配置
cat > test-raycast-local.json << 'EOF'
{
  "mcpServers": {
    "artifacts-local": {
      "command": "python",
      "args": ["$PWD/artifacts_mcp_server.py"],
      "env": {
        "AGENTSPHERE_API_KEY": "test_api_key"
      }
    }
  }
}
EOF

# UV本地运行配置
cat > test-raycast-uv.json << 'EOF'
{
  "mcpServers": {
    "artifacts-uv": {
      "command": "uv",
      "args": ["run", "python", "$PWD/artifacts_mcp_server.py"],
      "env": {
        "AGENTSPHERE_API_KEY": "test_api_key"
      }
    }
  }
}
EOF

# 模拟PyPI安装后的配置（这是最终用户使用的）
cat > test-raycast-pypi.json << 'EOF'
{
  "mcpServers": {
    "artifacts": {
      "command": "uvx",
      "args": ["artifacts-mcp-server"],
      "env": {
        "AGENTSPHERE_API_KEY": "your_api_key_here"
      }
    }
  }
}
EOF

echo ""
echo "✅ 测试配置文件已创建:"
echo "  - test-raycast-local.json (本地Python文件)"
echo "  - test-raycast-uv.json (UV本地运行)"
echo "  - test-raycast-pypi.json (最终用户配置)"
echo ""
echo "🚀 开始测试:"
echo "1. 设置API key: export AGENTSPHERE_API_KEY=your_key"
echo "2. 运行服务器: python artifacts_mcp_server.py"
echo "3. 或使用UV: uvx --from . artifacts-mcp-server"