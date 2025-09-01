"""
Main content area component - Chat interface
"""
import streamlit as st
import time
from GUI.utils.workflow import AsyncWorkflowManager

def render_question(question_data: dict, question_index: int) -> str:
    """Render a single question and return user answer"""
    st.markdown(f"**{question_index + 1}. {question_data['question']}**")
    
    question_type = question_data.get('type', 'text')
    
    if question_type == 'single_choice':
        options = question_data.get('options', [])
        if options:
            answer = st.radio(
                "Select answer:",
                options,
                key=f"q_{question_index}",
                label_visibility="collapsed"
            )
            return answer
        else:
            st.warning("This question is missing options")
            return ""
    
    elif question_type == 'multiple_choice':
        options = question_data.get('options', [])
        if options:
            answer = st.multiselect(
                "Select answers (multiple choice):",
                options,
                key=f"q_{question_index}",
                label_visibility="collapsed"
            )
            return ", ".join(answer) if answer else ""
        else:
            st.warning("This question is missing options")
            return ""
    
    elif question_type == 'text':
        placeholder = question_data.get('placeholder', 'Please enter your answer here...')
        answer = st.text_area(
            "Your answer:",
            placeholder=placeholder,
            height=100,
            key=f"q_{question_index}",
            label_visibility="collapsed"
        )
        return answer
    
    else:
        st.warning(f"Unsupported question type: {question_type}")
        return ""

@st.fragment(run_every="1s")
def render_questionnaire_section(workflow_manager):
    """Render questionnaire section"""
    st.markdown("---")
    st.subheader("Questionnaire")
    
    # Check if waiting for questionnaire
    if workflow_manager._manage_questionnaire_interaction("check"):
        questionnaire_data = workflow_manager._manage_questionnaire_interaction("get")
        
        if questionnaire_data:
            try:
                # Display questionnaire title and description
                st.markdown(f"## {questionnaire_data.get('title', 'Questionnaire')}")
                st.markdown(questionnaire_data.get('description', 'Please provide additional information based on the following questions:'))
                
                # Create questionnaire form
                with st.form("questionnaire_form"):
                    st.markdown("**Please answer the following questions:**")
                    
                    # Store user answers
                    user_answers = {}
                    
                    # Render each question
                    questions = questionnaire_data.get('questions', [])
                    for i, question in enumerate(questions):
                        st.markdown("---")
                        answer = render_question(question, i)
                        user_answers[f"q_{i}"] = {
                            "question": question['question'],
                            "answer": answer,
                            "type": question.get('type', 'text')
                        }
                    
                    # Submit button
                    submitted = st.form_submit_button("📤 Submit Questionnaire", use_container_width=True, type="primary")
                    
                    if submitted:
                        # Validate all questions are answered
                        unanswered_questions = []
                        for q_key, q_data in user_answers.items():
                            if not q_data['answer'].strip():
                                unanswered_questions.append(q_data['question'])
                        
                        if unanswered_questions:
                            st.error(f"The following questions are not answered:\n" + "\n".join([f"• {q}" for q in unanswered_questions]))
                        else:
                            # Build supplementary information
                            supplementary_info = "User questionnaire responses:\n\n"
                            for q_key, q_data in user_answers.items():
                                supplementary_info += f"**{q_data['question']}**\n{q_data['answer']}\n\n"
                            
                            # Submit to workflow
                            result = workflow_manager._manage_questionnaire_interaction("submit", supplementary_info)
                            if result == "success":
                                st.success("✅ Questionnaire submitted! Workflow will continue...")
                                st.rerun()
                            else:
                                st.error("❌ Submission failed, please try again")
            
            except Exception as e:
                st.error(f"Error rendering questionnaire: {e}")
                st.json(questionnaire_data)  # Display raw data for debugging
    
    else:
        st.info("No questionnaire to fill out currently")

