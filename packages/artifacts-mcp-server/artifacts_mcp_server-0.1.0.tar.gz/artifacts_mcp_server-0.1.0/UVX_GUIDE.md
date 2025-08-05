# Artifacts MCP Server - UVX版本

## 🚀 终极简化方案：一个JSON搞定！

不需要下载Python文件，不需要配置config.json，只需要一个JSON配置即可使用！

---

## 📋 前置要求

1. **UV包管理器** (如果没有，会自动安装)
2. **AgentSphere API Key** (免费获取)  
3. **支持MCP的AI客户端**

---

## ⚡ 超简单安装（2分钟）

### 第1步：获取API Key

1. 访问 [AgentSphere](https://www.agentsphere.run/)
2. 注册并登录
3. 访问 [API Key页面](https://www.agentsphere.run/apikey)
4. 点击 **CREATE KEY** 创建API密钥
5. 复制生成的密钥（格式如：`as_1234567890abcdef`）

### 第2步：配置客户端

选择你使用的客户端，只需要复制对应的JSON配置：

#### 🖥️ Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
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
```

#### 🚀 Raycast AI

编辑 `~/.config/raycast/ai/mcp_servers.json`：

```json
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
```

#### 💻 Cursor

编辑 `~/.cursor/mcp_servers.json`：

```json
{
  "mcp": {
    "servers": {
      "artifacts": {
        "command": "uvx",
        "args": ["artifacts-mcp-server"],
        "env": {
          "AGENTSPHERE_API_KEY": "your_api_key_here"
        }
      }
    }
  }
}
```

#### ⚡ Zed Editor

编辑 `~/.config/zed/settings.json`：

```json
{
  "experimental": {
    "mcp": {
      "servers": {
        "artifacts": {
          "command": "uvx",
          "args": ["artifacts-mcp-server"],
          "env": {
            "AGENTSPHERE_API_KEY": "your_api_key_here"
          }
        }
      }
    }
  }
}
```

#### 📝 VS Code + Cline

在`.vscode/mcp_servers.json`：

```json
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
```

### 第3步：开始使用

1. **重要**：把 `your_api_key_here` 替换成你的真实API Key
2. 重启你的AI客户端
3. 在AI客户端中测试：
   ```
   用artifacts创建一个python脚本打印hello world
   ```

**完成！** 🎉

---

## 🎮 使用示例

### Python脚本
```
用artifacts创建一个python脚本生成斐波那契数列
```

### HTML网页
```
用artifacts创建一个响应式的个人简历网页
```

### React应用
```
用artifacts创建一个React待办事项应用
```

### 数据可视化
```
用artifacts创建一个streamlit应用展示股票数据图表
```

---

## 🔧 工作原理

1. **uvx** 是UV包管理器的工具运行器
2. **自动下载**：首次运行时自动从PyPI下载最新版本
3. **自动更新**：总是使用最新版本，无需手动更新
4. **零配置**：不需要任何本地文件或配置
5. **环境隔离**：在临时环境中运行，不污染系统

---

## 🆚 对比其他方案

| 方案 | 文件数量 | 配置复杂度 | 更新方式 |
|------|----------|------------|----------|
| **UVX版本** | 0个 | 一个JSON | 自动更新 |
| Python文件版本 | 2个 | 手动配置 | 手动下载 |
| 完整安装版本 | 4个 | 多步骤 | 手动更新 |

---

## ❓ 常见问题

### 1. "uvx: command not found"

安装UV包管理器：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 第一次运行很慢

首次运行需要下载依赖（fastmcp和agentsphere），等待1-2分钟即可。

### 3. API Key错误

确保API Key：
- 以 `as_` 开头
- 完整复制，没有多余空格
- 在JSON中正确格式化

### 4. 如何更新到最新版本

UVX会自动使用最新版本，无需手动更新！

### 5. 如何卸载

UVX在临时环境运行，删除JSON配置即可完全卸载。

---

## 🔍 调试方法

如果遇到问题，可以手动运行查看错误：

```bash
# 检查是否能运行
uvx artifacts-mcp-server --help

# 设置API key并测试
export AGENTSPHERE_API_KEY=your_key
uvx artifacts-mcp-server
```

---

## 📞 获取帮助

- **查看帮助**：`uvx artifacts-mcp-server --help`
- **AgentSphere文档**：https://docs.agentsphere.run/
- **MCP官方文档**：https://modelcontextprotocol.io/
- **问题反馈**：联系提供此指南的人

---

## 🎉 给其他人的分享

分享这个UVX_GUIDE.md文件即可！

告诉他们：
1. 不需要下载任何Python文件
2. 只需要复制一个JSON配置
3. 自动下载和更新
4. 2分钟完成设置

**这是目前最简单的MCP服务器部署方案！** ✨