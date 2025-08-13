#!/usr/bin/env python3
"""
LLM测试界面启动脚本
"""

import os
import sys
import subprocess
import streamlit.web.cli as stcli

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        print("✅ Streamlit已安装")
        return True
    except ImportError:
        print("❌ Streamlit未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败")
            return False

def main():
    """主函数"""
    print("🚀 启动LLM测试界面...")
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 无法启动应用，请手动安装依赖")
        return
    
    # 设置环境变量
    os.environ["STREAMLIT_SERVER_PORT"] = "8501"
    os.environ["STREAMLIT_SERVER_ADDRESS"] = "localhost"
    
    print("🌐 应用将在 http://localhost:8501 启动")
    print("📱 按 Ctrl+C 停止应用")
    
    # 启动Streamlit应用
    try:
        sys.argv = ["streamlit", "run", "app.py", "--server.port=8501"]
        sys.exit(stcli.main())
    except KeyboardInterrupt:
        print("\n👋 应用已停止")

if __name__ == "__main__":
    main()
