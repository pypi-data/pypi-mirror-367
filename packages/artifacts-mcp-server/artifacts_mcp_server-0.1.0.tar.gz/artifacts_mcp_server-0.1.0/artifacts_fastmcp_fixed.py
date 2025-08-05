#!/usr/bin/env python3
"""
Artifacts MCP Server - 修复版
修复了update_artifact的参数问题
"""

import os
import sys
import json
import asyncio
from pathlib import Path
import time
from typing import Optional, List, Dict, Any

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
        api_key = "your_api_key_here"
        
    if api_key == "your_api_key_here":
        print("⚠️  请配置API Key:")
        print("1. 创建config.json: {'agentsphere_api_key': 'your_key'}")
        print("2. 或设置环境变量: export AGENTSPHERE_API_KEY=your_key")
        print("获取API Key: https://www.agentsphere.run/apikey")
    
    return api_key

# 获取API Key
API_KEY = load_config()

@mcp.tool()
async def create_artifact(
    title: str,
    template: str,
    code: str,
    dependencies: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a new code artifact with AgentSphere execution
    
    Args:
        title: Title of the artifact
        template: Code template type (python, javascript, html, react, streamlit, vue, gradio)
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
            timeout=300,  # 5分钟超时
            metadata={
                "artifact_id": artifact_id,
                "title": title,
                "template": template
            }
        )
        
        preview_url = None
        execution_result = None
        execution_status = "success"
        
        # 根据模板执行代码
        if template == "python":
            # Python脚本
            try:
                sandbox.files.write("script.py", code)
                
                if dependencies:
                    for dep in dependencies:
                        result = sandbox.commands.run(f"pip install {dep}")
                        if result.exit_code != 0:
                            execution_result = f"Failed to install {dep}: {result.stderr}"
                            execution_status = "dependency_error"
                            break
                
                if execution_status == "success":
                    result = sandbox.commands.run("python script.py", timeout=30)
                    execution_result = result.stdout if result.exit_code == 0 else result.stderr
                    execution_status = "success" if result.exit_code == 0 else "runtime_error"
                    
            except Exception as e:
                execution_result = f"Execution error: {str(e)}"
                execution_status = "timeout" if "timeout" in str(e).lower() else "error"
                
        elif template in ["javascript", "nodejs"]:
            # JavaScript/Node.js
            try:
                sandbox.files.write("script.js", code)
                
                if dependencies:
                    deps_str = " ".join(dependencies)
                    result = sandbox.commands.run(f"npm install {deps_str}")
                    if result.exit_code != 0:
                        execution_result = f"Failed to install dependencies: {result.stderr}"
                        execution_status = "dependency_error"
                
                if execution_status == "success":
                    result = sandbox.commands.run("node script.js", timeout=30)
                    execution_result = result.stdout if result.exit_code == 0 else result.stderr
                    execution_status = "success" if result.exit_code == 0 else "runtime_error"
                    
            except Exception as e:
                execution_result = f"Execution error: {str(e)}"
                execution_status = "error"
                
        elif template == "html":
            # HTML页面
            sandbox.files.write("index.html", code)
            sandbox.commands.run("python -m http.server 3000", background=True)
            time.sleep(2)
            host = sandbox.get_host(3000)
            preview_url = f"https://{host}"
            execution_result = "HTML page is being served"
            execution_status = "success"
            
        elif template == "react":
            # React应用
            react_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script crossorigin src="https://unpkg.com/react@18/umd/react.production.min.js"></script>
    <script crossorigin src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script>
    <script src="https://unpkg.com/@babel/standalone/babel.min.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
    </style>
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
            time.sleep(2)
            host = sandbox.get_host(3000)
            preview_url = f"https://{host}"
            execution_result = "React app is running"
            execution_status = "success"
            
        elif template == "vue":
            # Vue应用
            vue_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>
    <style>
        body {{ margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
    </style>
</head>
<body>
    <div id="app"></div>
    <script>
{code}
    </script>
</body>
</html>
"""
            sandbox.files.write("index.html", vue_html)
            sandbox.commands.run("python -m http.server 3000", background=True)
            time.sleep(2)
            host = sandbox.get_host(3000)
            preview_url = f"https://{host}"
            execution_result = "Vue app is running"
            execution_status = "success"
            
        elif template == "streamlit":
            # Streamlit应用
            sandbox.files.write("app.py", code)
            
            sandbox.commands.run("pip install streamlit")
            if dependencies:
                for dep in dependencies:
                    sandbox.commands.run(f"pip install {dep}")
                    
            sandbox.commands.run("streamlit run app.py --server.port 8501", background=True)
            time.sleep(5)
            host = sandbox.get_host(8501)
            preview_url = f"https://{host}"
            execution_result = "Streamlit app is running"
            execution_status = "success"
            
        elif template == "gradio":
            # Gradio应用
            sandbox.files.write("app.py", code)
            
            sandbox.commands.run("pip install gradio")
            if dependencies:
                for dep in dependencies:
                    sandbox.commands.run(f"pip install {dep}")
                    
            sandbox.commands.run("python app.py", background=True)
            time.sleep(5)
            host = sandbox.get_host(7860)
            preview_url = f"https://{host}"
            execution_result = "Gradio app is running"
            execution_status = "success"
        
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
            "execution_status": execution_status,
            "status": "ready",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        artifacts[artifact_id] = artifact
        
        # 自动打开浏览器
        if preview_url and execution_status == "success":
            try:
                import webbrowser
                webbrowser.open(preview_url)
                artifact["browser_opened"] = True
            except:
                artifact["browser_opened"] = False
        
        # 返回更详细的信息
        response = {
            "artifact_id": artifact_id,
            "title": title,
            "template": template,
            "execution_status": execution_status,
            "preview_url": preview_url,
            "execution_result": execution_result,
            "message": f"Artifact created successfully. ID: {artifact_id}"
        }
        
        if execution_status != "success":
            response["message"] = f"Artifact created but execution had issues. Status: {execution_status}"
            
        return response
        
    except Exception as e:
        error_msg = str(e)
        
        if "timeout" in error_msg.lower():
            helpful_msg = "The code execution timed out. This might happen with GUI applications (like Pygame) or long-running processes. Consider using web-based templates (html, react, streamlit) instead."
        elif "api" in error_msg.lower() or "key" in error_msg.lower():
            helpful_msg = "API key issue. Please check your AgentSphere API key is valid."
        else:
            helpful_msg = "An unexpected error occurred. Please check your code and try again."
            
        return {
            "error": f"Failed to create artifact: {error_msg}",
            "artifact_id": artifact_id,
            "hint": helpful_msg,
            "execution_status": "error"
        }

@mcp.tool()
async def update_artifact(
    artifact_id: str,
    code: str,
    title: Optional[str] = None,
    dependencies: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Update existing artifact code
    
    Args:
        artifact_id: ID of the artifact to update
        code: New code content
        title: Optional new title
        dependencies: Optional new dependencies list
    
    Returns:
        Updated artifact details
    """
    if artifact_id not in artifacts:
        return {
            "error": "Artifact not found",
            "hint": "Use list_artifacts to see available artifacts",
            "available_ids": list(artifacts.keys())
        }
    
    artifact = artifacts[artifact_id]
    
    # 使用新值或保留原值
    new_title = title if title is not None else artifact["title"]
    new_dependencies = dependencies if dependencies is not None else artifact.get("dependencies", [])
    
    # 创建新的artifact（会更新原有的）
    result = await create_artifact(
        title=new_title,
        template=artifact["template"],
        code=code,
        dependencies=new_dependencies
    )
    
    # 如果成功，更新artifact ID以保持一致
    if "artifact_id" in result and not result.get("error"):
        # 删除新创建的artifact
        new_id = result["artifact_id"]
        if new_id in artifacts and new_id != artifact_id:
            artifacts.pop(new_id)
        
        # 更新原artifact
        artifacts[artifact_id].update({
            "code": code,
            "title": new_title,
            "dependencies": new_dependencies,
            "preview_url": result.get("preview_url"),
            "execution_result": result.get("execution_result"),
            "execution_status": result.get("execution_status"),
            "updated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        
        result["artifact_id"] = artifact_id
        result["message"] = f"Artifact {artifact_id} updated successfully"
    
    return result

@mcp.tool()
async def execute_artifact(artifact_id: str) -> Dict[str, Any]:
    """
    Re-execute an existing artifact
    
    Args:
        artifact_id: ID of the artifact to execute
    
    Returns:
        Execution result with preview URL if applicable
    """
    if artifact_id not in artifacts:
        return {
            "error": "Artifact not found",
            "hint": "Use list_artifacts to see available artifacts",
            "available_ids": list(artifacts.keys())
        }
    
    artifact = artifacts[artifact_id]
    return await create_artifact(
        title=artifact["title"],
        template=artifact["template"],
        code=artifact["code"],
        dependencies=artifact.get("dependencies", [])
    )

@mcp.tool()
async def list_artifacts() -> Dict[str, Any]:
    """
    List all created artifacts
    
    Returns:
        List of all artifacts with their details
    """
    # 简化返回的信息，避免过长
    simplified_artifacts = []
    for artifact in artifacts.values():
        simplified_artifacts.append({
            "id": artifact["id"],
            "title": artifact["title"],
            "template": artifact["template"],
            "preview_url": artifact.get("preview_url"),
            "execution_status": artifact.get("execution_status", "unknown"),
            "created_at": artifact.get("created_at", "unknown")
        })
    
    return {
        "artifacts": simplified_artifacts,
        "count": len(artifacts),
        "message": f"Found {len(artifacts)} artifacts"
    }

@mcp.tool()
async def get_artifact(artifact_id: str) -> Dict[str, Any]:
    """
    Get specific artifact details
    
    Args:
        artifact_id: ID of the artifact
    
    Returns:
        Artifact details or error if not found
    """
    if artifact_id not in artifacts:
        return {
            "error": "Artifact not found",
            "available_ids": list(artifacts.keys()),
            "hint": "Use list_artifacts to see all available artifacts"
        }
    return artifacts[artifact_id]

@mcp.tool()
async def delete_artifact(artifact_id: str) -> Dict[str, Any]:
    """
    Delete an artifact
    
    Args:
        artifact_id: ID of the artifact to delete
    
    Returns:
        Success message or error
    """
    if artifact_id not in artifacts:
        return {
            "error": "Artifact not found",
            "available_ids": list(artifacts.keys()),
            "hint": "Use list_artifacts to see all available artifacts"
        }
    
    artifact = artifacts.pop(artifact_id)
    return {
        "message": f"Deleted artifact: {artifact['title']}",
        "deleted_id": artifact_id,
        "remaining_count": len(artifacts)
    }

# 主函数
if __name__ == "__main__":
    import sys
    
    # 显示帮助信息
    if "--help" in sys.argv:
        print("""
Artifacts MCP Server (修复版) - 使用说明

1. 配置API Key (三选一):
   a) 创建config.json: {"agentsphere_api_key": "your_key"}
   b) 设置环境变量: export AGENTSPHERE_API_KEY=your_key
   c) 直接修改本文件中的 'your_api_key_here'

2. 在Raycast/Cursor中配置:
   {
     "mcpServers": {
       "artifacts": {
         "command": "python3",
         "args": ["/path/to/artifacts_fastmcp_fixed.py"]
       }
     }
   }

3. 获取API Key: https://www.agentsphere.run/apikey

支持的模板:
- python: Python脚本（终端输出）
- javascript/nodejs: JavaScript/Node.js脚本
- html: 静态HTML页面（带预览）
- react: React应用（带预览）
- vue: Vue.js应用（带预览）
- streamlit: Streamlit数据应用（带预览）
- gradio: Gradio AI应用（带预览）

使用提示:
- update_artifact现在支持更新代码、标题和依赖
- GUI应用（如Pygame）可能会超时，建议使用Web模板
- Web应用会自动打开预览URL
        """)
        sys.exit(0)
    
    # 运行MCP服务器
    print("🚀 Starting Artifacts MCP Server (Fixed)...")
    print(f"📍 Working directory: {os.getcwd()}")
    
    # FastMCP会自动处理stdio通信
    mcp.run()