@st.fragment(run_every="1s")
def render_mcp_section(workflow_manager):
    """Render MCP and WorkingMemory module with real-time refresh"""
    st.markdown("---")
    st.subheader("🧠 MCP Overview")

    status = workflow_manager.get_status()
    results = status.get("results", {})
    mcp = results.get("mcp")
    working_memory = results.get("working_memory")

    if not mcp:
        st.info("No MCP data available (please start workflow first)")
        return

    # Top key information
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        st.metric("Session ID", getattr(mcp, "session_id", "-")[:12] + "…" if getattr(mcp, "session_id", "") else "-")
    with col_b:
        st.metric("Cycle Count", getattr(mcp, "global_cycle_count", 0))
    with col_c:
        st.metric("Strategy Plans", len(getattr(mcp, "strategy_plans", []) or []))
    with col_d:
        st.metric("Executable Commands", len(getattr(mcp, "executable_commands", []) or []))

    # Original requirements and completion requirements
    with st.expander("📥 User Requirements & Completion Requirements", expanded=True):
        st.markdown("**Original Requirements**")
        st.write(getattr(mcp, "user_requirements", "-"))

        comp_req = getattr(mcp, "completion_requirement", None)
        if comp_req:
            st.markdown("---")
            st.markdown("**Completion Requirements**")
            st.markdown(f"- Original Input: {getattr(comp_req, 'original_input', '-')}")
            st.markdown(f"- Supplementary Content: {getattr(comp_req, 'supplementary_content', '-')}")
            st.markdown(f"- Profile Analysis: {getattr(comp_req, 'profile_analysis', '-')}")
        else:
            st.caption("Completion requirements not generated yet")

    # Strategy plans list
    with st.expander("🧭 Strategy Plans", expanded=False):
        plans = getattr(mcp, "strategy_plans", []) or []
        if not plans:
            st.caption("No strategy plans available")
        else:
            for idx, sp in enumerate(plans, start=1):
                with st.container(border=True):
                    st.markdown(f"**[{idx}] ID:** {getattr(sp, 'id', '-')}")
                    st.markdown(f"- Completed: {getattr(sp, 'is_completed', False)}")
                    desc = getattr(sp, "description", {}) or {}
                    st.markdown("- Description:")
                    st.json(desc)

    # Sub-goals list
    with st.expander("🎯 Sub Goals", expanded=False):
        sub_goals = getattr(mcp, "sub_goals", []) or []
        if not sub_goals:
            st.caption("No sub-goals available")
        else:
            for idx, sg in enumerate(sub_goals, start=1):
                with st.container(border=True):
                    st.markdown(f"**[{idx}] ID:** {getattr(sg, 'id', '-')}")
                    st.markdown(f"- Parent Plan: {getattr(sg, 'parent_strategy_plan_id', '-')}")
                    st.markdown(f"- Description: {getattr(sg, 'description', '-')}")
                    st.markdown(f"- Completed: {getattr(sg, 'is_completed', False)}")

    # Executable commands
    with st.expander("🛠️ Executable Commands", expanded=False):
        commands = getattr(mcp, "executable_commands", []) or []
        if not commands:
            st.caption("No executable commands available")
        else:
            for idx, ec in enumerate(commands, start=1):
                with st.container(border=True):
                    st.markdown(f"**[{idx}] ID:** {getattr(ec, 'id', '-')}")
                    st.markdown(f"- Parent Sub-goal: {getattr(ec, 'parent_sub_goal_id', '-')}")
                    st.markdown(f"- Tool: {getattr(ec, 'tool', '-')}")
                    st.markdown(f"- Completed: {getattr(ec, 'is_completed', False)}")
                    st.markdown("- Parameters:")
                    st.json(getattr(ec, "params", {}) or {})

    # WorkingMemory
    st.markdown("---")
    st.subheader("🗂️ Working Memory")
    if not working_memory or not getattr(working_memory, "data", None):
        st.caption("No working memory data available")
    else:
        with st.expander("View Working Memory Content", expanded=False):
            st.json(getattr(working_memory, "data", {}) or {})

