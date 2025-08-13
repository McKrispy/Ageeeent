import streamlit as st
from typing import Dict, Any
from .config_panel import ConfigPanel
from .prompt_panel import PromptPanel
from .result_panel import ResultPanel

class LLMInterface:
    """LLM测试界面主组件"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.config_panel = ConfigPanel(config)
        self.prompt_panel = PromptPanel(config)
        self.result_panel = ResultPanel()
    
    def render(self):
        """渲染整个界面"""
        # 创建两列布局
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("⚙️ 配置设置")
            self.config_panel.render()
        
        with col2:
            st.subheader("💬 对话界面")
            self.prompt_panel.render()
            self.result_panel.render()
