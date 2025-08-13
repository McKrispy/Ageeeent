# -*- coding: utf-8 -*-
"""
GUI与核心工作流的接口服务
提供工作流管理、会话管理、状态监控等功能
"""
import threading
import time
import uuid
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from Workflow_Entry import AgentWorkflow
    from Data.mcp_models import MCP, WorkingMemory
    from Data.cycle_history import CycleHistory
except ImportError as e:
    print(f"Warning: Cannot import workflow modules: {e}")
    # 创建模拟类用于测试
    class AgentWorkflow:
        def __init__(self, user_requirements, session_id):
            self.user_requirements = user_requirements
            self.session_id = session_id
            self.mcp = None
            self.working_memory = None
    
    class MCP:
        pass
    
    class WorkingMemory:
        pass
    
    class CycleHistory:
        pass

class WorkflowStatus(Enum):
    """工作流状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"

@dataclass
class SessionInfo:
    """会话信息"""
    session_id: str
    user_requirements: str
    status: WorkflowStatus
    created_at: float
    updated_at: float
    workflow: Optional[AgentWorkflow] = None
    thread: Optional[threading.Thread] = None
    error_message: Optional[str] = None
    progress: Dict[str, Any] = None

class WorkflowService:
    """工作流服务类，管理GUI与核心工作流的交互"""
    
    def __init__(self):
        self.sessions: Dict[str, SessionInfo] = {}
        self.status_callbacks: List[Callable] = []
        self._lock = threading.Lock()
    
    def create_session(self, user_requirements: str) -> str:
        """创建新的会话"""
        session_id = f"gui_session_{uuid.uuid4().hex[:8]}"
        
        with self._lock:
            session_info = SessionInfo(
                session_id=session_id,
                user_requirements=user_requirements,
                status=WorkflowStatus.IDLE,
                created_at=time.time(),
                updated_at=time.time(),
                progress={"phase": "初始化", "step": 0, "total_steps": 4}
            )
            self.sessions[session_id] = session_info
        
        return session_id
    
    def start_workflow(self, session_id: str, supplementary_info: str = "") -> bool:
        """启动工作流"""
        with self._lock:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            if session.status != WorkflowStatus.IDLE:
                return False
            
            try:
                # 创建工作流实例
                workflow = AgentWorkflow(
                    user_requirements=session.user_requirements,
                    session_id=session_id
                )
                
                session.workflow = workflow
                session.status = WorkflowStatus.RUNNING
                session.updated_at = time.time()
                
                # 在后台线程中运行工作流
                thread = threading.Thread(
                    target=self._run_workflow_background,
                    args=(session_id, supplementary_info),
                    daemon=True
                )
                session.thread = thread
                thread.start()
                
                self._notify_status_change(session_id)
                return True
                
            except Exception as e:
                session.status = WorkflowStatus.ERROR
                session.error_message = str(e)
                session.updated_at = time.time()
                self._notify_status_change(session_id)
                return False
    
    def _run_workflow_background(self, session_id: str, supplementary_info: str):
        """在后台运行工作流"""
        try:
            session = self.sessions[session_id]
            workflow = session.workflow
            
            # 模拟工作流的各个阶段
            self._update_progress(session_id, "用户输入处理", 1, 4)
            
            # 这里需要修改原始工作流以支持GUI模式
            # 暂时使用简化的执行流程
            
            # 阶段1：用户输入处理
            questionnaire = workflow.questionnaire_designer.process(workflow.mcp)
            
            # 使用提供的补充信息而不是控制台输入
            if supplementary_info:
                workflow.mcp = workflow.profile_drawer.process(workflow.mcp, supplementary_info)
            
            self._update_progress(session_id, "策略规划", 2, 4)
            
            # 阶段2：规划
            workflow.mcp = workflow.strategy_planner.process(workflow.mcp, workflow.strategies)
            workflow.mcp = workflow.task_planner.process(workflow.mcp, workflow.strategies)
            
            self._update_progress(session_id, "任务执行", 3, 4)
            
            # 阶段3：执行（简化版本）
            # 这里可以添加实际的执行逻辑
            
            self._update_progress(session_id, "完成", 4, 4)
            
            with self._lock:
                session.status = WorkflowStatus.COMPLETED
                session.updated_at = time.time()
            
            self._notify_status_change(session_id)
            
        except Exception as e:
            with self._lock:
                session = self.sessions[session_id]
                session.status = WorkflowStatus.ERROR
                session.error_message = str(e)
                session.updated_at = time.time()
            
            self._notify_status_change(session_id)
    
    def _update_progress(self, session_id: str, phase: str, step: int, total_steps: int):
        """更新进度"""
        with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id].progress = {
                    "phase": phase,
                    "step": step,
                    "total_steps": total_steps
                }
                self.sessions[session_id].updated_at = time.time()
        
        self._notify_status_change(session_id)
    
    def pause_workflow(self, session_id: str) -> bool:
        """暂停工作流"""
        with self._lock:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            if session.status == WorkflowStatus.RUNNING:
                session.status = WorkflowStatus.PAUSED
                session.updated_at = time.time()
                self._notify_status_change(session_id)
                return True
            
        return False
    
    def cancel_workflow(self, session_id: str) -> bool:
        """取消工作流"""
        with self._lock:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            if session.status in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED]:
                session.status = WorkflowStatus.CANCELLED
                session.updated_at = time.time()
                self._notify_status_change(session_id)
                return True
            
        return False
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话状态"""
        with self._lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            return {
                "session_id": session.session_id,
                "user_requirements": session.user_requirements,
                "status": session.status.value,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
                "error_message": session.error_message,
                "progress": session.progress
            }
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """获取所有会话状态"""
        with self._lock:
            return [self.get_session_status(sid) for sid in self.sessions.keys()]
    
    def get_workflow_results(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取工作流结果"""
        with self._lock:
            if session_id not in self.sessions:
                return None
            
            session = self.sessions[session_id]
            if not session.workflow or session.status != WorkflowStatus.COMPLETED:
                return None
            
            # 提取工作流结果
            mcp = session.workflow.mcp
            working_memory = session.workflow.working_memory
            
            return {
                "session_id": session_id,
                "user_requirements": mcp.user_requirements,
                "completion_requirement": mcp.completion_requirement.dict() if mcp.completion_requirement else None,
                "strategy_plans": [sp.dict() for sp in mcp.strategy_plans],
                "sub_goals": [sg.dict() for sg in mcp.sub_goals],
                "executable_commands": [ec.dict() for ec in mcp.executable_commands],
                "working_memory_data": working_memory.data,
                "cycle_count": mcp.global_cycle_count
            }
    
    def delete_session(self, session_id: str) -> bool:
        """删除会话"""
        with self._lock:
            if session_id in self.sessions:
                # 如果工作流正在运行，先取消它
                session = self.sessions[session_id]
                if session.status == WorkflowStatus.RUNNING:
                    session.status = WorkflowStatus.CANCELLED
                
                del self.sessions[session_id]
                return True
            
        return False
    
    def add_status_callback(self, callback: Callable):
        """添加状态变化回调"""
        self.status_callbacks.append(callback)
    
    def remove_status_callback(self, callback: Callable):
        """移除状态变化回调"""
        if callback in self.status_callbacks:
            self.status_callbacks.remove(callback)
    
    def _notify_status_change(self, session_id: str):
        """通知状态变化"""
        for callback in self.status_callbacks:
            try:
                callback(session_id)
            except Exception as e:
                print(f"Status callback error: {e}")


# 全局工作流服务实例
workflow_service = WorkflowService()