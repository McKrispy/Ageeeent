"""
页面头部组件 - 聊天机器人
"""
import streamlit as st

def render_header():
    """渲染页面头部 - 聊天机器人"""
    st.title("🤖 AI 聊天机器人")
    st.markdown("---")
    
    # 显示系统状态
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("机器人状态", "在线", delta="正常")
    
    with col2:
        st.metric("对话次数", "0", delta="0")
    
    with col3:
        st.metric("响应时间", "0ms", delta="0ms")
