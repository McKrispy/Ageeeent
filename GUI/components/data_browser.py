# -*- coding: utf-8 -*-
"""
数据浏览器组件，用于浏览和管理工作流数据
"""
import streamlit as st
import json
import sys
import os
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Data.cycle_history import CycleHistory
from Interfaces.database_interface import RedisClient

class DataBrowser:
    """数据浏览器组件"""
    
    def __init__(self):
        self.redis_client = None
        self.cycle_history = CycleHistory()
    
    def render(self):
        """渲染数据浏览器"""
        st.subheader("📊 数据浏览器")
        
        # 数据源选择
        data_source = st.selectbox(
            "选择数据源：",
            ["Redis数据库", "历史记录", "本地文件"]
        )
        
        if data_source == "Redis数据库":
            self._render_redis_browser()
        elif data_source == "历史记录":
            self._render_history_browser()
        elif data_source == "本地文件":
            self._render_file_browser()
    
    def _render_redis_browser(self):
        """渲染Redis数据浏览器"""
        st.markdown("### Redis 数据库")
        
        # 连接控制
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button("🔌 连接 Redis"):
                try:
                    self.redis_client = RedisClient()
                    self.redis_client.connect()
                    st.success("Redis连接成功！")
                except Exception as e:
                    st.error(f"Redis连接失败: {e}")
        
        with col2:
            if st.button("❌ 断开连接"):
                if self.redis_client:
                    try:
                        self.redis_client.disconnect()
                        self.redis_client = None
                        st.success("已断开Redis连接")
                    except Exception as e:
                        st.error(f"断开连接失败: {e}")
        
        if self.redis_client:
            # 键搜索
            search_pattern = st.text_input("搜索键模式：", value="*", help="使用通配符*进行搜索")
            
            if st.button("🔍 搜索"):
                try:
                    keys = self.redis_client.search_keys(search_pattern)
                    if keys:
                        st.success(f"找到 {len(keys)} 个键")
                        
                        # 键列表
                        selected_key = st.selectbox("选择键：", keys)
                        
                        if selected_key:
                            # 获取键值
                            if st.button("📖 读取数据"):
                                try:
                                    data = self.redis_client.get(selected_key)
                                    st.json(data)
                                except Exception as e:
                                    st.error(f"读取数据失败: {e}")
                            
                            # 删除键
                            if st.button("🗑️ 删除键", key=f"delete_{selected_key}"):
                                if st.checkbox("确认删除", key=f"confirm_{selected_key}"):
                                    try:
                                        self.redis_client.delete(selected_key)
                                        st.success("键已删除")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"删除失败: {e}")
                    else:
                        st.info("未找到匹配的键")
                        
                except Exception as e:
                    st.error(f"搜索失败: {e}")
    
    def _render_history_browser(self):
        """渲染历史记录浏览器"""
        st.markdown("### 循环历史记录")
        
        # 获取历史记录
        history_data = self.cycle_history.get_all_history()
        
        if history_data:
            # 会话选择
            sessions = list(history_data.keys())
            selected_session = st.selectbox("选择会话：", sessions)
            
            if selected_session:
                session_data = history_data[selected_session]
                
                # 循环选择
                cycles = list(session_data.keys())
                selected_cycle = st.selectbox("选择循环：", cycles)
                
                if selected_cycle:
                    cycle_data = session_data[selected_cycle]
                    
                    # 数据展示
                    tabs = st.tabs(["基本信息", "策略计划", "子目标", "执行命令", "工作记忆"])
                    
                    with tabs[0]:
                        st.json({
                            "会话ID": selected_session,
                            "循环编号": selected_cycle,
                            "用户需求": cycle_data.get('user_requirements', ''),
                            "循环次数": cycle_data.get('global_cycle_count', 0)
                        })
                    
                    with tabs[1]:
                        strategy_plans = cycle_data.get('strategy_plans', [])
                        if strategy_plans:
                            for i, plan in enumerate(strategy_plans):
                                with st.expander(f"策略 {i+1}"):
                                    st.json(plan)
                        else:
                            st.info("无策略计划数据")
                    
                    with tabs[2]:
                        sub_goals = cycle_data.get('sub_goals', [])
                        if sub_goals:
                            for i, goal in enumerate(sub_goals):
                                with st.expander(f"目标 {i+1}"):
                                    st.json(goal)
                        else:
                            st.info("无子目标数据")
                    
                    with tabs[3]:
                        commands = cycle_data.get('executable_commands', [])
                        if commands:
                            for i, cmd in enumerate(commands):
                                status = "✅" if cmd.get('is_completed') else "⏳"
                                with st.expander(f"{status} 命令 {i+1}"):
                                    st.json(cmd)
                        else:
                            st.info("无执行命令数据")
                    
                    with tabs[4]:
                        memory_data = cycle_data.get('working_memory_data', {})
                        if memory_data:
                            st.json(memory_data)
                        else:
                            st.info("无工作记忆数据")
        else:
            st.info("暂无历史记录")
    
    def _render_file_browser(self):
        """渲染文件浏览器"""
        st.markdown("### 本地文件")
        
        # 文件上传
        uploaded_file = st.file_uploader(
            "上传JSON文件：",
            type=['json'],
            help="上传包含工作流数据的JSON文件"
        )
        
        if uploaded_file is not None:
            try:
                # 读取文件
                file_content = uploaded_file.read()
                data = json.loads(file_content)
                
                st.success("文件加载成功！")
                
                # 数据预览
                with st.expander("文件内容预览"):
                    st.json(data)
                
                # 数据分析
                if isinstance(data, dict):
                    st.markdown("#### 数据统计")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("顶级键数量", len(data.keys()))
                    
                    with col2:
                        total_items = sum(len(v) if isinstance(v, (list, dict)) else 1 for v in data.values())
                        st.metric("总项目数", total_items)
                    
                    with col3:
                        file_size = len(file_content)
                        st.metric("文件大小", f"{file_size} bytes")
                
            except json.JSONDecodeError as e:
                st.error(f"JSON格式错误: {e}")
            except Exception as e:
                st.error(f"文件处理错误: {e}")
        
        # 导出功能
        st.markdown("#### 数据导出")
        
        export_source = st.selectbox(
            "选择导出源：",
            ["当前会话数据", "Redis数据", "历史记录"]
        )
        
        if st.button("📤 导出数据"):
            try:
                export_data = {}
                
                if export_source == "当前会话数据":
                    # 从session_state导出数据
                    export_data = dict(st.session_state)
                elif export_source == "Redis数据":
                    if self.redis_client:
                        # 导出Redis中的所有数据
                        keys = self.redis_client.search_keys("*")
                        for key in keys:
                            export_data[key] = self.redis_client.get(key)
                    else:
                        st.error("请先连接Redis")
                        return
                elif export_source == "历史记录":
                    export_data = self.cycle_history.get_all_history()
                
                # 生成下载链接
                json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
                st.download_button(
                    label="💾 下载JSON文件",
                    data=json_str,
                    file_name=f"workflow_data_{export_source.replace(' ', '_')}.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"导出失败: {e}")