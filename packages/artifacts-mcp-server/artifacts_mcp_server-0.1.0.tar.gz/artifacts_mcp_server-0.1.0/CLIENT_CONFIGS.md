# MCP客户端配置指南

Artifacts MCP Server支持所有主流的MCP客户端。选择你使用的客户端进行配置：

## 📱 支持的客户端

### 🟢 完全支持
- **Claude Desktop** - Anthropic官方桌面应用
- **Raycast AI** - macOS启动器（需要Pro）
- **Cursor** - AI代码编辑器
- **Zed Editor** - 高性能代码编辑器
- **VS Code + Cline** - 使用Cline扮演

### 🟡 部分支持/即将支持
- **Continue.dev** - VS Code AI扩展
- **GitHub Copilot** - 代理模式
- **Claude.ai** - Web版（远程MCP）
- **JetBrains IDEs** - 即将在下个版本支持

---

## 🖥️ Claude Desktop

**适合**：桌面用户，需要本地文件集成

### 配置步骤

1. 下载并安装 [Claude Desktop](https://claude.ai/download)

2. 找到配置文件位置：
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
         "args": ["/完整路径/artifacts_fastmcp_fixed.py"],
         "env": {
           "AGENTSPHERE_API_KEY": "你的API_KEY"
         }
       }
     }
   }
   ```

4. 重启Claude Desktop

---

## 🚀 Raycast AI

**适合**：macOS用户，快速启动

### 配置步骤

1. 确保有Raycast Pro订阅

2. 编辑配置文件：
   ```bash
   nano ~/.config/raycast/ai/mcp_servers.json
   ```

3. 添加配置：
   ```json
   {
     "mcpServers": {
       "artifacts": {
         "command": "python3",
         "args": ["/Users/你的用户名/mcp-tools/artifacts_fastmcp_fixed.py"]
       }
     }
   }
   ```

4. 重启Raycast

---

## 💻 Cursor

**适合**：代码开发，AI编程助手

### 配置步骤

1. 安装 [Cursor](https://cursor.sh/)

2. 打开Cursor设置 (Cmd/Ctrl + ,)

3. 找到 "MCP Servers" 或 "AI Assistant" 部分

4. 添加服务器配置：
   ```json
   {
     "name": "artifacts",
     "command": "python3",
     "args": ["/完整路径/artifacts_fastmcp_fixed.py"],
     "env": {
       "AGENTSPHERE_API_KEY": "你的API_KEY"
     }
   }
   ```

或者手动编辑配置文件：
```bash
# macOS/Linux
~/.cursor/mcp_servers.json

# Windows  
%APPDATA%\Cursor\mcp_servers.json
```

内容：
```json
{
  "mcp": {
    "servers": {
      "artifacts": {
        "command": "python3",
        "args": ["/完整路径/artifacts_fastmcp_fixed.py"],
        "env": {
          "AGENTSPHERE_API_KEY": "你的API_KEY"
        }
      }
    }
  }
}
```

---

## ⚡ Zed Editor

**适合**：高性能代码编辑，现代开发

### 配置步骤

1. 安装 [Zed](https://zed.dev/)

2. 打开设置文件：
   ```bash
   # macOS
   ~/.config/zed/settings.json
   
   # Linux
   ~/.config/zed/settings.json
   
   # Windows
   %APPDATA%\Zed\settings.json
   ```

3. 添加MCP配置：
   ```json
   {
     "experimental": {
       "mcp": {
         "servers": {
           "artifacts": {
             "command": "python3",
             "args": ["/完整路径/artifacts_fastmcp_fixed.py"],
             "env": {
               "AGENTSPHERE_API_KEY": "你的API_KEY"
             }
           }
         }
       }
     }
   }
   ```

4. 重启Zed

---

## 📝 VS Code + Cline

**适合**：VS Code用户，自动化编程

### 配置步骤

1. 安装VS Code和Cline扩展

2. 在VS Code中，打开命令面板 (Cmd/Ctrl + Shift + P)

3. 搜索 "Cline: Configure MCP Servers"

4. 添加服务器：
   ```json
   {
     "artifacts": {
       "command": "python3",
       "args": ["/完整路径/artifacts_fastmcp_fixed.py"],
       "env": {
         "AGENTSPHERE_API_KEY": "你的API_KEY"
       }
     }
   }
   ```

或手动编辑 `.vscode/mcp_servers.json`：
```json
{
  "mcpServers": {
    "artifacts": {
      "command": "python3",
      "args": ["/完整路径/artifacts_fastmcp_fixed.py"],
      "env": {
        "AGENTSPHERE_API_KEY": "你的API_KEY"
      }
    }
  }
}
```

---

## 🌐 Continue.dev

**适合**：VS Code AI编程助手

### 配置步骤

1. 安装Continue扩展

2. 打开Continue配置：
   ```bash
   ~/.continue/config.json
   ```

3. 添加MCP服务器：
   ```json
   {
     "mcpServers": [
       {
         "name": "artifacts",
         "serverPath": "/完整路径/artifacts_fastmcp_fixed.py",
         "args": [],
         "env": {
           "AGENTSPHERE_API_KEY": "你的API_KEY"
         }
       }
     ]
   }
   ```

---

## 🔧 通用配置要点

### 1. API Key配置方式

**方式1：在客户端配置中**
```json
"env": {
  "AGENTSPHERE_API_KEY": "as_your_actual_key"
}
```

**方式2：使用config.json文件**
```json
// ~/mcp-tools/config.json
{
  "agentsphere_api_key": "as_your_actual_key"
}
```

**方式3：系统环境变量**
```bash
export AGENTSPHERE_API_KEY="as_your_actual_key"
```

### 2. Python命令选择

不同系统可能需要不同的Python命令：
- `python3` - 大多数macOS/Linux
- `python` - 某些Windows或Python别名
- `/usr/bin/python3` - 完整路径
- `/opt/homebrew/bin/python3` - Homebrew Python

查看你的Python路径：
```bash
which python3
```

### 3. 路径问题

**重要**：所有路径必须是**绝对路径**，不能使用：
- `~/` 
- `./`
- 相对路径

正确示例：
```
/Users/jack/mcp-tools/artifacts_fastmcp_fixed.py
/home/user/mcp-tools/artifacts_fastmcp_fixed.py
C:\Users\Jack\mcp-tools\artifacts_fastmcp_fixed.py
```

---

## 🧪 测试配置

在任何客户端中，都可以用这些命令测试：

1. **基础测试**
   ```
   列出所有可用的工具
   ```

2. **功能测试**
   ```
   用artifacts创建一个python脚本打印hello world
   ```

3. **Web预览测试**
   ```
   用artifacts创建一个HTML计算器页面
   ```

如果看到artifacts工具列表，说明配置成功！

---

## ❓ 故障排除

### 通用问题

1. **找不到python命令**
   - 检查：`which python3`
   - 使用完整路径

2. **找不到文件**
   - 确保使用绝对路径
   - 检查文件权限：`ls -la /path/to/file`

3. **API Key错误**
   - 确保key以`as_`开头
   - 检查config.json格式

4. **权限问题**
   - 给Python文件执行权限：`chmod +x *.py`

### 客户端特定问题

**Claude Desktop**：清除缓存重启
**Raycast**：完全退出后重启
**Cursor**：重启应用或重新加载窗口
**Zed**：检查experimental功能是否开启

---

选择适合你的客户端，按照对应步骤配置即可开始使用！