#!/usr/bin/env python3
"""
Artifacts MCP Server - FastMCP版本
使用FastMCP框架，更简单易用
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# 自动安装依赖
def ensure_dependencies():
    deps = ["fastmcp", "agentsphere"]
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            print(f"Installing {dep}...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

ensure_dependencies()

# 导入依赖
from fastmcp import FastMCP
from agentsphere import Sandbox

# 初始化FastMCP
mcp = FastMCP("artifacts-mcp")

# 全局变量存储artifacts
artifacts = {}

# 加载配置
def load_config():
    """加载API Key配置"""
    # 优先级：环境变量 > config.json > 硬编码
    api_key = os.getenv("AGENTSPHERE_API_KEY")
    
    if not api_key:
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    api_key = config.get("agentsphere_api_key")
            except:
                pass
    
    if not api_key:
        api_key = "your_api_key_here"  # 可以直接在这里填写
        
    if api_key == "your_api_key_here":
        print("⚠️  请配置API Key:")
        print("1. 创建config.json: {'agentsphere_api_key': 'your_key'}")
        print("2. 或设置环境变量: export AGENTSPHERE_API_KEY=your_key")
        print("3. 或直接修改本文件中的 'your_api_key_here'")
        print("获取API Key: https://www.agentsphere.run/apikey")
    
    return api_key

# 获取API Key
API_KEY = load_config()

@mcp.tool()
async def create_artifact(
    title: str,
    template: str,
    code: str,
    dependencies: list[str] = None
) -> dict:
    """
    Create a new code artifact with AgentSphere execution
    
    Args:
        title: Title of the artifact
        template: Code template type (python, javascript, html, react, streamlit)
        code: The code content
        dependencies: Optional list of dependencies
    
    Returns:
        Artifact details including ID, preview URL, and execution result
    """
    if not API_KEY or API_KEY == "your_api_key_here":
        return {"error": "Please configure AGENTSPHERE_API_KEY"}
    
    artifact_id = f"artifact_{len(artifacts) + 1}"
    
    # 设置环境变量
    os.environ["AGENTSPHERE_API_KEY"] = API_KEY
    os.environ["AGENTSPHERE_DOMAIN"] = "agentsphere.run"
    
    try:
        # 创建沙箱
        sandbox = Sandbox(
            timeout=1800,
            metadata={
                "artifact_id": artifact_id,
                "title": title,
                "template": template
            }
        )
        
        preview_url = None
        execution_result = None
        
        # 根据模板执行代码
        if template == "python":
            # Python脚本
            result = sandbox.run_code(code)
            execution_result = str(result.logs) if hasattr(result, 'logs') else str(result)
            
        elif template in ["javascript", "nodejs"]:
            # JavaScript/Node.js
            sandbox.files.write("code.js", code)
            if dependencies:
                deps_str = " ".join(dependencies)
                sandbox.commands.run(f"npm install {deps_str}")
            result = sandbox.commands.run("node code.js")
            execution_result = result.stdout if hasattr(result, 'stdout') else str(result)
            
        elif template == "html":
            # HTML页面
            sandbox.files.write("index.html", code)
            # 启动HTTP服务器
            sandbox.commands.run("python -m http.server 3000", background=True)
            host = sandbox.get_host(3000)
            preview_url = f"https://{host}"
            
        elif template == "react":
            # React应用
            react_html = f"""
<!DOCTYPE html>
<html>
<head>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
</head>
<body>
    <div id="root"></div>
    <script type="text/babel">
{code}
    </script>
