"""
主内容区域组件 - 聊天界面
"""
import streamlit as st
import time
from GUI.utils.workflow import AsyncWorkflowManager

def render_question(question_data: dict, question_index: int) -> str:
    """渲染单个问题并返回用户答案"""
    st.markdown(f"**{question_index + 1}. {question_data['question']}**")
    
    question_type = question_data.get('type', 'text')
    
    if question_type == 'single_choice':
        options = question_data.get('options', [])
        if options:
            answer = st.radio(
                "选择答案:",
                options,
                key=f"q_{question_index}",
                label_visibility="collapsed"
            )
            return answer
        else:
            st.warning("该问题缺少选项")
            return ""
    
    elif question_type == 'multiple_choice':
        options = question_data.get('options', [])
        if options:
            answer = st.multiselect(
                "选择答案（可多选）:",
                options,
                key=f"q_{question_index}",
                label_visibility="collapsed"
            )
            return ", ".join(answer) if answer else ""
        else:
            st.warning("该问题缺少选项")
            return ""
    
    elif question_type == 'text':
        placeholder = question_data.get('placeholder', '请在此输入您的答案...')
        answer = st.text_area(
            "您的答案:",
            placeholder=placeholder,
            height=100,
            key=f"q_{question_index}",
            label_visibility="collapsed"
        )
        return answer
    
    else:
        st.warning(f"不支持的问题类型: {question_type}")
        return ""

@st.fragment(run_every="1s")
def render_questionnaire_section(workflow_manager):
    """渲染问卷部分"""
    st.markdown("---")
    st.subheader("问题补充")
    
    # 检查是否正在等待问卷
    if workflow_manager._manage_questionnaire_interaction("check"):
        questionnaire_data = workflow_manager._manage_questionnaire_interaction("get")
        
        if questionnaire_data:
            try:
                # 显示问卷标题和描述
                st.markdown(f"## {questionnaire_data.get('title', '问题补充问卷')}")
                st.markdown(questionnaire_data.get('description', '请根据以下问题提供补充信息：'))
                
                # 创建问卷表单
                with st.form("questionnaire_form"):
                    st.markdown("**请回答以下问题：**")
                    
                    # 存储用户答案
                    user_answers = {}
                    
                    # 渲染每个问题
                    questions = questionnaire_data.get('questions', [])
                    for i, question in enumerate(questions):
                        st.markdown("---")
                        answer = render_question(question, i)
                        user_answers[f"q_{i}"] = {
                            "question": question['question'],
                            "answer": answer,
                            "type": question.get('type', 'text')
                        }
                    
                    # 提交按钮
                    submitted = st.form_submit_button("📤 提交问卷答案", use_container_width=True, type="primary")
                    
                    if submitted:
                        # 验证所有问题都已回答
                        unanswered_questions = []
                        for q_key, q_data in user_answers.items():
                            if not q_data['answer'].strip():
                                unanswered_questions.append(q_data['question'])
                        
                        if unanswered_questions:
                            st.error(f"以下问题尚未回答：\n" + "\n".join([f"• {q}" for q in unanswered_questions]))
                        else:
                            # 构建补充信息
                            supplementary_info = "用户问卷回答：\n\n"
                            for q_key, q_data in user_answers.items():
                                supplementary_info += f"**{q_data['question']}**\n{q_data['answer']}\n\n"
                            
                            # 提交到工作流
                            result = workflow_manager._manage_questionnaire_interaction("submit", supplementary_info)
                            if result == "success":
                                st.success("✅ 问卷答案已提交！工作流将继续执行...")
                                st.rerun()
                            else:
                                st.error("❌ 提交失败，请重试")
            
            except Exception as e:
                st.error(f"渲染问卷时出错: {e}")
                st.json(questionnaire_data)  # 显示原始数据用于调试
    
    else:
        st.info("当前无需填写问卷")

