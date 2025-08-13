import streamlit as st
from typing import Dict, Any

class PromptPanel:
    """提示词输入面板组件"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def render(self):
        """渲染提示词输入面板"""
        # 提示词输入区域
        st.markdown("**输入提示词:**")
        
        # 快速提示词选择
        if "default_prompts" in self.config:
            st.markdown("*快速选择提示词:*")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("👋 问候", key="prompt_greeting"):
                    st.session_state.selected_prompt = self.config["default_prompts"][0]
            
            with col2:
                if st.button("🤖 AI介绍", key="prompt_ai"):
                    st.session_state.selected_prompt = self.config["default_prompts"][1]
            
            with col3:
                if st.button("🐍 Python代码", key="prompt_python"):
                    st.session_state.selected_prompt = self.config["default_prompts"][2]
        
        # 提示词输入框
        prompt_input = st.text_area(
            "提示词",
            value=st.session_state.get("selected_prompt", ""),
            height=120,
            placeholder="请输入您的提示词...",
            help="在这里输入您想要测试的提示词",
            key="prompt_input"
        )
        
        # 清空快速选择的提示词
        if "selected_prompt" in st.session_state:
            del st.session_state.selected_prompt
        
        # 参数配置
        with st.expander("🔧 高级参数"):
            col1, col2 = st.columns(2)
            
            with col1:
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=2.0,
                    value=0.7,
                    step=0.1,
                    help="控制输出的随机性，值越高越随机"
                )
                
                max_tokens = st.number_input(
                    "最大Token数",
                    min_value=1,
                    max_value=4000,
                    value=1000,
                    help="限制输出的最大Token数量"
                )
            
            with col2:
                top_p = st.slider(
                    "Top P",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.9,
                    step=0.1,
                    help="控制词汇选择的多样性"
                )
                
                frequency_penalty = st.slider(
                    "频率惩罚",
                    min_value=-2.0,
                    max_value=2.0,
                    value=0.0,
                    step=0.1,
                    help="减少重复内容的生成"
                )
        
        # 发送按钮
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("🚀 发送请求", type="primary", key="send_request"):
                if prompt_input.strip():
                    # 这里将来会实现实际的LLM调用
                    st.session_state.current_prompt = prompt_input
                    st.session_state.current_params = {
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "top_p": top_p,
                        "frequency_penalty": frequency_penalty
                    }
                    st.success("请求已发送！")
                else:
                    st.error("请输入提示词！")
        
        # 清空按钮
        with col3:
            if st.button("🗑️ 清空", key="clear_prompt"):
                st.session_state.prompt_input = ""
                st.rerun()
        
        # 显示当前输入
        if prompt_input.strip():
            st.markdown("**当前输入:**")
            st.info(prompt_input)
