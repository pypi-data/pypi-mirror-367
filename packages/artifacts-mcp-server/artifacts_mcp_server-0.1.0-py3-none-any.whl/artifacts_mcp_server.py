#!/usr/bin/env python3
"""
Artifacts MCP Server - UVX Ready Version
Zero-config MCP server for AI code artifacts with AgentSphere
Designed to work seamlessly with uvx
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

# Import dependencies (will be auto-installed by uvx)
from fastmcp import FastMCP
from agentsphere import Sandbox

# Initialize FastMCP server
mcp = FastMCP("artifacts-mcp-server")

# Global storage for artifacts
artifacts = {}

def get_api_key() -> Optional[str]:
    """Get AgentSphere API key from environment or show instructions"""
    api_key = os.getenv("AGENTSPHERE_API_KEY")
    
    if not api_key:
        print("⚠️  AgentSphere API Key not found!")
        print("")
        print("Please set your API key as an environment variable:")
        print("export AGENTSPHERE_API_KEY=your_api_key")
        print("")
        print("Get your API key at: https://www.agentsphere.run/apikey")
        return None
        
    return api_key

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
    api_key = get_api_key()
    if not api_key:
        return {
            "error": "Please set AGENTSPHERE_API_KEY environment variable",
            "instructions": "Run: export AGENTSPHERE_API_KEY=your_key"
        }
    
    artifact_id = f"artifact_{len(artifacts) + 1}"
    
    # Set environment variables for AgentSphere
    os.environ["AGENTSPHERE_API_KEY"] = api_key
    os.environ["AGENTSPHERE_DOMAIN"] = "agentsphere.run"
    
    try:
        # Create sandbox
        sandbox = Sandbox(
            timeout=300,  # 5 minutes
            metadata={
                "artifact_id": artifact_id,
                "title": title,
                "template": template,
                "created_by": "artifacts-mcp-server"
            }
        )
        
        preview_url = None
        execution_result = None
        execution_status = "success"
        
        # Execute based on template
        if template == "python":
            try:
                sandbox.files.write("script.py", code)
                
                # Install dependencies
                if dependencies:
                    for dep in dependencies:
                        result = sandbox.commands.run(f"pip install {dep}")
                        if result.exit_code != 0:
                            execution_result = f"Failed to install {dep}: {result.stderr}"
                            execution_status = "dependency_error"
                            break
                
                # Execute script
                if execution_status == "success":
                    result = sandbox.commands.run("python script.py", timeout=30)
                    execution_result = result.stdout if result.exit_code == 0 else result.stderr
                    execution_status = "success" if result.exit_code == 0 else "runtime_error"
                    
            except Exception as e:
                execution_result = f"Execution error: {str(e)}"
                execution_status = "timeout" if "timeout" in str(e).lower() else "error"
                
        elif template in ["javascript", "nodejs"]:
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
            sandbox.files.write("index.html", code)
            sandbox.commands.run("python -m http.server 3000", background=True)
            time.sleep(2)
            host = sandbox.get_host(3000)
            preview_url = f"https://{host}"
            execution_result = "HTML page is being served"
            execution_status = "success"
            
        elif template == "react":
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
        
        # Store artifact info
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
        
        # Auto-open browser if preview available
        if preview_url and execution_status == "success":
            try:
                import webbrowser
                webbrowser.open(preview_url)
                artifact["browser_opened"] = True
            except:
                artifact["browser_opened"] = False
        
        return {
            "artifact_id": artifact_id,
            "title": title,
            "template": template,
            "execution_status": execution_status,
            "preview_url": preview_url,
            "execution_result": execution_result,
            "message": f"✅ Artifact created successfully! ID: {artifact_id}"
        }
        
    except Exception as e:
        error_msg = str(e)
        
        if "timeout" in error_msg.lower():
            helpful_msg = "Code execution timed out. Try using web-based templates (html, react, streamlit) for better compatibility."
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
            "available_ids": list(artifacts.keys()),
            "hint": "Use list_artifacts to see all available artifacts"
        }
    
    artifact = artifacts[artifact_id]
    
    # Use new values or keep original
    new_title = title if title is not None else artifact["title"]
    new_dependencies = dependencies if dependencies is not None else artifact.get("dependencies", [])
    
    # Create updated artifact
    result = await create_artifact(
        title=new_title,
        template=artifact["template"],
        code=code,
        dependencies=new_dependencies
    )
    
    # Update original artifact entry
    if "artifact_id" in result and not result.get("error"):
        new_id = result["artifact_id"]
        if new_id in artifacts and new_id != artifact_id:
            artifacts.pop(new_id)
        
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
        result["message"] = f"✅ Artifact {artifact_id} updated successfully"
    
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
            "available_ids": list(artifacts.keys()),
            "hint": "Use list_artifacts to see all available artifacts"
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
        "message": f"📋 Found {len(artifacts)} artifacts"
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
        "message": f"🗑️ Deleted artifact: {artifact['title']}",
        "deleted_id": artifact_id,
        "remaining_count": len(artifacts)
    }

def main():
    """Entry point for uvx execution"""
    import sys
    
    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
🚀 Artifacts MCP Server

A zero-config MCP server for AI code artifacts with AgentSphere execution.

Usage:
  uvx artifacts-mcp-server                    # Start the MCP server
  uvx artifacts-mcp-server --help            # Show this help

Environment Variables:
  AGENTSPHERE_API_KEY    Your AgentSphere API key (required)

Setup:
1. Get your API key at: https://www.agentsphere.run/apikey
2. Set environment variable: export AGENTSPHERE_API_KEY=your_key
3. Configure your MCP client with: uvx artifacts-mcp-server

Supported Templates:
  python      Python scripts with console output
  javascript  JavaScript/Node.js scripts  
  html        Static HTML pages with live preview
  react       React applications with live preview
  vue         Vue.js applications with live preview
  streamlit   Streamlit data applications
  gradio      Gradio AI applications

Example MCP Client Configuration:
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

More info: https://github.com/yourusername/artifacts-mcp-server
        """)
        return
    
    # Check API key
    api_key = get_api_key()
    if not api_key:
        print("\n❌ Cannot start server without API key")
        print("Run with --help for setup instructions")
        sys.exit(1)
    
    print("🚀 Starting Artifacts MCP Server...")
    print(f"📍 API Key: {api_key[:10]}...")
    print("✨ Ready to create artifacts!")
    
    # Run the FastMCP server
    mcp.run()

if __name__ == "__main__":
    main()