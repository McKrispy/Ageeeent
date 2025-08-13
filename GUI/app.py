import streamlit as st
from components.llm_interface import LLMInterface
from components.workflow_panel import WorkflowPanel
from config.settings import load_config, save_config
from utils.helpers import setup_page_config

def main():
    """主应用入口"""
    # 设置页面配置
    setup_page_config()
    
    # 加载配置
    config = load_config()
    
    # 页面标题
    st.title("🤖 智能Agent工作平台")
    st.markdown("---")
    
    # 创建选项卡
    tab1, tab2, tab3 = st.tabs(["🔄 Agent工作流", "💬 LLM测试", "📊 数据浏览"])
    
    with tab1:
        # 工作流管理界面
        workflow_panel = WorkflowPanel()
        workflow_panel.render()
    
    with tab2:
        # LLM测试界面
        llm_interface = LLMInterface(config)
        llm_interface.render()
    
    with tab3:
        # 数据浏览界面
        data_browser = DataBrowser()
        data_browser.render()

if __name__ == "__main__":
    main()
