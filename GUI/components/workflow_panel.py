# -*- coding: utf-8 -*-
"""
工作流管理面板组件
"""
import streamlit as st
import time
from typing import Dict, Any
from ..services.workflow_service import workflow_service, WorkflowStatus

class WorkflowPanel:
    """工作流管理面板"""
    
    def __init__(self):
        self.service = workflow_service
        if 'workflow_session_id' not in st.session_state:
            st.session_state.workflow_session_id = None
        if 'workflow_status' not in st.session_state:
            st.session_state.workflow_status = WorkflowStatus.IDLE
    
    def render(self):
        """渲染工作流面板"""
        st.subheader("🔄 Agent 工作流")
        
        # 工作流输入区域
        with st.container():
            st.markdown("### 任务配置")
            
            user_requirements = st.text_area(
                "请描述您的需求：",
                placeholder="例如：请帮我研究人工智能在医疗领域的最新应用，并总结前3个最重要的发现...",
                height=100,
                key="workflow_requirements"
            )
            
            supplementary_info = st.text_area(
                "补充信息（可选）：",
                placeholder="提供任何有助于理解您需求的额外信息...",
                height=80,
                key="workflow_supplementary"
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("🚀 启动工作流", disabled=not user_requirements.strip()):
                    if user_requirements.strip():
                        session_id = self.service.create_session(user_requirements)
                        if self.service.start_workflow(session_id, supplementary_info):
                            st.session_state.workflow_session_id = session_id
                            st.session_state.workflow_status = WorkflowStatus.RUNNING
                            st.success(f"工作流已启动！会话ID: {session_id}")
                            st.rerun()
                        else:
                            st.error("启动工作流失败！")
            
            with col2:
                if st.button("⏸️ 暂停", disabled=st.session_state.workflow_status != WorkflowStatus.RUNNING):
                    if st.session_state.workflow_session_id:
                        if self.service.pause_workflow(st.session_state.workflow_session_id):
                            st.session_state.workflow_status = WorkflowStatus.PAUSED
                            st.info("工作流已暂停")
                            st.rerun()
            
            with col3:
                if st.button("❌ 取消", disabled=st.session_state.workflow_status not in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]):
                    if st.session_state.workflow_session_id:
                        if self.service.cancel_workflow(st.session_state.workflow_session_id):
                            st.session_state.workflow_status = WorkflowStatus.CANCELLED
                            st.warning("工作流已取消")
                            st.rerun()
        
        # 状态监控区域
        if st.session_state.workflow_session_id:
            self._render_status_monitor()
        
        # 会话管理区域
        self._render_session_manager()
    
    def _render_status_monitor(self):
        """渲染状态监控"""
        st.markdown("### 执行状态")
        
        session_id = st.session_state.workflow_session_id
        status_info = self.service.get_session_status(session_id)
        
        if status_info:
            # 状态指示器
            status = WorkflowStatus(status_info['status'])
            
            status_colors = {
                WorkflowStatus.IDLE: "🔵",
                WorkflowStatus.RUNNING: "🟢",
                WorkflowStatus.PAUSED: "🟡",
                WorkflowStatus.COMPLETED: "✅",
                WorkflowStatus.ERROR: "🔴",
                WorkflowStatus.CANCELLED: "⚫"
            }
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"**状态:** {status_colors.get(status, '❓')} {status.value}")
            
            with col2:
                if status_info.get('error_message'):
                    st.error(f"错误: {status_info['error_message']}")
            
            # 进度条
            if status_info.get('progress'):
                progress = status_info['progress']
                progress_value = progress['step'] / progress['total_steps']
                st.progress(progress_value)
                st.text(f"当前阶段: {progress['phase']} ({progress['step']}/{progress['total_steps']})")
            
            # 会话信息
            with st.expander("会话详情"):
                st.json({
                    "会话ID": status_info['session_id'],
                    "创建时间": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(status_info['created_at'])),
                    "更新时间": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(status_info['updated_at'])),
                    "用户需求": status_info['user_requirements']
                })
            
            # 结果显示
            if status == WorkflowStatus.COMPLETED:
                self._render_results(session_id)
            
            # 自动刷新
            if status == WorkflowStatus.RUNNING:
                time.sleep(2)
                st.rerun()
    
    def _render_results(self, session_id: str):
        """渲染工作流结果"""
        st.markdown("### 📊 执行结果")
        
        results = self.service.get_workflow_results(session_id)
        if results:
            # 结果摘要
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("策略计划数", len(results.get('strategy_plans', [])))
            with col2:
                st.metric("子目标数", len(results.get('sub_goals', [])))
            with col3:
                st.metric("执行命令数", len(results.get('executable_commands', [])))
            
            # 详细结果
            tabs = st.tabs(["用户画像", "策略计划", "子目标", "执行命令", "工作记忆"])
            
            with tabs[0]:
                if results.get('completion_requirement'):
                    st.json(results['completion_requirement'])
                else:
                    st.info("用户画像信息不可用")
            
            with tabs[1]:
                if results.get('strategy_plans'):
                    for i, plan in enumerate(results['strategy_plans']):
                        with st.expander(f"策略 {i+1}: {plan.get('description', '无描述')[:50]}..."):
                            st.json(plan)
                else:
                    st.info("暂无策略计划")
            
            with tabs[2]:
                if results.get('sub_goals'):
                    for i, goal in enumerate(results['sub_goals']):
                        with st.expander(f"目标 {i+1}: {goal.get('description', '无描述')[:50]}..."):
                            st.json(goal)
                else:
                    st.info("暂无子目标")
            
            with tabs[3]:
                if results.get('executable_commands'):
                    for i, cmd in enumerate(results['executable_commands']):
                        status_icon = "✅" if cmd.get('is_completed') else "⏳"
                        with st.expander(f"{status_icon} 命令 {i+1}: {cmd.get('tool', '未知工具')}"):
                            st.json(cmd)
                else:
                    st.info("暂无执行命令")
            
            with tabs[4]:
                if results.get('working_memory_data'):
                    st.json(results['working_memory_data'])
                else:
                    st.info("工作记忆为空")
    
    def _render_session_manager(self):
        """渲染会话管理器"""
        st.markdown("### 📋 会话管理")
        
        sessions = self.service.get_all_sessions()
        if sessions:
            for session in sessions[-5:]:  # 显示最近5个会话
                status = WorkflowStatus(session['status'])
                status_colors = {
                    WorkflowStatus.IDLE: "🔵",
                    WorkflowStatus.RUNNING: "🟢",
                    WorkflowStatus.PAUSED: "🟡",
                    WorkflowStatus.COMPLETED: "✅",
                    WorkflowStatus.ERROR: "🔴",
                    WorkflowStatus.CANCELLED: "⚫"
                }
                
                with st.expander(f"{status_colors.get(status, '❓')} {session['session_id']} - {status.value}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.text(f"需求: {session['user_requirements'][:100]}...")
                        st.text(f"创建时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session['created_at']))}")
                    
                    with col2:
                        if st.button("🗑️ 删除", key=f"delete_{session['session_id']}"):
                            if self.service.delete_session(session['session_id']):
                                st.success("会话已删除")
                                st.rerun()
                        
                        if status == WorkflowStatus.COMPLETED:
                            if st.button("📄 查看结果", key=f"view_{session['session_id']}"):
                                st.session_state.workflow_session_id = session['session_id']
                                st.rerun()
        else:
            st.info("暂无历史会话")