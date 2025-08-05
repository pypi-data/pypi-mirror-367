# Artifacts MCP Server 安装指南

让AI帮你编程并实时预览结果！支持Python、JavaScript、HTML、React等多种语言。

## 📋 前置要求

1. **Python 3.9+** （macOS通常自带python3）
2. **MCP兼容客户端** （选择一个）：
   - **Raycast AI** （需要Pro订阅）
   - **Claude Desktop** （推荐）
   - **Cursor** （代码编辑器）
   - **Zed Editor** （高性能）
   - **VS Code + Cline** 
   - 更多客户端见 CLIENT_CONFIGS.md
3. **AgentSphere API Key** （免费获取）

## 🚀 快速安装（5分钟）

### 第1步：下载文件

创建一个专用文件夹并下载主程序：

```bash
# 创建文件夹
mkdir -p ~/mcp-tools
cd ~/mcp-tools

# 下载主程序（二选一）
# 选项A：使用curl
curl -o artifacts_fastmcp_fixed.py https://raw.githubusercontent.com/yourusername/artifacts-mcp/main/artifacts_fastmcp_fixed.py

# 选项B：手动创建文件
# 创建 artifacts_fastmcp_fixed.py 并粘贴提供的代码
```

### 第2步：获取API Key

1. 访问 [AgentSphere](https://www.agentsphere.run/)
2. 注册账号（免费）
3. 访问 [API Key页面](https://www.agentsphere.run/apikey)
4. 点击 **CREATE KEY** 创建密钥
5. 复制生成的密钥（格式如：`as_1234567890abcdef`）

### 第3步：配置API Key

在同一目录创建配置文件 `config.json`：

```bash
cd ~/mcp-tools
nano config.json
```

粘贴以下内容（替换YOUR_API_KEY）：

```json
{
  "agentsphere_api_key": "YOUR_API_KEY"
}
```

保存文件（Ctrl+O, Enter, Ctrl+X）

### 第4步：配置客户端

选择你使用的客户端进行配置：

#### 🖥️ Claude Desktop （推荐）

1. 下载并安装 [Claude Desktop](https://claude.ai/download)

2. 找到配置文件：
   ```bash
   # macOS
   ~/Library/Application Support/Claude/claude_desktop_config.json
   
   # Windows  
   %APPDATA%\Claude\claude_desktop_config.json
   
   # Linux
   ~/.config/Claude/claude_desktop_config.json
   ```

3. 编辑配置文件：
   ```json
   {
     "mcpServers": {
       "artifacts": {
         "command": "python3",
         "args": ["/Users/YOUR_USERNAME/mcp-tools/artifacts_fastmcp_fixed.py"]
       }
     }
   }
   ```

4. 重启Claude Desktop

#### 🚀 Raycast AI

1. 创建配置目录：
   ```bash
   mkdir -p ~/.config/raycast/ai
   ```

2. 编辑配置：
   ```bash
   nano ~/.config/raycast/ai/mcp_servers.json
   ```

3. 粘贴配置：
   ```json
   {
     "mcpServers": {
       "artifacts": {
         "command": "python3",
         "args": ["/Users/YOUR_USERNAME/mcp-tools/artifacts_fastmcp_fixed.py"]
       }
     }
   }
   ```

4. 重启Raycast

#### 💻 其他客户端

查看 `CLIENT_CONFIGS.md` 获取完整的客户端配置指南，包括：
- Cursor
- Zed Editor  
- VS Code + Cline
- Continue.dev

**重要**：将 `YOUR_USERNAME` 替换为你的实际用户名
   
查看用户名：
```bash
echo $USER
```

### 第5步：验证安装

1. **测试Python文件**：
   ```bash
   cd ~/mcp-tools
   python3 artifacts_fastmcp_fixed.py --help
   ```
   
   应该看到帮助信息

2. **重启客户端**：
   - **Claude Desktop**：完全退出后重启
   - **Raycast**：完全退出（Command+Q）后重启
   - **其他客户端**：按对应重启方式

3. **测试功能**：
   在你的AI客户端中输入：
   ```
   用artifacts创建一个python脚本打印hello world
   ```

## 📝 文件结构

安装完成后，你应该有以下文件：

```
~/mcp-tools/
├── artifacts_fastmcp_fixed.py    # 主程序
└── config.json                   # API配置

客户端配置文件位置：
├── Claude Desktop: ~/Library/Application Support/Claude/claude_desktop_config.json
├── Raycast: ~/.config/raycast/ai/mcp_servers.json  
├── Cursor: ~/.cursor/mcp_servers.json
└── 其他客户端见 CLIENT_CONFIGS.md
```

## 🎮 使用示例

在任何MCP兼容客户端中都可以这样使用：

### Python脚本
```
用artifacts创建一个python脚本生成斐波那契数列
```

### HTML网页
```
用artifacts创建一个HTML计算器页面
```

### React应用
```
用artifacts创建一个React待办事项应用
```

### 数据可视化
```
用artifacts创建一个streamlit数据可视化应用
```

## ❓ 常见问题

### 1. "python3: command not found"

检查Python是否安装：
```bash
which python3
# 或
which python
```

如果都没有，安装Python：
```bash
# macOS (使用Homebrew)
brew install python3

# 或从官网下载
# https://www.python.org/downloads/
```

### 2. "No such file or directory"

检查文件路径是否正确：
```bash
ls -la ~/mcp-tools/artifacts_fastmcp_fixed.py
```

确保客户端配置中的路径完全正确。

### 3. API Key错误

检查config.json：
```bash
cat ~/mcp-tools/config.json
```

确保API key格式正确（通常以`as_`开头）。

### 4. 客户端没有识别到工具

1. 确保已完全重启对应客户端
2. 检查配置文件格式是否正确（JSON格式）
3. 在AI客户端中输入"列出所有可用工具"查看
4. 查看 CLIENT_CONFIGS.md 确认配置格式

### 5. 第一次运行很慢

首次运行会自动安装依赖（fastmcp和agentsphere），需要等待1-2分钟。

## 🔧 高级配置

### 使用环境变量（可选）

如果不想在config.json中保存API key，可以使用环境变量：

```bash
# 在 ~/.zshrc 或 ~/.bash_profile 中添加
export AGENTSPHERE_API_KEY="your_api_key"
```

然后在客户端配置中添加环境变量：
```json
{
  "mcpServers": {
    "artifacts": {
      "command": "python3",
      "args": ["/Users/YOUR_USERNAME/mcp-tools/artifacts_fastmcp_fixed.py"],
      "env": {
        "AGENTSPHERE_API_KEY": "${AGENTSPHERE_API_KEY}"
      }
    }
  }
}
```

### 调试模式

如果遇到问题，可以直接运行查看错误：
```bash
cd ~/mcp-tools
python3 artifacts_fastmcp_fixed.py
```

## 📞 获取帮助

- **AgentSphere文档**: https://docs.agentsphere.run/
- **MCP官方文档**: https://modelcontextprotocol.io/clients
- **客户端配置**: 查看 CLIENT_CONFIGS.md
- **问题反馈**: 联系提供文件的人

---

**提示**：安装过程中遇到任何问题，可以截图错误信息寻求帮助。

祝你使用愉快！🎉