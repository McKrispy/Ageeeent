import os
import sys
import subprocess

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_streamlit():
    """检查Streamlit是否安装"""
    try:
        import streamlit
        print("✅ Streamlit已安装")
        return True
    except ImportError:
        print("❌ Streamlit未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "--server.fileWatcherType=poll", "--server.runOnSave=true"])
            print("✅ Streamlit安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ Streamlit安装失败")
            return False

def main():
    """主函数"""
    print("启动聊天机器人...")
    
    if not check_streamlit():
        print("❌ 无法启动应用")
        return
    
    print("🌐 聊天机器人将在浏览器中打开")
    print("📱 按 Ctrl+C 停止应用")
    
    # 启动Streamlit应用
    try:
        os.system("streamlit run GUI/app.py --server.fileWatcherType=poll --server.runOnSave=true")
    except KeyboardInterrupt:
        print("\n应用已停止")

if __name__ == "__main__":
    main()