@st.fragment(run_every="1s")
def render_mcp_section(workflow_manager):
    """渲染MCP与工作记忆(WorkingMemory)模块，实时刷新"""
    st.markdown("---")
    st.subheader("🧠 MCP 概览")

    status = workflow_manager.get_status()
    results = status.get("results", {})
    mcp = results.get("mcp")
    working_memory = results.get("working_memory")

    if not mcp:
        st.info("暂无 MCP 数据（请先启动工作流）")
        return

    # 顶部关键信息
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("会话ID", getattr(mcp, "session_id", "-")[:12] + "…" if getattr(mcp, "session_id", "") else "-")
    with col_b:
        st.metric("循环计数", getattr(mcp, "global_cycle_count", 0))
    with col_c:
        st.metric("战略计划", len(getattr(mcp, "strategy_plans", []) or []))
    with col_d:
        st.metric("执行命令", len(getattr(mcp, "executable_commands", []) or []))

    # 原始需求与完成需求
    with st.expander("📥 用户需求与完成要求", expanded=True):
        st.markdown("**原始需求**")
        st.write(getattr(mcp, "user_requirements", "-"))

        comp_req = getattr(mcp, "completion_requirement", None)
        if comp_req:
            st.markdown("---")
            st.markdown("**完成要求 CompletionRequirement**")
            st.markdown(f"- 原始输入: {getattr(comp_req, 'original_input', '-')}")
            st.markdown(f"- 补充内容: {getattr(comp_req, 'supplementary_content', '-')}")
            st.markdown(f"- 画像分析: {getattr(comp_req, 'profile_analysis', '-')}")
        else:
            st.caption("尚未生成完成要求")

    # 战略计划列表
    with st.expander("🧭 战略计划 StrategyPlans", expanded=False):
        plans = getattr(mcp, "strategy_plans", []) or []
        if not plans:
            st.caption("暂无战略计划")
        else:
            for idx, sp in enumerate(plans, start=1):
                with st.container(border=True):
                    st.markdown(f"**[{idx}] ID:** {getattr(sp, 'id', '-')}")
                    st.markdown(f"- 已完成: {getattr(sp, 'is_completed', False)}")
                    desc = getattr(sp, "description", {}) or {}
                    st.markdown("- 描述:")
                    st.json(desc)

    # 子目标列表
    with st.expander("🎯 子目标 SubGoals", expanded=False):
        sub_goals = getattr(mcp, "sub_goals", []) or []
        if not sub_goals:
            st.caption("暂无子目标")
        else:
            for idx, sg in enumerate(sub_goals, start=1):
                with st.container(border=True):
                    st.markdown(f"**[{idx}] ID:** {getattr(sg, 'id', '-')}")
                    st.markdown(f"- 父计划: {getattr(sg, 'parent_strategy_plan_id', '-')}")
                    st.markdown(f"- 描述: {getattr(sg, 'description', '-')}")
                    st.markdown(f"- 已完成: {getattr(sg, 'is_completed', False)}")

    # 可执行命令
    with st.expander("🛠️ 可执行命令 ExecutableCommands", expanded=False):
        commands = getattr(mcp, "executable_commands", []) or []
        if not commands:
            st.caption("暂无可执行命令")
        else:
            for idx, ec in enumerate(commands, start=1):
                with st.container(border=True):
                    st.markdown(f"**[{idx}] ID:** {getattr(ec, 'id', '-')}")
                    st.markdown(f"- 父子目标: {getattr(ec, 'parent_sub_goal_id', '-')}")
                    st.markdown(f"- 工具: {getattr(ec, 'tool', '-')}")
                    st.markdown(f"- 已完成: {getattr(ec, 'is_completed', False)}")
                    st.markdown("- 参数:")
                    st.json(getattr(ec, "params", {}) or {})

    # WorkingMemory
    st.markdown("---")
    st.subheader("🗂️ 工作记忆 WorkingMemory")
    if not working_memory or not getattr(working_memory, "data", None):
        st.caption("暂无工作记忆数据")
    else:
        with st.expander("查看工作记忆内容", expanded=False):
            st.json(getattr(working_memory, "data", {}) or {})

@st.fragment(run_every="1s")
def render_workflow_status(workflow_manager):
    """渲染工作流状态"""
    st.markdown("---")
    st.subheader("⚙️ 工作流状态")
    
    workflow_status = workflow_manager.get_status()
    
    # 显示详细状态
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_color = "🟢" if workflow_status["is_running"] else "🔴"
        st.metric("运行状态", f"{status_color} {'运行中' if workflow_status['is_running'] else '已停止'}")
    
    with col2:
        if workflow_status["is_running"]:
            if workflow_manager._manage_questionnaire_interaction("check"):
                st.metric("当前阶段", "⏳ 等待问卷")
            else:
                st.metric("当前阶段", "🟢 执行中")
        else:
            st.metric("当前阶段", "⏸️ 未启动")
    
    with col3:
        results = workflow_status.get("results", {})
        total_items = results.get("strategy_plans", 0) + results.get("sub_goals", 0) + results.get("executable_commands", 0)
        st.metric("生成项目", total_items)

