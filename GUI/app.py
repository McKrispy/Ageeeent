import streamlit as st
from components.llm_interface import LLMInterface
from config.settings import load_config, save_config
from utils.helpers import setup_page_config

def main():
    """主应用入口"""
    # 设置页面配置
    setup_page_config()
    
    # 加载配置
    config = load_config()
    
    # 页面标题
    st.title("🤖 LLM 测试界面")
    st.markdown("---")
    
    # 创建LLM接口组件
    llm_interface = LLMInterface(config)
    llm_interface.render()

if __name__ == "__main__":
    main()
