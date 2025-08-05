# Artifacts MCP Server - 让AI帮你写代码并实时预览

## 这是什么？

一个连接Raycast AI和代码执行环境的工具。你可以：
- 让AI写代码并立即看到运行结果
- 创建网页、应用并获得预览链接
- 支持Python、JavaScript、HTML、React等多种语言

## 需要的文件

1. **artifacts_fastmcp_fixed.py** - 主程序文件
2. **INSTALL_GUIDE.md** - 详细安装说明
3. **CLIENT_CONFIGS.md** - 多客户端配置指南

## 快速开始

1. **获取API Key**（5分钟）
   - 访问 https://www.agentsphere.run/
   - 注册并创建API Key

2. **安装**（5分钟）
   ```bash
   # 创建目录
   mkdir ~/mcp-tools
   cd ~/mcp-tools
   
   # 放入python文件
   # 创建config.json配置API Key
   ```

3. **配置AI客户端**（2分钟）
   - 选择客户端：Claude Desktop、Raycast、Cursor、Zed等  
   - 按CLIENT_CONFIGS.md配置
   - 重启客户端

4. **开始使用**
   在任何AI客户端中：
   - "用artifacts创建一个python脚本"
   - "用artifacts创建一个网页"

详细步骤请看 **INSTALL_GUIDE.md**

## 支持的功能

✅ Python脚本执行
✅ HTML网页（自动预览）
✅ React应用（自动预览）
✅ Streamlit数据应用
✅ JavaScript/Node.js
✅ Vue.js应用

## 给其他人的说明

发送这4个文件：
1. `artifacts_fastmcp_fixed.py`
2. `INSTALL_GUIDE.md`
3. `CLIENT_CONFIGS.md`
4. `README_SIMPLE.md`（本文件）

告诉他们：
- 需要Python 3.9+
- 需要支持MCP的AI客户端（Claude Desktop、Raycast、Cursor等）
- 按照INSTALL_GUIDE.md操作即可

## 常见问题

**Q: 需要编程知识吗？**
A: 不需要，只要会复制粘贴就行。

**Q: 免费吗？**
A: AgentSphere提供免费额度，客户端有些免费有些付费（Claude Desktop免费，Raycast需Pro）。

**Q: 安全吗？**
A: 代码在云端沙箱运行，不会影响本地电脑。

---

有问题？查看 INSTALL_GUIDE.md 和 CLIENT_CONFIGS.md 或联系分享者。