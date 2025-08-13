import streamlit as st

def setup_page_config():
    """设置页面配置"""
    st.set_page_config(
        page_title="LLM 测试界面",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 自定义CSS样式
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .config-panel {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    
    .prompt-panel {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
    }
    
    .result-panel {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin-top: 1rem;
    }
    
    .stButton > button {
        width: 100%;
        margin: 0.25rem 0;
    }
    
    .stTextInput > div > div > input {
        border-radius: 0.5rem;
    }
    
    .stTextArea > div > div > textarea {
        border-radius: 0.5rem;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 0.5rem;
    }
    
    .stSlider > div > div > div > div > div > div {
        border-radius: 0.5rem;
    }
    
    .stNumberInput > div > div > input {
        border-radius: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

def display_welcome_message():
    """显示欢迎信息"""
    st.markdown("""
    <div class="main-header">
        🤖 LLM 测试界面
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **欢迎使用LLM测试界面！** 🎉
    
    这个界面可以帮助您：
    - 🎯 测试不同的AI模型
    - 🔑 配置API密钥
    - 💬 输入提示词
    - 📊 查看响应结果
    - ⚙️ 调整生成参数
    
    **使用说明：**
    1. 在左侧配置面板中选择模型和输入API密钥
    2. 在右侧输入您想要测试的提示词
    3. 调整生成参数（可选）
    4. 点击发送请求查看结果
    
    ---
    """)

def create_sidebar():
    """创建侧边栏"""
    with st.sidebar:
        st.title("🔧 工具面板")
        
        st.markdown("### 快速操作")
        
        if st.button("🔄 刷新页面"):
            st.rerun()
        
        if st.button("📊 查看统计"):
            st.info("统计功能开发中...")
        
        if st.button("⚙️ 高级设置"):
            st.info("高级设置功能开发中...")
        
        st.markdown("---")
        
        st.markdown("### 帮助信息")
        st.markdown("""
        **支持的模型：**
        - OpenAI: GPT-4, GPT-3.5
        - Anthropic: Claude 3
        - Google: Gemini Pro
        
        **参数说明：**
        - Temperature: 控制随机性
        - Max Tokens: 最大输出长度
        - Top P: 词汇选择多样性
        - Frequency Penalty: 减少重复
        """)
        
        st.markdown("---")
        
        st.markdown("### 版本信息")
        st.caption("LLM测试界面 v1.0.0")
        st.caption("基于Streamlit构建")
