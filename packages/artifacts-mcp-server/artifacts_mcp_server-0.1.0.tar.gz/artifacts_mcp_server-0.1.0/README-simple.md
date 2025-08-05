# Artifacts MCP Server

**一个JSON，立即使用** 🚀

## 用户安装（仅需30秒）

### Raycast

1. 复制下面的JSON到 `~/.config/raycast/ai/mcp_servers.json`:

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

2. 替换 `your_api_key_here` → [获取API Key](https://www.agentsphere.run/apikey)

3. 重启 Raycast

**完成！** 无需安装Python包，无需配置环境。

### Cursor

同样简单，复制到 `~/.cursor/mcp_servers.json`：

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

## 使用

在AI客户端中：
- "创建一个Python数据分析脚本"
- "创建一个React组件"
- "创建一个响应式网页"

## 工作原理

- `uvx` = UV包管理器的工具运行器
- 自动从PyPI下载最新版本
- 自动管理Python环境和依赖
- 零配置，零维护

---

**就是这么简单！** 不需要：
- ❌ 安装Python包
- ❌ 管理虚拟环境  
- ❌ 处理依赖冲突
- ❌ 手动更新版本

只需要：
- ✅ 复制JSON
- ✅ 添加API Key
- ✅ 开始使用