@st.fragment(run_every="1s")
def render_logs_section(workflow_manager):
    """渲染日志部分"""
    st.markdown("---")
    st.subheader("📋 后台日志")
    # 获取工作流状态
    workflow_status = workflow_manager.get_status()
    logger = workflow_status["logger"]
    
    # 显示工作流状态
    status_color = "🟢" if workflow_status["is_running"] else "🔴"
    st.metric("状态", f"{status_color} {'运行中' if workflow_status['is_running'] else '已停止'}")
    
    summary = logger.get_summary()
    st.metric("日志数量", summary["total_logs"])
    
    # 显示最新日志
    logs = logger.get_all_logs()
    if logs:
        st.subheader(f"📋 日志记录 (共 {len(logs)} 条)")
        # 使用 st.expander
        with st.expander("📋 查看日志详情", expanded=False):
            with st.container(height=500):
                for log in logs:
                    timestamp = time.strftime("%H:%M:%S", time.localtime(log["timestamp"]))
                    phase = log.get("phase", "unknown")
                    message = log['message']
                    
                    full_message = f"[{timestamp}] [{phase}] {message}"
                    
                    if log["type"] == "success":
                        st.success(full_message)
                    elif log["type"] == "error":
                        st.error(full_message)
                    elif log["type"] == "warning":
                        st.warning(full_message)
                    else:
                        st.info(full_message)
            
            # 显示日志统计信息
            st.caption(f"共 {len(logs)} 条记录")
            
    else:
        st.info("暂无日志")
    
    # 日志控制
    st.markdown("---")
    col_clear, col_export = st.columns(2)
    
    with col_clear:
        if st.button("🔄 清空日志", use_container_width=True):
            logger.clear_logs()
            
    with col_export:
        st.download_button(label="📥 导出日志",
                data=logger.export_logs("text"),
                file_name=f"workflow_logs_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True)

def render_main_content():
    """渲染主内容区域 - 聊天界面"""
    
    # 初始化会话状态
    if "workflow_manager" not in st.session_state:
        st.session_state.workflow_manager = AsyncWorkflowManager()
    
    workflow_manager = st.session_state.workflow_manager
    
    # 创建两列布局：左侧聊天窗口，右侧日志
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 聊天窗口")
        
        # 聊天记录显示区域
        chat_container = st.container()
        with chat_container:
            if workflow_manager.is_workflow_running():
                if workflow_manager._manage_questionnaire_interaction("check"):
                    st.info("🤔 系统正在等待您完成问题补充...")
                else:
                    st.info("🔄 工作流正在执行中...")
            else:
                st.info("请输入您的需求，系统将为您生成相应的分析计划")
        
        # 聊天输入区域
        st.markdown("---")
        user_input = st.text_input("请输入您的消息...", placeholder="例如：帮我分析2024年人工智能在医疗领域的最新发展趋势...")
        
        # 发送按钮
        col_send1, col_send2 = st.columns([3, 1])
        with col_send1:
            if st.button("🚀 启动工作流", use_container_width=True, type="primary"):
                if user_input.strip():
                    # 启动工作流
                    if workflow_manager.start_workflow(user_input):
                        st.success("✅ 工作流已启动！")
                        st.rerun()
                    else:
                        st.warning("⚠️ 工作流已在运行中")
                else:
                    st.warning("⚠️ 请输入消息内容")
        
        with col_send2:
            if st.button("⏹️ 停止", use_container_width=True):
                workflow_manager.stop_workflow()
                st.success("🛑 工作流已停止")
                st.rerun()
        
        
        # 渲染问卷部分
        render_questionnaire_section(workflow_manager)
        
        # 渲染工作流状态
        render_workflow_status(workflow_manager)
        
        # 渲染 MCP 模块
        render_mcp_section(workflow_manager)
    
    with col2:
        render_logs_section(workflow_manager)
            