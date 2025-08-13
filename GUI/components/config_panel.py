import streamlit as st
from typing import Dict, Any
from config.settings import save_config

class ConfigPanel:
    """配置面板组件"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def render(self):
        """渲染配置面板"""
        # 模型选择
        st.markdown("**选择模型:**")
        selected_model = st.selectbox(
            "模型",
            options=list(self.config["models"].keys()),
            format_func=lambda x: self.config["models"][x],
            key="model_selector"
        )
        
        # API密钥配置
        st.markdown("**API配置:**")
        
        # OpenAI API
        if "openai" in self.config["api_keys"]:
            openai_key = st.text_input(
                "OpenAI API Key",
                value=self.config["api_keys"]["openai"],
                type="password",
                help="输入您的OpenAI API密钥",
                key="openai_key"
            )
            self.config["api_keys"]["openai"] = openai_key
        
        # Anthropic API
        if "anthropic" in self.config["api_keys"]:
            anthropic_key = st.text_input(
                "Anthropic API Key",
                value=self.config["api_keys"]["anthropic"],
                type="password",
                help="输入您的Anthropic API密钥",
                key="anthropic_key"
            )
            self.config["api_keys"]["anthropic"] = anthropic_key
        
        # Google API
        if "google" in self.config["api_keys"]:
            google_key = st.text_input(
                "Google API Key",
                value=self.config["api_keys"]["google"],
                type="password",
                help="输入您的Google API密钥",
                key="google_key"
            )
            self.config["api_keys"]["google"] = google_key
        
        # 更新选中的模型
        self.config["selected_model"] = selected_model
        
        # 保存配置按钮
        if st.button("💾 保存配置", key="save_config"):
            save_config(self.config)
            st.success("配置已保存！")
        
        # 显示当前配置信息
        st.markdown("---")
        st.markdown("**当前配置:**")
        st.info(f"选中模型: {self.config['models'][selected_model]}")
        
        # 显示API密钥状态
        api_status = []
        for provider, key in self.config["api_keys"].items():
            status = "✅ 已配置" if key else "❌ 未配置"
            api_status.append(f"{provider.title()}: {status}")
        
        for status in api_status:
            st.text(status)
