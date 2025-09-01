import os
import sys
import streamlit as st

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from GUI.components.header import render_header
from GUI.components.sidebar import render_sidebar
from GUI.components.main_content import render_main_content

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "app_initialized" not in st.session_state:
    st.session_state.app_initialized = True
    st.session_state.current_llm_provider = "OpenAI"
    st.session_state.debug_mode = False

def main():
    render_header()
    render_sidebar()
    render_main_content()
    
    st.markdown("---")
    st.markdown(
        "💡 **Note**: This is a demo interface for an AI chatbot, some features are pending implementation."
    )

if __name__ == "__main__":
    main()