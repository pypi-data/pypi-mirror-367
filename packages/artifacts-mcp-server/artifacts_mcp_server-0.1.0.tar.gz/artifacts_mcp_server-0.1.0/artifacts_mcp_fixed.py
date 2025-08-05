#!/usr/bin/env python3
"""
Artifacts MCP Server - 修复版本
兼容最新MCP API
"""

import os
import sys
import json
import asyncio
from pathlib import Path

# 自动安装依赖
def ensure_dependencies():
    deps = ["mcp", "agentsphere"]
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            print(f"Installing {dep}...")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

ensure_dependencies()

# 导入依赖
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server import Server
from mcp.types import Tool
from agentsphere import Sandbox


class ArtifactsMCP:
    def __init__(self):
        self.server = Server("artifacts-mcp")
        self.artifacts = {}
        
        # API Key配置 - 优先级：环境变量 > 配置文件 > 硬编码
        self.api_key = (
            os.getenv("AGENTSPHERE_API_KEY") or 
            self.load_config_key() or
            "your_api_key_here"  # 可以直接在这里填写你的API key
        )
        
        if self.api_key == "your_api_key_here":
            print("⚠️  请配置API Key:")
            print("1. 直接修改本文件中的 'your_api_key_here'")
            print("2. 或设置环境变量 AGENTSPHERE_API_KEY")
            print("3. 或创建 config.json 文件")
            print("获取API Key: https://www.agentsphere.run/apikey")
    
    def load_config_key(self):
        """从同目录的config.json加载API key"""
        config_path = Path(__file__).parent / "config.json"
        if config_path.exists():
            try:
                with open(config_path) as f:
                    config = json.load(f)
                    return config.get("agentsphere_api_key")
            except:
                pass
        return None
    
    async def handle_create_artifact(self, arguments):
        """处理创建artifact请求"""
        title = arguments.get("title", "Untitled")
        template = arguments.get("template", "python")
        code = arguments.get("code", "")
        dependencies = arguments.get("dependencies", [])
        
        if not self.api_key or self.api_key == "your_api_key_here":
            return {"error": "Please configure AGENTSPHERE_API_KEY"}
        
        artifact_id = f"artifact_{len(self.artifacts) + 1}"
        
        # 设置API key
        os.environ["AGENTSPHERE_API_KEY"] = self.api_key
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
                # 启动简单HTTP服务器
                sandbox.commands.run("python -m http.server 3000", background=True)
                host = sandbox.get_host(3000)
                preview_url = f"https://{host}"
                
            elif template == "react":
                # React应用
                # 创建基础React结构
                sandbox.files.write("index.html", """
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
""" + code + """
    </script>
</body>
</html>
                """)
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
                "sandbox_id": sandbox.sandbox_id if hasattr(sandbox, 'sandbox_id') else "unknown",
                "preview_url": preview_url,
                "execution_result": execution_result,
                "status": "ready"
            }
            
            self.artifacts[artifact_id] = artifact
            
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
    
    async def handle_update_artifact(self, arguments):
        """处理更新artifact请求"""
        artifact_id = arguments.get("artifact_id")
        code = arguments.get("code", "")
        
        if artifact_id not in self.artifacts:
            return {"error": "Artifact not found"}
        
        artifact = self.artifacts[artifact_id]
        return await self.handle_create_artifact({
            "title": artifact["title"],
            "template": artifact["template"],
            "code": code,
            "dependencies": artifact["dependencies"]
        })
    
    async def handle_execute_artifact(self, arguments):
        """处理执行artifact请求"""
        artifact_id = arguments.get("artifact_id")
        
        if artifact_id not in self.artifacts:
            return {"error": "Artifact not found"}
        
        artifact = self.artifacts[artifact_id]
        return await self.handle_create_artifact({
            "title": artifact["title"],
            "template": artifact["template"],
            "code": artifact["code"],
            "dependencies": artifact["dependencies"]
        })
    
    async def handle_list_artifacts(self, arguments):
        """处理列出artifacts请求"""
        return {
            "artifacts": list(self.artifacts.values()),
            "count": len(self.artifacts)
        }
    
    async def handle_get_artifact(self, arguments):
        """处理获取单个artifact请求"""
        artifact_id = arguments.get("artifact_id")
        
        if artifact_id not in self.artifacts:
            return {"error": "Artifact not found"}
        return self.artifacts[artifact_id]
    
    async def handle_call_tool(self, name, arguments):
        """统一的工具调用处理器"""
        handlers = {
            "create_artifact": self.handle_create_artifact,
            "update_artifact": self.handle_update_artifact,
            "execute_artifact": self.handle_execute_artifact,
            "list_artifacts": self.handle_list_artifacts,
            "get_artifact": self.handle_get_artifact,
        }
        
        handler = handlers.get(name)
        if handler:
            return await handler(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    async def run(self):
        """运行MCP服务器"""
        # 设置请求处理器
        @self.server.call_tool
        async def handle_call_tool(name, arguments):
            return await self.handle_call_tool(name, arguments)
        
        # 设置工具列表
        @self.server.list_tools
        async def handle_list_tools():
            return [
                Tool(
                    name="create_artifact",
                    description="Create a new code artifact with AgentSphere execution",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Title of the artifact"},
                            "template": {"type": "string", "enum": ["python", "javascript", "nodejs", "html", "react", "streamlit"], "description": "Code template type"},
                            "code": {"type": "string", "description": "The code content"},
                            "dependencies": {"type": "array", "items": {"type": "string"}, "description": "List of dependencies"}
                        },
                        "required": ["title", "template", "code"]
                    }
                ),
                Tool(
                    name="update_artifact",
                    description="Update existing artifact code",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "artifact_id": {"type": "string", "description": "ID of the artifact to update"},
                            "code": {"type": "string", "description": "New code content"}
                        },
                        "required": ["artifact_id", "code"]
                    }
                ),
                Tool(
                    name="execute_artifact",
                    description="Re-execute an existing artifact",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "artifact_id": {"type": "string", "description": "ID of the artifact to execute"}
                        },
                        "required": ["artifact_id"]
                    }
                ),
                Tool(
                    name="list_artifacts",
                    description="List all created artifacts",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_artifact",
                    description="Get specific artifact details",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "artifact_id": {"type": "string", "description": "ID of the artifact"}
                        },
                        "required": ["artifact_id"]
                    }
                )
            ]
        
        # 运行服务器
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="artifacts-mcp",
                    server_version="0.1.0"
                )
            )


def main():
    """主入口"""
    print("🚀 Starting Artifacts MCP Server...")
    print(f"📍 Working directory: {os.getcwd()}")
    
    server = ArtifactsMCP()
    
    # 如果直接运行（不是作为MCP服务器），显示帮助信息
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("""
Artifacts MCP Server - 使用说明

1. 配置API Key (三选一):
   a) 直接修改本文件中的 'your_api_key_here'
   b) 设置环境变量: export AGENTSPHERE_API_KEY=your_key
   c) 创建config.json: {"agentsphere_api_key": "your_key"}

2. 在Raycast/Cursor中配置MCP

3. 获取API Key: https://www.agentsphere.run/apikey
        """)
        return
    
    asyncio.run(server.run())


if __name__ == "__main__":
    main()