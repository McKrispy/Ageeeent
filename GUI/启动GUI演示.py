#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI演示启动脚本
"""

import os
import sys
import subprocess
import time

def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖...")
    
    required_packages = [
        'streamlit',
        'redis', 
        'openai',
        'pydantic'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - 未安装")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  缺少依赖: {', '.join(missing)}")
        print("请运行: pip install " + " ".join(missing))
        return False
    
    return True

def check_redis():
    """检查Redis连接"""
    print("\n🔍 检查Redis连接...")
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=1)
        client.ping()
        print("✅ Redis连接正常")
        return True
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        print("请确保Redis服务正在运行: redis-server")
        return False

def start_gui():
    """启动GUI"""
    print("\n🚀 启动GUI界面...")
    
    gui_dir = os.path.join(os.path.dirname(__file__), 'GUI')
    app_file = os.path.join(gui_dir, 'app.py')
    
    if not os.path.exists(app_file):
        print(f"❌ 找不到GUI应用文件: {app_file}")
        return False
    
    # 设置环境
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.dirname(__file__)
    
    try:
        # 启动Streamlit
        cmd = ['streamlit', 'run', app_file, '--server.port', '8501']
        print(f"执行命令: {' '.join(cmd)}")
        print("GUI将在浏览器中打开: http://localhost:8501")
        
        subprocess.run(cmd, cwd=gui_dir, env=env)
        
    except FileNotFoundError:
        print("❌ 找不到streamlit命令，请安装: pip install streamlit")
        return False
    except KeyboardInterrupt:
        print("\n👋 用户中断，退出GUI")
        return True
    except Exception as e:
        print(f"❌ 启动GUI失败: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("🤖 智能Agent工作平台 - GUI启动器")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查Redis（可选）
    redis_ok = check_redis()
    if not redis_ok:
        print("⚠️  Redis未连接，部分功能可能不可用")
        response = input("是否继续启动GUI？(y/N): ")
        if response.lower() != 'y':
            return
    
    # 环境变量提示
    print("\n🔧 环境变量检查...")
    env_vars = ['OPENAI_API_KEY', 'OPENAI_BASE_URL']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 10}...{value[-4:]}")
        else:
            print(f"⚠️  {var}: 未设置")
    
    print("\n📖 功能介绍:")
    print("1. 🔄 Agent工作流 - 创建和管理智能任务")
    print("2. 💬 LLM测试 - 测试语言模型接口")  
    print("3. 📊 数据浏览 - 浏览工作流数据和历史")
    
    print("\n" + "=" * 60)
    input("按Enter键启动GUI界面...")
    
    # 启动GUI
    start_gui()

if __name__ == "__main__":
    main()