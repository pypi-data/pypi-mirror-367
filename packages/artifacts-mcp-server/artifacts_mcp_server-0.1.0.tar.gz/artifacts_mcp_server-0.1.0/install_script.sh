#!/bin/bash
# Artifacts MCP Server 一键安装脚本
# 适用于macOS和Linux

set -e

echo "🚀 Artifacts MCP Server 安装脚本"
echo "================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查Python
echo -e "\n${YELLOW}步骤1: 检查Python环境${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    echo -e "${GREEN}✓ 找到 python3${NC}"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    echo -e "${GREEN}✓ 找到 python${NC}"
else
    echo -e "${RED}✗ 未找到Python，请先安装Python 3.9+${NC}"
    echo "  访问 https://www.python.org/downloads/ 下载安装"
    exit 1
fi

# 显示Python版本
$PYTHON_CMD --version

# 创建目录
echo -e "\n${YELLOW}步骤2: 创建安装目录${NC}"
MCP_DIR="$HOME/mcp-tools"
mkdir -p "$MCP_DIR"
echo -e "${GREEN}✓ 创建目录: $MCP_DIR${NC}"

# 检查主程序文件
echo -e "\n${YELLOW}步骤3: 检查程序文件${NC}"
if [ ! -f "artifacts_fastmcp_fixed.py" ]; then
    echo -e "${RED}✗ 未找到 artifacts_fastmcp_fixed.py${NC}"
    echo "  请确保在当前目录下有此文件"
    exit 1
fi

# 复制文件
cp artifacts_fastmcp_fixed.py "$MCP_DIR/"
echo -e "${GREEN}✓ 复制程序文件到 $MCP_DIR${NC}"

# 配置API Key
echo -e "\n${YELLOW}步骤4: 配置API Key${NC}"
CONFIG_FILE="$MCP_DIR/config.json"

if [ -f "$CONFIG_FILE" ]; then
    echo -e "${YELLOW}发现已存在的配置文件${NC}"
    read -p "是否要重新配置API Key? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "保留现有配置"
    else
        rm "$CONFIG_FILE"
    fi
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "请获取你的AgentSphere API Key:"
    echo "1. 访问 https://www.agentsphere.run/"
    echo "2. 注册/登录账号"
    echo "3. 访问 https://www.agentsphere.run/apikey"
    echo "4. 点击 CREATE KEY"
    echo ""
    read -p "请输入你的API Key (以as_开头): " API_KEY
    
    if [[ ! $API_KEY =~ ^as_ ]]; then
        echo -e "${YELLOW}警告: API Key通常以'as_'开头${NC}"
    fi
    
    # 创建配置文件
    cat > "$CONFIG_FILE" << EOF
{
  "agentsphere_api_key": "$API_KEY"
}
EOF
    echo -e "${GREEN}✓ 配置文件已创建${NC}"
fi

# 测试运行
echo -e "\n${YELLOW}步骤5: 测试安装${NC}"
cd "$MCP_DIR"
if $PYTHON_CMD artifacts_fastmcp_fixed.py --help > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 程序测试成功${NC}"
else
    echo -e "${RED}✗ 程序测试失败${NC}"
    echo "尝试手动运行查看错误:"
    echo "  cd $MCP_DIR"
    echo "  $PYTHON_CMD artifacts_fastmcp_fixed.py --help"
fi

# 配置Raycast
echo -e "\n${YELLOW}步骤6: 配置Raycast${NC}"
RAYCAST_DIR="$HOME/.config/raycast/ai"
RAYCAST_CONFIG="$RAYCAST_DIR/mcp_servers.json"

mkdir -p "$RAYCAST_DIR"

# 获取完整路径
FULL_PATH="$MCP_DIR/artifacts_fastmcp_fixed.py"

# 生成Raycast配置
cat > "$RAYCAST_CONFIG" << EOF
{
  "mcpServers": {
    "artifacts": {
      "command": "$PYTHON_CMD",
      "args": ["$FULL_PATH"]
    }
  }
}
EOF

echo -e "${GREEN}✓ Raycast配置已创建${NC}"
echo "  配置文件: $RAYCAST_CONFIG"

# 完成提示
echo -e "\n${GREEN}🎉 安装完成！${NC}"
echo ""
echo "下一步:"
echo "1. 重启Raycast (Command+Q 然后重新打开)"
echo "2. 在Raycast AI中测试:"
echo "   输入: 用artifacts创建一个python hello world脚本"
echo ""
echo "文件位置:"
echo "  程序: $MCP_DIR/artifacts_fastmcp_fixed.py"
echo "  配置: $MCP_DIR/config.json"
echo "  Raycast: $RAYCAST_CONFIG"
echo ""
echo "遇到问题? 查看 INSTALL_GUIDE.md 获取帮助"