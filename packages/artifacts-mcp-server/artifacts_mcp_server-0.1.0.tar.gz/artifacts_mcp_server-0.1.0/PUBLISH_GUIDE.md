# PyPI Publishing Guide

## 📦 如何发布到PyPI (详细步骤)

由于我无法直接访问您的PyPI账户，请按照以下步骤自行发布：

### 第1步：准备PyPI账户

1. **注册PyPI账户** (如果没有)
   - 访问: https://pypi.org/account/register/
   - 填写信息并验证邮箱

2. **生成API Token**
   - 登录PyPI后，访问: https://pypi.org/manage/account/token/
   - 点击 "Add API token"
   - Token name: `artifacts-mcp-server`
   - Scope: 选择 "Entire account" (首次发布)
   - 复制生成的token (格式: `pypi-AgE...`)

### 第2步：安装发布工具

确保已安装UV:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 第3步：构建和发布

在项目目录中运行:

```bash
cd /home/ubuntu/jack/projects/artifacts/artifacts-mcp-simple

# 构建包
uv build

# 发布到PyPI
uv publish

# 输入你的PyPI token (以pypi-AgE开头)
```

### 第4步：验证发布

1. **检查PyPI页面**
   - 访问: https://pypi.org/project/artifacts-mcp-server/
   - 确认包信息正确显示

2. **测试安装**
   ```bash
   # 测试uvx运行
   uvx artifacts-mcp-server --help
   
   # 应该显示帮助信息
   ```

### 第5步：更新版本 (后续发布)

修改 `pyproject.toml` 中的版本号:
```toml
version = "0.1.1"  # 递增版本
```

然后重复构建和发布步骤。

---

## 🔧 故障排除

### 1. "Package already exists"
- 增加版本号在 `pyproject.toml`
- 重新构建和发布

### 2. "Invalid API token"
- 检查token是否完整复制
- 确保token有正确的权限

### 3. "Build failed"
- 检查依赖是否正确: `fastmcp>=2.0.0`, `agentsphere>=0.1.0`
- 确保Python版本 >= 3.9

---

## 📊 发布完成后

发布成功后，用户就可以使用:

```bash
# 直接运行 (无需下载文件)
uvx artifacts-mcp-server

# 或带帮助
uvx artifacts-mcp-server --help
```

**分享UVX_GUIDE.md给用户即可！** ✨

---

## 🎯 推广建议

1. **GitHub仓库**: 创建GitHub repo并推送代码
2. **文档网站**: 考虑创建简单的文档站点
3. **社区分享**: 在MCP相关社区分享此工具

发布后记得更新README.md中的GitHub链接！