#!/usr/bin/env python3
"""
Simplified Artifacts MCP Server
单文件实现，最小依赖，一键配置
"""

import json
import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# 动态导入，如果缺少依赖则提示安装
try:
    from mcp.server.stdio import stdio_server
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.types import Tool, Resource
except ImportError:
    print("❌ MCP SDK not found. Installing...")
    os.system(f"{sys.executable} -m pip install mcp")
    from mcp.server.stdio import stdio_server
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.types import Tool, Resource

try:
    from agentsphere import Sandbox
except ImportError:
    print("❌ AgentSphere SDK not found. Installing...")
    os.system(f"{sys.executable} -m pip install agentsphere")
    from agentsphere import Sandbox

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    os.system(f"{sys.executable} -m pip install python-dotenv")
    from dotenv import load_dotenv
    load_dotenv()


class SimpleArtifactsMCP:
    """简化的Artifacts MCP服务器"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self.load_or_create_config()
        self.server = Server("artifacts-mcp-simple")
        self.artifacts: Dict[str, Dict[str, Any]] = {}
        self.active_sandboxes: Dict[str, Sandbox] = {}
        
    def load_or_create_config(self) -> Dict[str, Any]:
        """加载或创建配置文件"""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        
        # 创建默认配置
        default_config = {
            "agentsphere_api_key": os.getenv("AGENTSPHERE_API_KEY", ""),
            "agentsphere_domain": "agentsphere.run", 
            "auto_open_browser": True,
            "preview_enabled": True,
            "log_level": "INFO",
            "raycast": {
                "config_path": "~/.config/raycast/ai/mcp_servers.json",
                "auto_configure": True
            },
            "cursor": {
                "config_path": "~/.cursor/mcp_servers.json",
                "auto_configure": False
            }
        }
        
        with open(config_file, 'w') as f:
            json.dump(default_config, f, indent=2)
            
        print(f"📄 已创建默认配置文件: {config_file}")
        
        if not default_config["agentsphere_api_key"]:
            print("\n⚠️  请配置AgentSphere API Key:")
            print("1. 访问: https://www.agentsphere.run/apikey")
            print("2. 创建API key")
            print("3. 方式1 - 环境变量: export AGENTSPHERE_API_KEY=your_key")
            print("4. 方式2 - 编辑config.json文件")
            
        return default_config
    
    def setup_agentsphere_env(self):
        """设置AgentSphere环境变量"""
        if self.config["agentsphere_api_key"]:
            os.environ["AGENTSPHERE_API_KEY"] = self.config["agentsphere_api_key"]
            os.environ["AGENTSPHERE_DOMAIN"] = self.config["agentsphere_domain"]
    
    async def create_artifact(self, 
                            title: str, 
                            template: str, 
                            code: str, 
                            dependencies: Optional[list] = None) -> Dict[str, Any]:
        """创建并执行artifact"""
        
        if not self.config["agentsphere_api_key"]:
            return {
                "error": "AgentSphere API key not configured. Please run: artifacts-mcp --setup"
            }
        
        self.setup_agentsphere_env()
        
        artifact_id = f"artifact_{len(self.artifacts) + 1}"
        
        try:
            # 创建沙箱
            sandbox = Sandbox(
                timeout=1800,  # 30分钟
                metadata={
                    "artifact_id": artifact_id,
                    "title": title,
                    "template": template,
                    "created_by": "artifacts-mcp-simple"
                }
            )
            
            preview_url = None
            execution_result = None
            
            # 根据模板执行代码
            if template == "python":
                result = sandbox.run_code(code)
                execution_result = str(result.logs)
                
            elif template == "javascript" or template == "nodejs":
                # 写入JS文件并执行
                await sandbox.files.write("code.js", code)
                if dependencies:
                    # 安装依赖
                    deps_str = " ".join(dependencies)
                    sandbox.commands.run(f"npm install {deps_str}")
                result = sandbox.commands.run("node code.js")
                execution_result = result.stdout
                
            elif template in ["html", "react", "vue", "nextjs"]:
                # Web应用模板
                if template == "html":
                    await sandbox.files.write("index.html", code)
                    sandbox.commands.run("python -m http.server 3000", background=True)
                elif template == "react":
                    # 创建React应用
                    await sandbox.files.write("src/App.jsx", code)
                    if dependencies:
                        deps_str = " ".join(dependencies)
                        sandbox.commands.run(f"npm install {deps_str}")
                    sandbox.commands.run("npm start", background=True)
                
                # 获取预览URL
                host = sandbox.get_host(3000)
                preview_url = f"https://{host}"
                
            elif template == "streamlit":
                # Streamlit应用
                await sandbox.files.write("app.py", code)
                if dependencies:
                    deps_str = " ".join(dependencies)
                    sandbox.commands.run(f"pip install {deps_str}")
                sandbox.commands.run("streamlit run app.py --server.port 8501", background=True)
                host = sandbox.get_host(8501)
                preview_url = f"https://{host}"
            
            # 存储artifact信息
            artifact = {
                "id": artifact_id,
                "title": title,
                "template": template,
                "code": code,
                "dependencies": dependencies or [],
                "sandbox_id": sandbox.get_info().sandbox_id,
                "preview_url": preview_url,
                "execution_result": execution_result,
                "status": "ready",
                "created_at": sandbox.get_info().started_at.isoformat()
            }
            
            self.artifacts[artifact_id] = artifact
            self.active_sandboxes[artifact_id] = sandbox
            
            # 自动打开浏览器
            if preview_url and self.config["auto_open_browser"]:
                import webbrowser
                webbrowser.open(preview_url)
                
            return artifact
            
        except Exception as e:
            return {
                "error": f"Failed to create artifact: {str(e)}",
                "artifact_id": artifact_id
            }
    
    async def update_artifact(self, artifact_id: str, code: str) -> Dict[str, Any]:
        """更新artifact代码"""
        if artifact_id not in self.artifacts:
            return {"error": "Artifact not found"}
        
        artifact = self.artifacts[artifact_id]
        artifact["code"] = code
        
        # 重新创建沙箱执行更新的代码
        return await self.create_artifact(
            artifact["title"], 
            artifact["template"], 
            code, 
            artifact["dependencies"]
        )
    
    async def list_artifacts(self) -> Dict[str, Any]:
        """列出所有artifacts"""
        return {
            "artifacts": list(self.artifacts.values()),
            "count": len(self.artifacts)
        }
    
    def setup_tools(self):
        """设置MCP工具"""
        
        @self.server.tool()
        async def create_artifact(
            title: str,
            template: str, 
            code: str,
            dependencies: list = None
        ) -> Dict[str, Any]:
            """创建新的代码artifact"""
            return await self.create_artifact(title, template, code, dependencies)
        
        @self.server.tool()
        async def update_artifact(artifact_id: str, code: str) -> Dict[str, Any]:
            """更新existing artifact的代码"""
            return await self.update_artifact(artifact_id, code)
        
        @self.server.tool() 
        async def execute_artifact(artifact_id: str) -> Dict[str, Any]:
            """执行artifact"""
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
        async def list_artifacts() -> Dict[str, Any]:
            """列出所有artifacts"""
            return await self.list_artifacts()
        
        @self.server.tool()
        async def delete_artifact(artifact_id: str) -> Dict[str, Any]:
            """删除artifact"""
            if artifact_id not in self.artifacts:
                return {"error": "Artifact not found"}
            
            # 清理沙箱
            if artifact_id in self.active_sandboxes:
                try:
                    self.active_sandboxes[artifact_id].kill()
                except:
                    pass
                del self.active_sandboxes[artifact_id]
            
            artifact = self.artifacts.pop(artifact_id)
            return {"message": f"Deleted artifact: {artifact['title']}"}
    
    def configure_raycast(self):
        """自动配置Raycast"""
        raycast_config_path = Path(self.config["raycast"]["config_path"]).expanduser()
        raycast_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 读取现有配置或创建新配置
        if raycast_config_path.exists():
            with open(raycast_config_path, 'r') as f:
                raycast_config = json.load(f)
        else:
            raycast_config = {"mcpServers": {}}
        
        # 添加artifacts配置
        raycast_config["mcpServers"]["artifacts"] = {
            "command": "python",
            "args": [str(Path(__file__).absolute())],
            "env": {
                "AGENTSPHERE_API_KEY": self.config["agentsphere_api_key"]
            }
        }
        
        with open(raycast_config_path, 'w') as f:
            json.dump(raycast_config, f, indent=2)
        
        print(f"✅ Raycast配置已更新: {raycast_config_path}")
        print("请重启Raycast使配置生效")
    
    def configure_cursor(self):
        """配置Cursor"""
        cursor_config_path = Path(self.config["cursor"]["config_path"]).expanduser()
        cursor_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        cursor_config = {
            "mcp": {
                "servers": {
                    "artifacts": {
                        "command": "python",
                        "args": [str(Path(__file__).absolute())],
                        "env": {
                            "AGENTSPHERE_API_KEY": self.config["agentsphere_api_key"]
                        }
                    }
                }
            }
        }
        
        with open(cursor_config_path, 'w') as f:
            json.dump(cursor_config, f, indent=2)
        
        print(f"✅ Cursor配置已更新: {cursor_config_path}")
    
    def validate_setup(self):
        """验证设置"""
        issues = []
        
        if not self.config["agentsphere_api_key"]:
            issues.append("❌ AgentSphere API key未配置")
        else:
            print("✅ AgentSphere API key已配置")
        
        # 测试AgentSphere连接
        if self.config["agentsphere_api_key"]:
            try:
                self.setup_agentsphere_env()
                test_sandbox = Sandbox(timeout=10)
                test_sandbox.kill()
                print("✅ AgentSphere连接测试成功")
            except Exception as e:
                issues.append(f"❌ AgentSphere连接失败: {e}")
        
        if issues:
            print("\n🔧 需要解决的问题:")
            for issue in issues:
                print(f"  {issue}")
            print("\n运行 'python artifacts-mcp.py --setup' 进行配置")
        else:
            print("\n🎉 所有配置都正确！")
    
    async def run(self):
        """运行MCP服务器"""
        self.setup_tools()
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, 
                write_stream, 
                InitializationOptions(
                    server_name="artifacts-mcp-simple",
                    server_version="0.1.0",
                    capabilities={}
                )
            )


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(description="Simplified Artifacts MCP Server")
    parser.add_argument("--config", default="config.json", help="配置文件路径")
    parser.add_argument("--setup", action="store_true", help="运行初始设置")
    parser.add_argument("--setup-raycast", action="store_true", help="配置Raycast")
    parser.add_argument("--setup-cursor", action="store_true", help="配置Cursor") 
    parser.add_argument("--validate", action="store_true", help="验证配置")
    
    args = parser.parse_args()
    
    server = SimpleArtifactsMCP(args.config)
    
    if args.setup:
        print("🔧 运行初始设置...")
        server.validate_setup()
        if input("\n配置Raycast? (y/N): ").lower() == 'y':
            server.configure_raycast()
        if input("配置Cursor? (y/N): ").lower() == 'y':
            server.configure_cursor()
    elif args.setup_raycast:
        server.configure_raycast()
    elif args.setup_cursor:
        server.configure_cursor()
    elif args.validate:
        server.validate_setup()
    else:
        # 启动MCP服务器
        print("🚀 启动Artifacts MCP Server...")
        asyncio.run(server.run())


if __name__ == "__main__":
    main()