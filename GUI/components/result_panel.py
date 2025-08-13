import streamlit as st
from typing import Dict, Any

class ResultPanel:
    """结果显示面板组件"""
    
    def __init__(self):
        pass
    
    def render(self):
        """渲染结果显示面板"""
        st.markdown("**📤 响应结果:**")
        
        # 检查是否有当前请求
        if "current_prompt" in st.session_state:
            # 显示请求信息
            with st.expander("📋 请求详情", expanded=True):
                st.markdown(f"**提示词:** {st.session_state.current_prompt}")
                
                if "current_params" in st.session_state:
                    params = st.session_state.current_params
                    st.markdown("**参数配置:**")
                    param_text = f"""
                    - Temperature: {params['temperature']}
                    - Max Tokens: {params['max_tokens']}
                    - Top P: {params['top_p']}
                    - Frequency Penalty: {params['frequency_penalty']}
                    """
                    st.code(param_text, language="text")
            
            # 模拟结果显示（将来会替换为实际的LLM响应）
            st.markdown("**🤖 AI响应:**")
            
            # 模拟响应内容
            mock_response = self._generate_mock_response(st.session_state.current_prompt)
            
            # 响应显示区域
            response_container = st.container()
            with response_container:
                st.markdown(mock_response)
                
                # 响应操作按钮
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if st.button("📋 复制", key="copy_response"):
                        st.success("已复制到剪贴板！")
                
                with col2:
                    if st.button("💾 保存", key="save_response"):
                        st.success("响应已保存！")
                
                with col3:
                    if st.button("🔄 重新生成", key="regenerate"):
                        st.info("重新生成中...")
                
                with col4:
                    if st.button("⭐ 收藏", key="favorite"):
                        st.success("已添加到收藏！")
            
            # 历史记录
            if "response_history" not in st.session_state:
                st.session_state.response_history = []
            
            # 添加到历史记录
            if "current_prompt" in st.session_state:
                history_item = {
                    "prompt": st.session_state.current_prompt,
                    "response": mock_response,
                    "timestamp": "刚刚"
                }
                if history_item not in st.session_state.response_history:
                    st.session_state.response_history.append(history_item)
            
            # 显示历史记录
            if st.session_state.response_history:
                with st.expander("📚 历史记录"):
                    for i, item in enumerate(reversed(st.session_state.response_history[-5:])):  # 只显示最近5条
                        st.markdown(f"**{item['timestamp']}**")
                        st.markdown(f"**Q:** {item['prompt'][:50]}...")
                        st.markdown(f"**A:** {item['response'][:100]}...")
                        st.markdown("---")
        else:
            # 没有请求时的提示
            st.info("👆 请在左侧输入提示词并发送请求")
    
    def _generate_mock_response(self, prompt: str) -> str:
        """生成模拟响应（将来会替换为实际的LLM调用）"""
        if "你好" in prompt or "介绍" in prompt:
            return """
            👋 你好！我是一个AI助手，很高兴为您服务。
            
            我可以帮助您：
            - 回答问题
            - 编写代码
            - 分析文本
            - 提供建议
            
            请告诉我您需要什么帮助！
            """
        elif "人工智能" in prompt or "AI" in prompt:
            return """
            🤖 人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，旨在创建能够执行通常需要人类智能的任务的系统。
            
            **主要特点：**
            - 学习能力：从数据中学习模式
            - 推理能力：基于逻辑进行推理
            - 感知能力：理解图像、语音等
            - 自然语言处理：理解和生成人类语言
            
            **应用领域：**
            - 医疗诊断
            - 自动驾驶
            - 智能助手
            - 金融分析
            """
        elif "Python" in prompt or "代码" in prompt:
            return """
            🐍 这是一个计算斐波那契数列的Python函数：
            
            ```python
            def fibonacci(n):
                \"\"\"
                计算斐波那契数列的第n项
                \"\"\"
                if n <= 1:
                    return n
                else:
                    return fibonacci(n-1) + fibonacci(n-2)
            
            # 使用示例
            for i in range(10):
                print(f"F({i}) = {fibonacci(i)}")
            ```
            
            **输出结果：**
            F(0) = 0
            F(1) = 1
            F(2) = 1
            F(3) = 2
            F(4) = 3
            F(5) = 5
            F(6) = 8
            F(7) = 13
            F(8) = 21
            F(9) = 34
            """
        else:
            return """
            🤔 我理解您的问题，但目前这是一个演示界面，还没有连接到实际的LLM服务。
            
            在完整版本中，我会：
            1. 连接到您选择的AI模型
            2. 使用您提供的API密钥
            3. 根据您的参数设置生成响应
            4. 提供完整的对话体验
            
            请期待后续的功能实现！
            """
