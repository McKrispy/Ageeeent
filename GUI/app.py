"""
AI 聊天机器人 - 主应用
"""
import os
import sys
import streamlit as st

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from GUI.config.llm_config import LLMConfig
from GUI.components.header import render_header
from GUI.components.sidebar import render_sidebar
from GUI.components.main_content import render_main_content

# 页面配置
st.set_page_config(
    page_title="AI 聊天机器人",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = True
    st.session_state.current_llm_provider = "OpenAI"
    st.session_state.debug_mode = False

def main():
    """主函数"""
    # 渲染页面头部
    render_header()
    
    # 渲染侧边栏
    render_sidebar()
    
    # 渲染主内容
    render_main_content()
    
    # 页面底部
    st.markdown("---")
    st.markdown(
        "💡 **提示**: 这是一个AI聊天机器人的演示界面，所有功能都处于待实现状态。"
    )

if __name__ == "__main__":
    main()