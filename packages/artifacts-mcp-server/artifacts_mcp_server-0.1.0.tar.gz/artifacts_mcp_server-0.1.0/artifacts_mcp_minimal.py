#!/usr/bin/env python3
"""
Artifacts MCP Server - 最小化版本
直接运行，自动安装依赖
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
from mcp.server.stdio import stdio_server
from mcp.server import Server
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
    
    async def create_artifact(self, title: str, template: str, code: str, dependencies: list = None):
        """创建并执行artifact"""
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
    
    async def update_artifact(self, artifact_id: str, code: str):
        """更新artifact代码"""
        if artifact_id not in self.artifacts:
            return {"error": "Artifact not found"}
        
        artifact = self.artifacts[artifact_id]
        return await self.create_artifact(
            artifact["title"],
            artifact["template"],
            code,
            artifact["dependencies"]
        )
    
    def setup_tools(self):
        """注册MCP工具"""
        
        @self.server.tool()
        async def create_artifact(
            title: str,
            template: str,
            code: str,
            dependencies: list = None
        ):
            """Create a new code artifact with AgentSphere execution"""
            return await self.create_artifact(title, template, code, dependencies)
        
        @self.server.tool()
        async def update_artifact(artifact_id: str, code: str):
            """Update existing artifact code"""
            return await self.update_artifact(artifact_id, code)
        
        @self.server.tool()
        async def execute_artifact(artifact_id: str):
            """Re-execute an existing artifact"""
            if artifact_id not in self.artifacts:
                return {"error": "Artifact not found"}
            
            artifact = self.artifacts[artifact_id]
            return await self.create_artifact(
                artifact["title"],
                artifact["template"],
                artifact["code"],
                artifact["dependencies"]
            )
        
        @self.server.tool()
        async def list_artifacts():
            """List all created artifacts"""
            return {
                "artifacts": list(self.artifacts.values()),
                "count": len(self.artifacts)
            }
        
        @self.server.tool()
        async def get_artifact(artifact_id: str):
            """Get specific artifact details"""
            if artifact_id not in self.artifacts:
                return {"error": "Artifact not found"}
            return self.artifacts[artifact_id]
    
    async def run(self):
        """运行MCP服务器"""
        self.setup_tools()
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)


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