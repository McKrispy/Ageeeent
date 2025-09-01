import streamlit as st

def render_header():
    st.title("🤖 AI Chatbot")
    st.markdown("---")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Bot Status", "Online", delta="Normal")
    
    with col2:
        st.metric("Run Cycles", "0", delta="0")
    
    with col3:
        st.metric("Response Time", "0s", delta="0s")

    with col4:
        st.metric("Total Time", "0s", delta="0s")