</body>
</html>
"""
            sandbox.files.write("index.html", react_html)
            sandbox.commands.run("python -m http.server 3000", background=True)
            host = sandbox.get_host(3000)
            preview_url = f"https://{host}"
            
        elif template == "streamlit":
            # Streamlit应用
            sandbox.files.write("app.py", code)
            if dependencies:
                deps_str = " ".join(dependencies)
                sandbox.commands.run(f"pip install {deps_str}")
            sandbox.commands.run("pip install streamlit")
            sandbox.commands.run("streamlit run app.py --server.port 8501", background=True)
            host = sandbox.get_host(8501)
            preview_url = f"https://{host}"
        
        # 保存artifact信息
        artifact = {
            "id": artifact_id,
            "title": title,
            "template": template,
            "code": code,
            "dependencies": dependencies or [],
            "sandbox_id": getattr(sandbox, 'sandbox_id', 'unknown'),
            "preview_url": preview_url,
            "execution_result": execution_result,
            "status": "ready"
        }
        
        artifacts[artifact_id] = artifact
        
        # 自动打开浏览器
        if preview_url:
            try:
                import webbrowser
                webbrowser.open(preview_url)
                artifact["browser_opened"] = True
            except:
                artifact["browser_opened"] = False
                
        return artifact
        
    except Exception as e:
        return {
            "error": f"Failed to create artifact: {str(e)}",
            "artifact_id": artifact_id,
            "hint": "Check your API key and network connection"
        }

@mcp.tool()
async def update_artifact(artifact_id: str, code: str) -> dict:
    """
    Update existing artifact code
    
    Args:
        artifact_id: ID of the artifact to update
        code: New code content
    
    Returns:
        Updated artifact details
    """
    if artifact_id not in artifacts:
        return {"error": "Artifact not found"}
    
    artifact = artifacts[artifact_id]
    return await create_artifact(
        title=artifact["title"],
        template=artifact["template"],
        code=code,
        dependencies=artifact["dependencies"]
    )

@mcp.tool()
async def execute_artifact(artifact_id: str) -> dict:
    """
    Re-execute an existing artifact
    
    Args:
        artifact_id: ID of the artifact to execute
    
    Returns:
        Execution result with preview URL if applicable
    """
    if artifact_id not in artifacts:
        return {"error": "Artifact not found"}
    
    artifact = artifacts[artifact_id]
    return await create_artifact(
        title=artifact["title"],
        template=artifact["template"],
        code=artifact["code"],
        dependencies=artifact["dependencies"]
    )

@mcp.tool()
async def list_artifacts() -> dict:
    """
    List all created artifacts
    
    Returns:
        List of all artifacts with their details
    """
    return {
        "artifacts": list(artifacts.values()),
        "count": len(artifacts)
    }

@mcp.tool()
async def get_artifact(artifact_id: str) -> dict:
    """
    Get specific artifact details
    
    Args:
        artifact_id: ID of the artifact
    
    Returns:
        Artifact details or error if not found
    """
    if artifact_id not in artifacts:
        return {"error": "Artifact not found"}
    return artifacts[artifact_id]

@mcp.tool()
async def delete_artifact(artifact_id: str) -> dict:
    """
    Delete an artifact
    
    Args:
        artifact_id: ID of the artifact to delete
    
    Returns:
        Success message or error
    """
    if artifact_id not in artifacts:
        return {"error": "Artifact not found"}
    
    artifact = artifacts.pop(artifact_id)
    return {"message": f"Deleted artifact: {artifact['title']}"}

# 主函数
if __name__ == "__main__":
    import sys
    
    # 显示帮助信息
    if "--help" in sys.argv:
        print("""
Artifacts MCP Server (FastMCP版本) - 使用说明

1. 配置API Key (三选一):
   a) 创建config.json: {"agentsphere_api_key": "your_key"}
   b) 设置环境变量: export AGENTSPHERE_API_KEY=your_key
   c) 直接修改本文件中的 'your_api_key_here'

2. 在Raycast/Cursor中配置:
   {
     "mcpServers": {
       "artifacts": {
         "command": "python",
         "args": ["/path/to/artifacts_fastmcp.py"]
       }
     }
   }

3. 获取API Key: https://www.agentsphere.run/apikey

支持的模板:
- python: Python脚本
- javascript/nodejs: JavaScript/Node.js脚本
- html: 静态HTML页面
- react: React应用
- streamlit: Streamlit数据应用
        """)
        sys.exit(0)
    
    # 运行MCP服务器
    print("🚀 Starting Artifacts MCP Server (FastMCP)...")
    print(f"📍 Working directory: {os.getcwd()}")
    
    # FastMCP会自动处理stdio通信
    mcp.run()