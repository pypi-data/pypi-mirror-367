# 开发指南

## 本地测试

### 1. 准备环境

```bash
# 克隆代码
git clone https://github.com/yourusername/artifacts-mcp-server
cd artifacts-mcp-server

# 设置API key
export AGENTSPHERE_API_KEY=your_test_key
```

### 2. 本地运行测试

#### 方法1: 直接Python运行
```bash
python artifacts_mcp_server.py
```

#### 方法2: UV本地安装
```bash
# 安装到虚拟环境
uv pip install -e .

# 运行
uv run artifacts-mcp-server
```

#### 方法3: 模拟uvx（从本地）
```bash
# 直接从当前目录运行
uvx --from . artifacts-mcp-server
```

### 3. 测试Raycast集成

使用提供的测试配置文件：

```bash
# 运行测试脚本生成配置
./test-local.sh

# 复制测试配置到Raycast
cp test-raycast-local.json ~/.config/raycast/ai/mcp_servers.json

# 重启Raycast进行测试
```

## 发布到PyPI

### 1. 准备发布

```bash
# 确保版本号更新
# 编辑 pyproject.toml 中的 version

# 构建包
uv build

# 检查构建结果
ls dist/
```

### 2. 配置PyPI认证

```bash
# 获取PyPI token
# https://pypi.org/manage/account/token/

# 设置环境变量
export UV_PUBLISH_USERNAME=__token__
export UV_PUBLISH_PASSWORD=pypi-your-token-here
```

### 3. 发布

```bash
# 发布到PyPI
uv publish

# 或发布到TestPyPI进行测试
uv publish --index-url https://test.pypi.org/simple/
```

### 4. 验证发布

```bash
# 等待几分钟让PyPI更新索引

# 测试安装
uvx artifacts-mcp-server --help

# 或使用pip
pip install artifacts-mcp-server
```

## 最终用户使用

发布后，用户只需要：

1. 复制JSON配置：
```json
{
  "mcpServers": {
    "artifacts": {
      "command": "uvx",
      "args": ["artifacts-mcp-server"],
      "env": {
        "AGENTSPHERE_API_KEY": "user_api_key"
      }
    }
  }
}
```

2. 粘贴到 `~/.config/raycast/ai/mcp_servers.json`

3. 重启Raycast

**就这么简单！** 

## 工作流程图

```
本地开发 → 测试 → 发布PyPI → 用户使用
   ↓         ↓        ↓           ↓
Python文件  UV本地   uv publish   uvx直接运行
```

## 版本管理

- 开发版本：0.1.0-dev
- 测试版本：0.1.0-beta
- 正式版本：0.1.0

## 注意事项

1. **依赖管理**: 保持最小依赖（mcp, agentsphere）
2. **兼容性**: 支持Python 3.9+
3. **错误处理**: 友好的错误提示
4. **自动化**: uvx会自动处理依赖安装