@st.fragment(run_every="1s")
def render_workflow_status(workflow_manager):
    """Render workflow status"""
    st.markdown("---")
    st.subheader("⚙️ Workflow Status")
    
    workflow_status = workflow_manager.get_status()
    
    # Display detailed status
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_color = "🟢" if workflow_status["is_running"] else "🔴"
        st.metric("Running Status", f"{status_color} {'Running' if workflow_status['is_running'] else 'Stopped'}")
    
    with col2:
        if workflow_status["is_running"]:
            if workflow_manager._manage_questionnaire_interaction("check"):
                st.metric("Current Phase", "⏳ Waiting for Questionnaire")
            else:
                st.metric("Current Phase", "🟢 Executing")
        else:
            st.metric("Current Phase", "⏸️ Not Started")
    
    with col3:
        results = workflow_status.get("results", {})
        total_items = results.get("strategy_plans", 0) + results.get("sub_goals", 0) + results.get("executable_commands", 0)
        st.metric("Generated Items", total_items)

@st.fragment(run_every="1s")
def render_logs_section(workflow_manager):
    """Render logs section"""
    st.markdown("---")
    st.subheader("📋 Background Logs")
    # Get workflow status
    workflow_status = workflow_manager.get_status()
    logger = workflow_status["logger"]
    
    # Display workflow status
    status_color = "🟢" if workflow_status["is_running"] else "🔴"
    st.metric("Status", f"{status_color} {'Running' if workflow_status['is_running'] else 'Stopped'}")
    
    summary = logger.get_summary()
    st.metric("Log Count", summary["total_logs"])
    
    # Display latest logs
    logs = logger.get_all_logs()
    if logs:
        st.subheader(f"📋 Log Records (Total: {len(logs)})")
        # Use st.expander
        with st.expander("📋 View Log Details", expanded=False):
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
            
            # Display log statistics
            st.caption(f"Total: {len(logs)} records")
            
    else:
        st.info("No logs available")
    
    # Log controls
    st.markdown("---")
    col_clear, col_export = st.columns(2)
    
    with col_clear:
        if st.button("🔄 Clear Logs", use_container_width=True):
            logger.clear_logs()
            
    with col_export:
        st.download_button(label="📥 Export Logs",
                data=logger.export_logs("text"),
                file_name=f"workflow_logs_{int(time.time())}.txt",
                mime="text/plain",
                use_container_width=True)

def render_main_content():
    """Render main content area - Chat interface"""
    
    # Initialize session state
    if "workflow_manager" not in st.session_state:
        st.session_state.workflow_manager = AsyncWorkflowManager()
    
    workflow_manager = st.session_state.workflow_manager
    
    # Create two-column layout: left chat window, right logs
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat Window")
        
        # Chat record display area
        chat_container = st.container()
        with chat_container:
            if workflow_manager.is_workflow_running():
                if workflow_manager._manage_questionnaire_interaction("check"):
                    st.info("🤔 System is waiting for you to complete the questionnaire...")
                else:
                    st.info("🔄 Workflow is executing...")
            else:
                st.info("Please enter your requirements, the system will generate corresponding analysis plans")
        
        # Chat input area
        st.markdown("---")
        user_input = st.text_input("Please enter your message...", placeholder="For example: Help me analyze the latest development trends of artificial intelligence in the medical field in 2024...")
        
        # Send buttons
        col_send1, col_send2 = st.columns([3, 1])
        with col_send1:
            if st.button("🚀 Start Workflow", use_container_width=True, type="primary"):
                if user_input.strip():
                    # Start workflow
                    if workflow_manager.start_workflow(user_input):
                        st.success("✅ Workflow started!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Workflow is already running")
                else:
                    st.warning("⚠️ Please enter message content")
        
        with col_send2:
            if st.button("⏹️ Stop", use_container_width=True):
                workflow_manager.stop_workflow()
                st.success("🛑 Workflow stopped")
                st.rerun()
        
        
        # Render questionnaire section
        render_questionnaire_section(workflow_manager)
        
        # Render workflow status
        render_workflow_status(workflow_manager)
        
        # Render MCP module
        render_mcp_section(workflow_manager)
    
    with col2:
        render_logs_section(workflow_manager)
            