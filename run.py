import os
import sys
import subprocess

def check_streamlit():
    try:
        import streamlit
        print("✅ Streamlit is installed")
        return True
    except ImportError:
        print("❌ Streamlit not installed, installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "--server.fileWatcherType=poll", "--server.runOnSave=true"])
            print("✅ Streamlit installation completed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Streamlit installation failed")
            return False

def main():
    print("Starting chatbot...")
    
    if not check_streamlit():
        print("❌ Cannot start application")
        return
    
    print("🌐 Chatbot will open in browser")
    print("📱 Press Ctrl+C to stop application")
    
    try:
        os.system("streamlit run GUI/app.py --server.fileWatcherType=poll --server.runOnSave=true")
    except KeyboardInterrupt:
        print("\nApplication stopped")

if __name__ == "__main__":
    main()