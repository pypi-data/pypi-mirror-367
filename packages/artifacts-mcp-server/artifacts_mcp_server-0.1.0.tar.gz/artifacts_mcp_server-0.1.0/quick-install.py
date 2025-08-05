#!/usr/bin/env python3
"""
一键安装和配置脚本
使用: python quick-install.py
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path

def run_command(cmd, check=True):
    """执行命令"""
    print(f"🔧 执行: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"❌ 命令失败: {result.stderr}")
        sys.exit(1)
    return result

def check_python():
    """检查Python版本"""
    if sys.version_info < (3, 9):
        print("❌ 需要Python 3.9+")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

def install_uv():
    """安装UV包管理器"""
    if shutil.which("uv"):
        print("✅ UV已安装")
        return
    
    print("📦 安装UV包管理器...")
    run_command("curl -LsSf https://astral.sh/uv/install.sh | sh")
    
    # 添加到PATH
    cargo_env = Path.home() / ".cargo" / "env"
    if cargo_env.exists():
        run_command(f"source {cargo_env}")

def install_dependencies():
    """安装Python依赖"""
    print("📦 安装Python依赖...")
    
    # 使用UV或pip安装
    if shutil.which("uv"):
        run_command("uv add mcp agentsphere python-dotenv")
    else:
        run_command("pip install mcp agentsphere python-dotenv")

def setup_config():
    """创建配置文件"""
    config_file = Path("config.json")
    
    if config_file.exists():
        print("✅ 配置文件已存在")
        return
    
    print("⚙️ 创建配置文件...")
    
    # 提示用户输入API key
    print("\n请配置AgentSphere API Key:")
    print("1. 访问: https://www.agentsphere.run/apikey")
    print("2. 点击CREATE KEY创建API key")
    
    api_key = input("3. 请输入API key (或回车跳过): ").strip()
    
    config = {
        "agentsphere_api_key": api_key,
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
        json.dump(config, f, indent=2)
    
    print(f"✅ 配置文件已创建: {config_file}")

def setup_raycast():
    """配置Raycast"""
    if input("\n配置Raycast? (Y/n): ").lower() != 'n':
        raycast_dir = Path.home() / ".config" / "raycast" / "ai"
        raycast_dir.mkdir(parents=True, exist_ok=True)
        
        raycast_config_path = raycast_dir / "mcp_servers.json"
        
        # 读取现有配置或创建新的
        if raycast_config_path.exists():
            with open(raycast_config_path, 'r') as f:
                raycast_config = json.load(f)
        else:
            raycast_config = {"mcpServers": {}}
        
        # 添加artifacts配置
        artifacts_script = Path("artifacts_mcp.py").absolute()
        raycast_config["mcpServers"]["artifacts"] = {
            "command": "python",
            "args": [str(artifacts_script)],
            "env": {}
        }
        
        with open(raycast_config_path, 'w') as f:
            json.dump(raycast_config, f, indent=2)
        
        print(f"✅ Raycast配置完成: {raycast_config_path}")
        print("请重启Raycast使配置生效")

def setup_cursor():
    """配置Cursor"""
    if input("\n配置Cursor? (y/N): ").lower() == 'y':
        cursor_dir = Path.home() / ".cursor"
        cursor_dir.mkdir(parents=True, exist_ok=True)
        
        cursor_config_path = cursor_dir / "mcp_servers.json"
        
        artifacts_script = Path("artifacts_mcp.py").absolute()
        cursor_config = {
            "mcp": {
                "servers": {
                    "artifacts": {
                        "command": "python",
                        "args": [str(artifacts_script)],
                        "env": {}
                    }
                }
            }
        }
        
        with open(cursor_config_path, 'w') as f:
            json.dump(cursor_config, f, indent=2)
        
        print(f"✅ Cursor配置完成: {cursor_config_path}")

def create_scripts():
    """创建启动脚本"""
    
    # 创建启动脚本
    start_script = Path("start.sh")
    with open(start_script, 'w') as f:
        f.write("""#!/bin/bash
# 启动Artifacts MCP Server

echo "🚀 启动 Artifacts MCP Server..."

# 检查配置
if [ ! -f "config.json" ]; then
    echo "❌ 配置文件不存在，运行setup.sh进行配置"
    exit 1
fi

# 启动服务器
python artifacts_mcp.py
""")
    start_script.chmod(0o755)
    
    # 创建设置脚本
    setup_script = Path("setup.sh")
    with open(setup_script, 'w') as f:
        f.write("""#!/bin/bash
# 设置和配置Artifacts MCP Server

echo "🔧 配置 Artifacts MCP Server..."

python artifacts_mcp.py --setup
""")
    setup_script.chmod(0o755)
    
    print("✅ 创建了启动脚本: start.sh, setup.sh")

def main():
    """主函数"""
    print("🚀 Artifacts MCP Server 一键安装")
    print("="*50)
    
    # 检查Python版本
    check_python()
    
    # 安装UV (可选)
    if input("\n安装UV包管理器? (推荐) (Y/n): ").lower() != 'n':
        install_uv()
    
    # 安装依赖
    install_dependencies()
    
    # 创建配置
    setup_config()
    
    # 配置AI客户端
    setup_raycast()
    setup_cursor()
    
    # 创建便捷脚本
    create_scripts()
    
    print("\n" + "="*50)
    print("🎉 安装完成！")
    print("\n下一步:")
    print("1. 如果跳过了API key配置，请编辑config.json文件")
    print("2. 启动服务器: python artifacts_mcp.py")
    print("3. 或使用便捷脚本: ./start.sh")
    print("4. 重新配置: ./setup.sh")
    print("\n📖 更多信息请查看README.md")

if __name__ == "__main__":
    main()