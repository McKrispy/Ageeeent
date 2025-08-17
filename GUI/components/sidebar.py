"""
侧边栏组件 - 聊天机器人配置
"""
import streamlit as st
from utils.config import LLMConfig, DBConfig

def render_sidebar():

    openai_config = LLMConfig.get_openai_config()
    google_config = LLMConfig.get_google_config()
    anthropic_config = LLMConfig.get_anthropic_config()
    general_config = LLMConfig.get_general_config()

    openai_model_list = ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "gpt-5"]
    google_model_list = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.5-pro-latest", "gemini-1.5-pro-latest-001"]
    anthropic_model_list = ["claude-3-5-sonnet-20240620", "claude-3-5-sonnet-20240620-v1", "claude-3-5-sonnet-20240620-v2", "claude-3-5-sonnet-20240620-v3"]

    provider_list = ["OpenAI", "Google", "Anthropic"]
    """渲染侧边栏 - 聊天机器人配置"""
    with st.sidebar:
        st.header("⚙️ 机器人配置")
        
        # LLM模型选择
        st.subheader("🤖 AI模型")
        selected_provider = st.selectbox(
            "选择AI提供商",
            provider_list,
            index=provider_list.index(general_config['selected_provider'])
        )
        
        # 模型参数配置
        st.subheader("🔧 模型参数")
        openai_model = st.selectbox("OpenAI Model", openai_model_list, index = openai_model_list.index(openai_config['model']))
        google_model = st.selectbox("Google Model", google_model_list, index = google_model_list.index(google_config['model']))
        anthropic_model = st.selectbox("Anthropic Model", anthropic_model_list, index = anthropic_model_list.index(anthropic_config['model']))
        
        openai_base_url = st.text_input("OpenAI Base URL", value="https://api.openai.com/v1")
        google_base_url = st.text_input("Google Base URL", value="https://api.google.com/v1")
        anthropic_base_url = st.text_input("Anthropic Base URL", value="https://api.anthropic.com/v1")

        temperature = st.slider("Temperature", 0.0, 1.0, float(general_config['temperature']), 0.1)
        max_tokens = st.slider("Max Tokens", 100, 8000, int(general_config['max_tokens']), 100)
        
        # 操作按钮
        st.subheader("🔄 操作")
        if st.button("保存配置"):
            LLMConfig.update_general_config(selected_provider=selected_provider)
            LLMConfig.update_openai_config(model=openai_model, base_url=openai_base_url)
            LLMConfig.update_google_config(model=google_model, base_url=google_base_url)
            LLMConfig.update_anthropic_config(model=anthropic_model, base_url=anthropic_base_url)
            LLMConfig.update_general_config(temperature=temperature, max_tokens=max_tokens)
            st.success("配置已保存")
        
        if st.button("清空聊天记录"):
            st.info("清空功能待实现")
        
        # 底部信息
        st.markdown("---")
        st.markdown("**版本**: v1.0.0")
